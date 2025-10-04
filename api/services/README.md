# Services

This directory contains business logic services for the mindmap system.

## Services

### `text_processing.py` - Text Processing Service
Extracts concepts and relationships from raw text using OpenAI GPT-4.

### `graph_service.py` - Graph Service
Manages knowledge graph structures using NetworkX.

Extracts concepts and relationships from raw text using OpenAI GPT-4.

**Key Features:**
- Input validation (100-50,000 characters)
- Concept extraction with GPT-4
- Relationship extraction between concepts
- Embedding generation with text-embedding-3-small (1536 dimensions)
- Cosine similarity calculation for semantic search
- Structured JSON output
- Configurable parameters (max concepts, min importance, min strength)

**Usage:**

```python
from api.services.text_processing import TextProcessingService

# Initialize service
service = TextProcessingService()

# Extract concepts
concepts = service.extract_concepts(
    text="Your text here...",
    max_concepts=10,
    min_importance=0.6
)

# Or use the full processing method (extracts concepts + relationships)
result = service.process_text(
    text="Your text here...",
    max_concepts=10,
    min_importance=0.5,
    min_strength=0.5,
    extract_rels=True
)

# Result contains:
# {
#   "concepts": [
#     {
#       "name": "Concept Name",
#       "description": "Brief description",
#       "importance": 0.95,
#       "source_text": "Relevant excerpt"
#     }
#   ],
#   "relationships": [
#     {
#       "source": "Concept A",
#       "target": "Concept B",
#       "type": "is-a",
#       "strength": 0.9,
#       "description": "Explanation of relationship"
#     }
#   ],
#   "metadata": {
#     "model": "gpt-4o-mini",
#     "concepts_found": 5,
#     "relationships_found": 3,
#     ...
#   }
# }

# Or extract relationships separately
relationships = service.extract_relationships(
    text="Your text...",
    concepts=concepts_list,
    min_strength=0.5
)

# Generate embeddings
embedding = service.generate_embedding("Your text here...")
# Returns: [0.1, 0.2, ...] (1536 dimensions)

# Batch generate embeddings
embeddings = service.generate_embeddings_batch(["Text 1", "Text 2", "Text 3"])

# Calculate similarity
similarity = TextProcessingService.cosine_similarity(embedding1, embedding2)
# Returns: 0.0 to 1.0 (higher = more similar)
```

**Validation Rules:**
- Minimum length: 100 characters
- Maximum length: 50,000 characters
- Text cannot be empty

**Environment Variables:**
- `OPENAI_API_KEY` - Required
- `OPENAI_MODEL` - Optional (default: gpt-4o-mini)
- `OPENAI_EMBEDDING_MODEL` - Optional (default: text-embedding-3-small)

## Testing

Run tests for text processing:

```bash
python api/tests/test_text_processing.py
```

This tests:
- ✓ Input validation
- ✓ Concept extraction
- ✓ Response format
- ✓ Full processing workflow

**Key Features:**
- In-memory graph storage
- NetworkX integration
- Graph traversal (BFS, DFS)
- Path finding (shortest path, all paths)
- Node expansion for UI interactions
- Subgraph extraction
- Distance queries (n-hop neighbors)
- Graph statistics

**Usage:**

```python
from api.services.graph_service import GraphService

# Initialize service
service = GraphService()

# Create graph
nodes = [
    {"id": "node_1", "label": "Python", "type": "language"},
    {"id": "node_2", "label": "Web Dev", "type": "field"}
]
edges = [
    {"source": "node_1", "target": "node_2", "relationship_type": "used-in"}
]

G = service.create_graph("my_graph", nodes, edges)

# Traversal operations
bfs_order = service.bfs_traversal("my_graph", "node_1")
dfs_order = service.dfs_traversal("my_graph", "node_1")

# Node expansion (for UI)
expansion = service.expand_node("my_graph", "node_1", depth=1)

# Query operations
neighbors = service.get_neighbors("my_graph", "node_1")
path = service.get_path("my_graph", "node_1", "node_2")
stats = service.get_graph_statistics("my_graph")
```

## LLM Service

### `llm_service.py`

Service for LLM-powered explanations and Q&A using GPT-4.

**Key Features:**
- Relationship explanations between nodes
- Question answering about the knowledge graph
- Graph summarization
- Context-aware responses using graph structure

**Usage:**

```python
from api.services.llm_service import LLMService

# Initialize service
service = LLMService()

# Generate relationship explanation
explanation = service.explain_relationship(
    source_node={"label": "Python", "description": "Programming language"},
    target_node={"label": "Data Science", "description": "Field of data analysis"},
    path=[source_node, intermediate_node, target_node],
    relationship_type="used-in"
)

# Answer questions about the graph
result = service.answer_question(
    question="What is Python used for?",
    graph_context={
        "nodes": [...],
        "edges": [...],
        "paths": [...]
    }
)

# Generate graph summary
summary = service.generate_summary(nodes, edges)
```

## Future Services

Coming in next phases:
- `tts_service.py` - Text-to-speech synthesis

