"""
Text Processing Service for extracting concepts and relationships from raw text.

This service uses OpenAI GPT-4 to:
1. Extract key concepts from unstructured text (unlimited - LLM decides)
2. Generate descriptions for each concept
3. Assign importance scores to concepts
4. Identify relationships between concepts
5. Generate embeddings for semantic similarity
6. Chunk long texts for comprehensive coverage
7. Merge duplicate concepts using semantic embeddings

The extracted concepts become nodes and relationships become edges
in the knowledge graph.
"""

import os
import json
import re
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path
from textwrap import shorten

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
    
    @staticmethod
    def _clean_json_block(s: str) -> str:
        """
        Clean JSON response from LLM (remove markdown code blocks).
        
        Args:
            s: Raw string response from LLM
            
        Returns:
            Cleaned JSON string
        """
        s = s.strip()
        # Remove ```json and ``` wrappers
        if s.startswith("```json"):
            s = s[len("```json"):].strip()
            if s.endswith("```"):
                s = s[:-3].strip()
        elif s.startswith("```"):
            s = s[3:].strip()
            if s.endswith("```"):
                s = s[:-3].strip()
        return s
    
    @staticmethod
    def _chunk(text: str, target: int = 1800, overlap: int = 200) -> List[str]:
        """
        Split long text into overlapping chunks for comprehensive coverage.
        
        Splits at sentence boundaries to maintain context.
        
        Args:
            text: Input text to chunk
            target: Target chunk size in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks (only chunks > 200 chars)
        """
        chunks, start = [], 0
        n = len(text)
        
        while start < n:
            end = min(n, start + target)
            # Try to cut at sentence boundary
            cut = text.rfind('.', start, end)
            if cut == -1 or cut <= start + 200:
                cut = end
            chunks.append(text[start:cut].strip())
            start = max(cut - overlap, cut)
        
        # Only return substantial chunks
        return [c for c in chunks if len(c) > 200]
    
    @staticmethod
    def _batch(items: List[Any], size: int = 60) -> List[List[Any]]:
        """
        Split a list into smaller batches.
        
        Args:
            items: List of items to batch
            size: Size of each batch
            
        Yields:
            Batches of items
        """
        for i in range(0, len(items), size):
            yield items[i:i+size]
    
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
        min_importance: float = 0.0,  # No filtering by default - LLM decides
    ) -> List[Dict[str, Any]]:
        """
        Extract ALL salient concepts from text using GPT-4.
        
        No artificial limit on count. We rely on chunking for coverage.
        The LLM returns as many concepts as it deems meaningful.
        
        Args:
            text: Input text to analyze
            min_importance: Minimum importance score (0-1) for concepts
            
        Returns:
            List of concept dictionaries with keys:
            - name: Concept name (2-5 words, canonical)
            - description: Brief description (1-2 sentences)
            - importance: Importance score (0-1)
            - source_text: Evidence quote from text
            - level: Hierarchy level (1=core, 2=subtopics, 3=details)
            - parent: Parent concept name if level>1, else null
            
        Raises:
            ValueError: If text validation fails
            Exception: If API call fails
        """
        # Validate input
        is_valid, error_msg = self.validate_text_input(text)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Build the extraction prompt
        system_prompt = """You are an expert at concept mining.
Return ALL salient, distinct concepts the text supports (no arbitrary limits).

For each concept return:
- name: 2–5 words, canonical
- description: 1–2 sentences, faithful to the text
- importance: 0.0–1.0 (how central to the text)
- source_text: short evidence quote from the text
- level: 1, 2, or 3  (1=core themes, 2=subtopics of a level-1, 3=details/examples)
- parent: the parent concept's exact name if level>1, else null

Return ONLY valid JSON:
{"concepts":[{...},{...}]}"""

        user_prompt = f"""Analyze the text and return ALL meaningful concepts,
including core themes (level 1), subtopics (level 2), and details/examples (level 3).
Be inclusive; avoid merging distinct ideas.

TEXT:
{text}

Important:
- Use {{ "concepts": [...] }} EXACT JSON.
- If two concepts are related but distinct, keep both.
"""

        try:
            # Call OpenAI API with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},  # Enforce JSON output
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent extraction
                max_tokens=8000  # Allow comprehensive extraction
            )
            
            # Parse response
            raw = response.choices[0].message.content
            cleaned = self._clean_json_block(raw)
            data = json.loads(cleaned)
            concepts = data.get("concepts", [])
            
            # Validate concepts is a list
            if not isinstance(concepts, list):
                raise Exception(f"Expected 'concepts' to be a list, got {type(concepts)}")
            
            # Filter out invalid concepts and ensure required fields
            valid_concepts = []
            for c in concepts:
                if not isinstance(c, dict):
                    continue
                # Ensure required fields exist with defaults
                if not c.get("name"):
                    continue
                c.setdefault("description", "")
                c.setdefault("importance", 0.5)
                c.setdefault("source_text", "")
                c.setdefault("level", 1)
                c.setdefault("parent", None)
                
                # Only filter by min_importance if specified
                if min_importance > 0 and c.get("importance", 0) < min_importance:
                    continue
                    
                valid_concepts.append(c)
            
            return valid_concepts
            
        except json.JSONDecodeError as e:
            # Safely truncate response without breaking JSON strings in error message
            safe_preview = raw[:500].replace('"', "'").replace('\n', ' ') if 'raw' in locals() else 'N/A'
            error_msg = f"Failed to parse LLM JSON response: {str(e)}. Preview: {safe_preview}"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Concept extraction failed: {str(e)}")
    
    def _merge_dupes_by_embedding(
        self, 
        concepts: List[Dict[str, Any]], 
        sim_thresh: float = 0.87
    ) -> List[Dict[str, Any]]:
        """
        Merge duplicate concepts using semantic similarity of embeddings.
        
        Concepts with similarity >= sim_thresh are merged into one.
        The highest-importance concept becomes the canonical version.
        
        Args:
            concepts: List of concept dictionaries
            sim_thresh: Similarity threshold for merging (0-1)
            
        Returns:
            Deduplicated list of concepts with aliases for merged items
        """
        if not concepts:
            return concepts
        
        # Ensure all concepts have embeddings
        need_embed = any('embedding' not in c for c in concepts)
        if need_embed:
            # Generate embeddings for concepts missing them
            texts = [f"{c.get('name','')}: {c.get('description','')}" for c in concepts]
            embeds = self.generate_embeddings_batch(texts)
            for i, c in enumerate(concepts):
                c['embedding'] = embeds[i]
        
        # Merge duplicates by similarity
        out, used = [], [False] * len(concepts)
        
        for i, c in enumerate(concepts):
            if used[i]:
                continue
            
            # Start a new group with this concept
            group = [c]
            used[i] = True
            
            # Find all similar concepts
            for j in range(i + 1, len(concepts)):
                if used[j]:
                    continue
                
                if 'embedding' in c and 'embedding' in concepts[j]:
                    sim = self.cosine_similarity(c['embedding'], concepts[j]['embedding'])
                    if sim >= sim_thresh:
                        group.append(concepts[j])
                        used[j] = True
            
            # Keep highest-importance as canonical
            best = max(group, key=lambda g: g.get('importance', 0))
            
            # Add aliases for merged concepts
            aliases = list({g.get('name') for g in group if g is not best})
            if aliases:
                best['aliases'] = aliases
            
            out.append(best)
        
        return out
    
    def extract_relationships_all(
        self,
        text: str,
        concepts: List[Dict[str, Any]],
        min_strength: float = 0.0,  # Keep all edges by default
        batch_size: int = 60  # Batch for token safety, not a cap on total
    ) -> List[Dict[str, Any]]:
        """
        Extract ALL meaningful relationships across concepts.
        
        Batches concepts only for token safety, not as a limit.
        Returns all edges the LLM can justify from the text.
        
        Args:
            text: Original input text
            concepts: List of extracted concepts
            min_strength: Minimum relationship strength (0-1)
            batch_size: Size of concept batches (for token safety)
            
        Returns:
            List of relationship dictionaries with keys:
            - source: Source concept name
            - target: Target concept name
            - type: Relationship type
            - strength: Relationship strength (0-1)
            - description: Brief explanation
            
        Raises:
            ValueError: If concepts list is empty
        """
        if not concepts:
            return []
        
        # Extract all concept names
        all_names = [c.get('name', '') for c in concepts if c.get('name')]
        relationships: List[Dict[str, Any]] = []
        
        # Build system prompt for relationship extraction
        system_prompt = """You identify relationships among a provided list of concepts.
Return ALL meaningful edges you can justify from the text.

Allowed types:
- "is-a", "part-of", "related-to", "causes", "enables", "requires", "uses", "implements", "contrasts-with"

For each relationship:
- source: exact concept name
- target: exact concept name
- type: one of the above
- strength: 0.0–1.0 (confidence)
- description: one sentence rationale with evidence

Return ONLY JSON:
{"relationships":[{...},{...}]}"""
        
        # Create context of all concept names
        names_context = "\n".join(f"- {n}" for n in all_names)
        
        # Process in batches (for token safety, not limiting output)
        for batch in self._batch(all_names, size=batch_size):
            user_prompt = f"""TEXT:
{text}

ALL CONCEPTS (context):
{names_context}

BATCH FOCUS (propose edges that involve AT LEAST ONE of these):
{', '.join(batch)}

Return JSON with ALL edges you can justify. No arbitrary limits."""
            
            try:
                # Call OpenAI API with JSON mode
                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format={"type": "json_object"},  # Enforce JSON output
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,  # Low temperature for consistent extraction
                    max_tokens=8000
                )
                
                # Parse response
                raw = response.choices[0].message.content
                cleaned = self._clean_json_block(raw)
                data = json.loads(cleaned)
                rels = data.get("relationships", [])
                
                # Ensure rels is a list
                if not isinstance(rels, list):
                    print(f"Warning: relationships is not a list, got {type(rels)}")
                    rels = []
                
                # Filter by min_strength if requested
                if min_strength > 0:
                    rels = [r for r in rels if isinstance(r, dict) and r.get("strength", 0) >= min_strength]
                
                # Sanity check: only keep edges whose endpoints actually exist
                keep = []
                sset = set(all_names)
                for r in rels:
                    if not isinstance(r, dict):
                        continue
                    s, t = r.get("source", ""), r.get("target", "")
                    if s in sset and t in sset and s != t:
                        keep.append(r)
                
                relationships.extend(keep)
                
            except json.JSONDecodeError as e:
                # Safely log JSON errors without breaking
                safe_preview = raw[:300].replace('"', "'") if 'raw' in locals() else 'N/A'
                print(f"Relationship batch JSON parse failed: {e}. Preview: {safe_preview}")
            except Exception as e:
                print(f"Relationship batch failed: {str(e)}")
        
        # Deduplicate edges by (source, target, type)
        seen = set()
        unique = []
        for r in relationships:
            key = (r.get('source'), r.get('target'), r.get('type'))
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        return unique
    
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
        min_importance: float = 0.0,  # LLM decides; keep everything by default
        min_strength: float = 0.0,    # Keep all edges by default
        extract_rels: bool = True,
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Process text with NO artificial caps - unlimited concepts and edges.
        
        Full pipeline:
        1. Chunk text for comprehensive coverage
        2. Extract ALL concepts per chunk (LLM decides count)
        3. Embed and merge duplicates semantically
        4. Extract ALL relationships across concepts (batched for token safety)
        5. Build hierarchy and ensure connectivity
        
        Args:
            text: Input text to process
            min_importance: Minimum importance score (0-1) for concepts
            min_strength: Minimum strength score (0-1) for relationships
            extract_rels: Whether to extract relationships (default: True)
            generate_embeddings: Whether to generate embeddings (default: True)
            
        Returns:
            Dictionary containing:
            - concepts: List of extracted concept dictionaries (with tier/level info)
            - relationships: List of extracted relationship dictionaries
            - metadata: Processing metadata (counts, chunk info, etc.)
            
        Raises:
            ValueError: If text validation fails
            Exception: If processing fails
        """
        # Validate input
        is_valid, error_msg = self.validate_text_input(text)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Step 1: Chunk for comprehensive recall
        # Optimization: Skip chunking for texts < 3000 chars (single LLM call is faster)
        if len(text) < 3000:
            chunks = [text]
        else:
            chunks = self._chunk(text)
            if not chunks:
                chunks = [text]
        
        print(f"Processing {len(chunks)} chunk(s) for {len(text)} characters")
        
        # Step 2: Extract ALL concepts per chunk (no limits)
        concepts_all: List[Dict[str, Any]] = []
        for i, chunk in enumerate(chunks):
            print(f"  Extracting concepts from chunk {i+1}/{len(chunks)}...")
            chunk_concepts = self.extract_concepts(chunk, min_importance=min_importance)
            print(f"    Found {len(chunk_concepts)} concepts")
            concepts_all.extend(chunk_concepts)
        
        # Step 3: Embed & merge duplicates semantically
        print(f"  Total concepts before deduplication: {len(concepts_all)}")
        if generate_embeddings and concepts_all:
            print(f"  Generating embeddings and merging duplicates...")
            # _merge_dupes_by_embedding will generate embeddings if missing
            concepts_all = self._merge_dupes_by_embedding(concepts_all, sim_thresh=0.87)
            print(f"  Concepts after deduplication: {len(concepts_all)}")
        else:
            # Minimal fallback: dedupe by exact name match
            seen_names = set()
            unique = []
            for c in concepts_all:
                n = c.get('name', '')
                if n and n not in seen_names:
                    seen_names.add(n)
                    unique.append(c)
            concepts_all = unique
        
        # Step 4: Extract ALL relationships across concepts (batched for token safety)
        relationships: List[Dict[str, Any]] = []
        if extract_rels and concepts_all:
            print(f"  Extracting relationships for {len(concepts_all)} concepts...")
            relationships = self.extract_relationships_all(
                text=text,
                concepts=concepts_all,
                min_strength=min_strength,
            )
            print(f"  Found {len(relationships)} relationships")
        
        # Step 5: Build hierarchy and ensure connectivity
        # This ensures a single connected graph with proper tiers
        if concepts_all:
            concepts_all, relationships = self.build_hierarchy_and_connectivity(
                concepts_all,
                relationships
            )
        
        # Step 6: Gather metadata
        tier1_count = sum(1 for c in concepts_all if c.get('tier') == 1)
        tier2_count = sum(1 for c in concepts_all if c.get('tier') == 2)
        inferred_rels = sum(1 for r in relationships if r.get('inferred', False))
        
        # Build response
        response = {
            "concepts": concepts_all,
            "relationships": relationships,
            "metadata": {
                "model": self.model,
                "embedding_model": self.embedding_model,
                "concepts_found": len(concepts_all),
                "relationships_found": len(relationships),
                "explicit_relationships": len(relationships) - inferred_rels,
                "inferred_relationships": inferred_rels,
                "tier1_concepts": tier1_count,
                "tier2_concepts": tier2_count,
                "input_length": len(text),
                "embeddings_generated": bool(generate_embeddings),
                "hierarchy_enabled": True,
                "connectivity_ensured": True,
                "chunk_count": len(chunks)
            }
        }
        
        return response


# Convenience function for quick usage
def extract_concepts_from_text(
    text: str,
    min_importance: float = 0.0,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to extract concepts from text.
    
    Extracts ALL salient concepts (no artificial limit).
    
    Args:
        text: Input text to analyze
        min_importance: Minimum importance score (0-1)
        api_key: OpenAI API key (uses env var if not provided)
        
    Returns:
        List of concept dictionaries
    """
    service = TextProcessingService(api_key=api_key)
    return service.extract_concepts(text, min_importance)

