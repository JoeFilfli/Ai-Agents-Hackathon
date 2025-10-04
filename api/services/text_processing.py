"""
Text Processing Service for extracting concepts and relationships from raw text.

This service uses OpenAI GPT-4 to:
1. Extract key concepts from unstructured text
2. Generate descriptions for each concept
3. Assign importance scores to concepts
4. Identify relationships between concepts
5. Generate embeddings for semantic similarity

The extracted concepts become nodes and relationships become edges
in the knowledge graph.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env.local'
load_dotenv(env_path)

class TextProcessingService:
    """
    Service for processing text and extracting concepts and relationships.
    
    Uses OpenAI GPT-4 to analyze text and extract:
    - Key concepts with descriptions and importance scores
    - Relationships between concepts with types and strengths
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, embedding_model: Optional[str] = None):
        """
        Initialize the text processing service.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Model to use for text generation (uses env var or default if not provided)
            embedding_model: Model to use for embeddings (uses env var or default if not provided)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.embedding_model = embedding_model or os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def validate_text_input(self, text: str) -> tuple[bool, str]:
        """
        Validate text input meets requirements.
        
        Args:
            text: Input text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if text passes validation
            - error_message: Empty if valid, error description if invalid
        """
        # Check if text is empty or None
        if not text or not text.strip():
            return False, "Text cannot be empty"
        
        # Check minimum length
        if len(text) < 100:
            return False, f"Text must be at least 100 characters (got {len(text)})"
        
        # Check maximum length
        if len(text) > 50000:
            return False, f"Text cannot exceed 50,000 characters (got {len(text)})"
        
        return True, ""
    
    def extract_concepts(
        self, 
        text: str, 
        max_concepts: int = 10,
        min_importance: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Extract key concepts from text using GPT-4.
        
        This method analyzes the input text and identifies important concepts,
        generating descriptions and importance scores for each.
        
        Args:
            text: Input text to analyze
            max_concepts: Maximum number of concepts to extract
            min_importance: Minimum importance score (0-1) for concepts
            
        Returns:
            List of concept dictionaries with keys:
            - name: Concept name
            - description: Brief description
            - importance: Importance score (0-1)
            - source_text: Relevant excerpt from input
            
        Raises:
            ValueError: If text validation fails
            Exception: If API call fails
        """
        # Validate input
        is_valid, error_msg = self.validate_text_input(text)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Build the extraction prompt
        system_prompt = """You are an expert at analyzing text and extracting key concepts.
Your task is to identify the most important concepts, ideas, or topics from the given text.

For each concept:
- name: A clear, concise name (2-5 words)
- description: A brief explanation of what this concept means (1-2 sentences)
- importance: A score from 0.0 to 1.0 indicating how central this concept is to the text
- source_text: A relevant quote or excerpt from the original text that supports this concept

Return ONLY valid JSON in this exact format:
{
  "concepts": [
    {
      "name": "Concept Name",
      "description": "Brief description of the concept",
      "importance": 0.95,
      "source_text": "Relevant excerpt from the text"
    }
  ]
}

Be selective - focus on the most important and distinct concepts.
Avoid redundant or overlapping concepts."""

        user_prompt = f"""Analyze the following text and extract the {max_concepts} most important concepts.
Only include concepts with importance >= {min_importance}.

TEXT:
{text}

Remember: Return ONLY the JSON object, no additional text."""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=2000
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            # Sometimes the model adds markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            # Parse JSON
            result = json.loads(response_text)
            concepts = result.get("concepts", [])
            
            # Filter by minimum importance
            filtered_concepts = [
                c for c in concepts 
                if c.get("importance", 0) >= min_importance
            ]
            
            # Limit to max_concepts
            filtered_concepts = filtered_concepts[:max_concepts]
            
            return filtered_concepts
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse GPT-4 response as JSON: {e}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"Concept extraction failed: {e}")
    
    def extract_relationships(
        self,
        text: str,
        concepts: List[Dict[str, Any]],
        min_strength: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships between concepts using GPT-4.
        
        This method analyzes the concepts and input text to identify
        meaningful relationships between concepts.
        
        Args:
            text: Original input text
            concepts: List of extracted concepts
            min_strength: Minimum relationship strength (0-1)
            
        Returns:
            List of relationship dictionaries with keys:
            - source: Source concept name
            - target: Target concept name
            - type: Relationship type (e.g., 'is-a', 'part-of', 'related-to')
            - strength: Relationship strength (0-1)
            - description: Brief explanation of the relationship
            
        Raises:
            ValueError: If concepts list is empty
            Exception: If API call fails
        """
        if not concepts or len(concepts) == 0:
            raise ValueError("Concepts list cannot be empty")
        
        # Build concept list for prompt
        concept_names = [c.get('name', '') for c in concepts]
        concept_list = "\n".join([f"- {name}" for name in concept_names])
        
        # Build the extraction prompt
        system_prompt = """You are an expert at identifying relationships between concepts in text.
Your task is to analyze concepts extracted from text and identify meaningful relationships between them.

Common relationship types:
- "is-a": Hierarchical relationship (e.g., "Dog is-a Animal")
- "part-of": Component relationship (e.g., "Engine part-of Car")
- "related-to": General association
- "causes": Causal relationship
- "enables": One concept enables another
- "requires": Dependency relationship
- "uses": One concept uses another
- "implements": Implementation relationship
- "contrasts-with": Opposition or difference

For each relationship:
- source: The source concept name (must match exactly from the concept list)
- target: The target concept name (must match exactly from the concept list)
- type: One of the relationship types above
- strength: A score from 0.0 to 1.0 indicating relationship strength
- description: A brief explanation of why these concepts are related (1 sentence)

Return ONLY valid JSON in this exact format:
{
  "relationships": [
    {
      "source": "Concept A",
      "target": "Concept B",
      "type": "is-a",
      "strength": 0.9,
      "description": "Concept A is a type of Concept B"
    }
  ]
}

Only identify strong, meaningful relationships. Avoid weak or speculative connections."""

        user_prompt = f"""Analyze the following text and identify relationships between the extracted concepts.
Only include relationships with strength >= {min_strength}.

ORIGINAL TEXT:
{text}

EXTRACTED CONCEPTS:
{concept_list}

Identify the relationships between these concepts based on the text.
Remember: Return ONLY the JSON object, no additional text."""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=2000
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            # Parse JSON
            result = json.loads(response_text)
            relationships = result.get("relationships", [])
            
            # Filter by minimum strength
            filtered_relationships = [
                r for r in relationships
                if r.get("strength", 0) >= min_strength
            ]
            
            # Validate that source and target exist in concepts
            valid_relationships = []
            for rel in filtered_relationships:
                source = rel.get("source", "")
                target = rel.get("target", "")
                
                # Check if both source and target are in concept names
                if source in concept_names and target in concept_names:
                    valid_relationships.append(rel)
            
            return valid_relationships
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse GPT-4 response as JSON: {e}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"Relationship extraction failed: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a text string using OpenAI.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector (1536 dimensions)
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Call OpenAI embedding API
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            # Extract embedding from response
            embedding = response.data[0].embedding
            
            return embedding
            
        except Exception as e:
            raise Exception(f"Embedding generation failed: {e}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.
        
        This is more efficient than calling generate_embedding() multiple times.
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            List of embedding vectors, one for each input text
            
        Raises:
            Exception: If embedding generation fails
        """
        if not texts:
            return []
        
        try:
            # Call OpenAI embedding API with batch
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            # Extract embeddings from response
            embeddings = [item.embedding for item in response.data]
            
            return embeddings
            
        except Exception as e:
            raise Exception(f"Batch embedding generation failed: {e}")
    
    def add_embeddings_to_concepts(
        self, 
        concepts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add embeddings to a list of concepts.
        
        Generates embeddings based on concept name and description,
        then adds them to each concept dictionary.
        
        Args:
            concepts: List of concept dictionaries
            
        Returns:
            Updated list of concepts with embeddings added
        """
        if not concepts:
            return concepts
        
        try:
            # Build texts for embedding (combine name and description)
            texts = [
                f"{c.get('name', '')}: {c.get('description', '')}"
                for c in concepts
            ]
            
            # Generate embeddings in batch
            embeddings = self.generate_embeddings_batch(texts)
            
            # Add embeddings to concepts
            for i, concept in enumerate(concepts):
                concept['embedding'] = embeddings[i]
            
            return concepts
            
        except Exception as e:
            # Log error but don't fail - return concepts without embeddings
            print(f"Warning: Failed to add embeddings: {e}")
            return concepts
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1, where 1 is most similar)
        """
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        return float(similarity)
    
    def process_text(
        self,
        text: str,
        max_concepts: int = 10,
        min_importance: float = 0.5,
        min_strength: float = 0.5,
        extract_rels: bool = True,
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Process text and return extracted concepts and relationships with metadata.
        
        This is the main entry point for text processing. It validates input,
        extracts concepts, generates embeddings, extracts relationships,
        and returns a structured response.
        
        Args:
            text: Input text to process
            max_concepts: Maximum number of concepts to extract
            min_importance: Minimum importance score (0-1) for concepts
            min_strength: Minimum strength score (0-1) for relationships
            extract_rels: Whether to extract relationships (default: True)
            generate_embeddings: Whether to generate embeddings (default: True)
            
        Returns:
            Dictionary containing:
            - concepts: List of extracted concept dictionaries (with embeddings if enabled)
            - relationships: List of extracted relationship dictionaries (if extract_rels=True)
            - metadata: Processing metadata (model used, parameters, etc.)
            
        Raises:
            ValueError: If text validation fails
            Exception: If processing fails
        """
        # Extract concepts
        concepts = self.extract_concepts(text, max_concepts, min_importance)
        
        # Generate embeddings if requested
        if generate_embeddings and len(concepts) > 0:
            concepts = self.add_embeddings_to_concepts(concepts)
        
        # Build response
        response = {
            "concepts": concepts,
            "metadata": {
                "model": self.model,
                "embedding_model": self.embedding_model,
                "max_concepts": max_concepts,
                "min_importance": min_importance,
                "concepts_found": len(concepts),
                "input_length": len(text),
                "embeddings_generated": generate_embeddings
            }
        }
        
        # Extract relationships if requested and concepts exist
        if extract_rels and len(concepts) > 0:
            relationships = self.extract_relationships(text, concepts, min_strength)
            response["relationships"] = relationships
            response["metadata"]["relationships_found"] = len(relationships)
            response["metadata"]["min_strength"] = min_strength
        else:
            response["relationships"] = []
            response["metadata"]["relationships_found"] = 0
        
        return response


# Convenience function for quick usage
def extract_concepts_from_text(
    text: str,
    max_concepts: int = 10,
    min_importance: float = 0.5,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to extract concepts from text.
    
    Args:
        text: Input text to analyze
        max_concepts: Maximum number of concepts to extract
        min_importance: Minimum importance score (0-1)
        api_key: OpenAI API key (uses env var if not provided)
        
    Returns:
        List of concept dictionaries
    """
    service = TextProcessingService(api_key=api_key)
    return service.extract_concepts(text, max_concepts, min_importance)

