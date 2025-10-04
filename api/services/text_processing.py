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
                max_tokens=8000  # Increased to max for comprehensive extraction
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
                max_tokens=8000  # Increased to max for comprehensive relationship extraction
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
    
    def build_hierarchy_and_connectivity(
        self,
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Build hierarchical structure and ensure FULL graph connectivity.
        
        This lightweight pass GUARANTEES:
        1. ONE fully connected graph (no isolated islands)
        2. Tier levels (1=core concepts, 2=details)
        3. Semantic relationships based on embeddings when needed
        
        Args:
            concepts: List of concept dictionaries
            relationships: List of relationship dictionaries
            
        Returns:
            Tuple of (enhanced_concepts, enhanced_relationships)
        """
        if not concepts:
            return concepts, relationships
        
        if len(concepts) == 1:
            # Single concept - mark as tier 1
            concepts[0]['tier'] = 1
            concepts[0]['connections'] = 0
            return concepts, relationships
        
        # Step 1: Build adjacency structure for connectivity analysis
        concept_names = {c['name']: i for i, c in enumerate(concepts)}
        concept_connections = {c['name']: 0 for c in concepts}
        adjacency = {c['name']: set() for c in concepts}
        
        # Build adjacency list (undirected)
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            if source in concept_names and target in concept_names:
                adjacency[source].add(target)
                adjacency[target].add(source)
                concept_connections[source] += 1
                concept_connections[target] += 1
        
        # Step 2: Find connected components using BFS
        def find_connected_components():
            visited = set()
            components = []
            
            for concept in concepts:
                name = concept['name']
                if name not in visited:
                    # BFS to find component
                    component = set()
                    queue = [name]
                    
                    while queue:
                        current = queue.pop(0)
                        if current not in visited:
                            visited.add(current)
                            component.add(current)
                            # Add unvisited neighbors
                            for neighbor in adjacency[current]:
                                if neighbor not in visited:
                                    queue.append(neighbor)
                    
                    components.append(component)
            
            return components
        
        # Step 3: Connect all components into ONE graph
        new_relationships = []
        components = find_connected_components()
        
        print(f"Found {len(components)} connected component(s)")
        
        # If multiple components exist, connect them
        if len(components) > 1:
            # Strategy: Connect each component to the main (largest) component
            main_component = max(components, key=len)
            
            for component in components:
                if component == main_component:
                    continue
                
                # Find best connection between this component and main component
                best_source = None
                best_target = None
                best_similarity = -1
                
                for source_name in component:
                    source_concept = next(c for c in concepts if c['name'] == source_name)
                    
                    if 'embedding' in source_concept:
                        for target_name in main_component:
                            target_concept = next(c for c in concepts if c['name'] == target_name)
                            
                            if 'embedding' in target_concept:
                                similarity = self.cosine_similarity(
                                    source_concept['embedding'],
                                    target_concept['embedding']
                                )
                                if similarity > best_similarity:
                                    best_similarity = similarity
                                    best_source = source_name
                                    best_target = target_name
                
                # Create bridge connection
                if best_source and best_target:
                    new_relationships.append({
                        'source': best_source,
                        'target': best_target,
                        'type': 'related-to',
                        'strength': max(0.5, float(best_similarity * 0.8)),
                        'description': f'Bridge connection (component merge)',
                        'inferred': True
                    })
                    # Update adjacency
                    adjacency[best_source].add(best_target)
                    adjacency[best_target].add(best_source)
                else:
                    # Fallback: connect highest importance from each
                    source_concept = max(
                        [c for c in concepts if c['name'] in component],
                        key=lambda x: x.get('importance', 0)
                    )
                    target_concept = max(
                        [c for c in concepts if c['name'] in main_component],
                        key=lambda x: x.get('importance', 0)
                    )
                    new_relationships.append({
                        'source': source_concept['name'],
                        'target': target_concept['name'],
                        'type': 'related-to',
                        'strength': 0.6,
                        'description': 'Bridge connection (fallback)',
                        'inferred': True
                    })
        
        # Step 4: Ensure isolated nodes are connected
        # Re-check connectivity after adding bridges
        for rel in new_relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            if source in concept_connections:
                concept_connections[source] += 1
            if target in concept_connections:
                concept_connections[target] += 1
        
        # Find any remaining isolated nodes
        isolated = [c for c in concepts if concept_connections[c['name']] == 0]
        
        for isolated_concept in isolated:
            # Connect to nearest neighbor by embedding similarity
            if 'embedding' in isolated_concept:
                best_match = None
                best_similarity = -1
                
                for concept in concepts:
                    if concept['name'] != isolated_concept['name'] and 'embedding' in concept:
                        similarity = self.cosine_similarity(
                            isolated_concept['embedding'],
                            concept['embedding']
                        )
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = concept
                
                if best_match:
                    new_relationships.append({
                        'source': isolated_concept['name'],
                        'target': best_match['name'],
                        'type': 'related-to',
                        'strength': max(0.5, float(best_similarity * 0.8)),
                        'description': 'Connectivity link',
                        'inferred': True
                    })
                    concept_connections[isolated_concept['name']] += 1
                    concept_connections[best_match['name']] += 1
        
        # Step 5: Assign tiers based on importance + connectivity
        for concept in concepts:
            importance = concept.get('importance', 0.5)
            connections = concept_connections[concept['name']]
            
            # Core concepts: high importance (>0.7) OR well-connected (>=2 connections)
            if importance > 0.7 or connections >= 2:
                concept['tier'] = 1
            else:
                concept['tier'] = 2
            
            # Store connection count
            concept['connections'] = connections
        
        # Step 6: Ensure at least one tier-1 concept exists
        tier1_concepts = [c for c in concepts if c.get('tier') == 1]
        if not tier1_concepts and concepts:
            # Promote the highest importance concept to tier 1
            highest = max(concepts, key=lambda x: x.get('importance', 0))
            highest['tier'] = 1
        
        # Combine all relationships
        enhanced_relationships = relationships + new_relationships
        
        # Verify connectivity
        final_components = find_connected_components()
        print(f"Final graph has {len(final_components)} connected component(s) - Target: 1")
        print(f"Added {len(new_relationships)} inferred relationships for connectivity")
        
        return concepts, enhanced_relationships
    
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
        builds hierarchy, and ensures connectivity.
        
        Args:
            text: Input text to process
            max_concepts: Maximum number of concepts to extract
            min_importance: Minimum importance score (0-1) for concepts
            min_strength: Minimum strength score (0-1) for relationships
            extract_rels: Whether to extract relationships (default: True)
            generate_embeddings: Whether to generate embeddings (default: True)
            
        Returns:
            Dictionary containing:
            - concepts: List of extracted concept dictionaries (with tier info)
            - relationships: List of extracted relationship dictionaries
            - metadata: Processing metadata (model used, parameters, hierarchy info, etc.)
            
        Raises:
            ValueError: If text validation fails
            Exception: If processing fails
        """
        # Step 1: Extract concepts
        concepts = self.extract_concepts(text, max_concepts, min_importance)
        
        # Step 2: Generate embeddings if requested
        if generate_embeddings and len(concepts) > 0:
            concepts = self.add_embeddings_to_concepts(concepts)
        
        # Step 3: Extract relationships if requested and concepts exist
        relationships = []
        if extract_rels and len(concepts) > 0:
            relationships = self.extract_relationships(text, concepts, min_strength)
        
        # Step 4: Build hierarchy and ensure connectivity
        # This creates a consolidated, tiered graph with no islands
        if len(concepts) > 0:
            concepts, relationships = self.build_hierarchy_and_connectivity(
                concepts, 
                relationships
            )
        
        # Step 5: Count tier distribution
        tier1_count = sum(1 for c in concepts if c.get('tier') == 1)
        tier2_count = sum(1 for c in concepts if c.get('tier') == 2)
        inferred_rels = sum(1 for r in relationships if r.get('inferred', False))
        
        # Build response
        response = {
            "concepts": concepts,
            "relationships": relationships,
            "metadata": {
                "model": self.model,
                "embedding_model": self.embedding_model,
                "max_concepts": max_concepts,
                "min_importance": min_importance,
                "min_strength": min_strength,
                "concepts_found": len(concepts),
                "relationships_found": len(relationships),
                "tier1_concepts": tier1_count,
                "tier2_concepts": tier2_count,
                "inferred_relationships": inferred_rels,
                "explicit_relationships": len(relationships) - inferred_rels,
                "input_length": len(text),
                "embeddings_generated": generate_embeddings,
                "hierarchy_enabled": True,
                "connectivity_ensured": True
            }
        }
        
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

