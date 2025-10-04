# FastAPI Backend

This is the FastAPI backend for the Interactive Mindmap System.

## API Endpoints

### Health Check
```
GET /api/py/health
```
Returns service status and version.

### Text Processing
```
POST /api/py/text/process
```
Process raw text and extract a knowledge graph.

**Request Body:**
```json
{
  "text": "Your text here (100-50,000 chars)",
  "max_concepts": 10,
  "min_importance": 0.5,
  "min_strength": 0.5,
  "extract_relationships": true,
  "generate_embeddings": true
}
```

**Response:**
```json
{
  "graph_id": "graph_abc123",
  "nodes": [
    {
      "id": "node_0",
      "label": "Concept Name",
      "description": "Brief description",
      "source_text": "Relevant excerpt",
      "confidence": 0.95,
      "embedding": [0.1, 0.2, ...],
      "metadata": {...},
      "has_children": false
    }
  ],
  "edges": [
    {
      "id": "edge_0",
      "source": "node_0",
      "target": "node_1",
      "relationship_type": "is-a",
      "weight": 0.9,
      "confidence": 0.9,
      "metadata": {"description": "..."}
    }
  ],
  "metadata": {
    "model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
    "node_count": 5,
    "edge_count": 3,
    ...
  }
}
```

### Graph Operations

#### Retrieve Graph
```
GET /api/py/graph/{graph_id}
```
Retrieve a previously generated graph by its ID. Returns all nodes, edges, and graph statistics.

**Response:**
```json
{
  "graph_id": "graph_abc123",
  "nodes": [...],
  "edges": [...],
  "statistics": {
    "node_count": 5,
    "edge_count": 3,
    "density": 0.6,
    "avg_degree": 1.2
  }
}
```

#### Expand Node
```
POST /api/py/graph/{graph_id}/expand/{node_id}
```
Expand a node to get its local neighborhood subgraph. Useful for interactive UI exploration.

**Request Body:**
```json
{
  "depth": 1
}
```

**Response:**
```json
{
  "center_node": "node_0",
  "nodes": [...],
  "edges": [...],
  "depth": 1
}
```

#### Get Relationship Paths
```
POST /api/py/graph/{graph_id}/relationships/{node_id}
```
Get relationship paths and connections from a specific node (up to 3 hops).

**Response:**
```json
{
  "node_id": "node_0",
  "paths": [
    {
      "target": "node_2",
      "path": ["node_0", "node_1", "node_2"],
      "length": 2,
      "nodes": [...]
    }
  ],
  "neighbors": [...],
  "statistics": {
    "total_paths": 5,
    "direct_neighbors": 2,
    "reachable_nodes": 4,
    "avg_path_length": 1.5
  }
}
```

## Running the Server

### Development Mode
```bash
uvicorn api.index:app --reload --port 8000
```

The API will be available at:
- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/api/py/docs
- OpenAPI schema: http://127.0.0.1:8000/api/py/openapi.json

### Production Mode
```bash
uvicorn api.index:app --host 0.0.0.0 --port 8000
```

## Testing

Run all backend tests:
```bash
# Setup tests
python api/tests/test_setup.py

# Model tests
python api/tests/test_models.py

# Text processing tests
python api/tests/test_text_processing.py

# Relationship tests
python api/tests/test_relationships.py

# Embedding tests
python api/tests/test_embeddings.py

# API endpoint tests
python api/tests/test_api.py

# Graph service tests
python api/tests/test_graph_service.py

# Graph API endpoint tests
python api/tests/test_graph_api.py
```

## Interactive API Testing

1. Start the server:
   ```bash
   uvicorn api.index:app --reload --port 8000
   ```

2. Open the interactive docs:
   ```
   http://127.0.0.1:8000/api/py/docs
   ```

3. Try the endpoints using the "Try it out" button

## Using curl

Test the health endpoint:
```bash
curl http://127.0.0.1:8000/api/py/health
```

Test text processing:
```bash
curl -X POST http://127.0.0.1:8000/api/py/text/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python is a high-level programming language. It is widely used for web development, data science, and automation. Python has a simple and readable syntax that makes it beginner-friendly. Popular frameworks like Django and Flask are built with Python.",
    "max_concepts": 5,
    "min_importance": 0.5
  }'
```

Retrieve a graph:
```bash
curl http://127.0.0.1:8000/api/py/graph/graph_abc123
```

Expand a node:
```bash
curl -X POST http://127.0.0.1:8000/api/py/graph/graph_abc123/expand/node_0 \
  -H "Content-Type: application/json" \
  -d '{"depth": 1}'
```

Get relationship paths:
```bash
curl -X POST http://127.0.0.1:8000/api/py/graph/graph_abc123/relationships/node_0
```

## Directory Structure

```
api/
├── models/         # Pydantic data models
├── services/       # Business logic
├── tests/          # Test suite
├── index.py        # Main FastAPI app
└── README.md       # This file
```

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `OPENAI_MODEL` - Model for text generation (default: gpt-4o-mini)
- `OPENAI_EMBEDDING_MODEL` - Model for embeddings (default: text-embedding-3-small)

## Error Handling

The API returns structured error responses:

**400 Bad Request** - Invalid input
```json
{
  "detail": {
    "error": {
      "code": "INVALID_INPUT",
      "message": "Text must be at least 100 characters",
      "retry": false
    }
  }
}
```

**500 Internal Server Error** - Processing failed
```json
{
  "detail": {
    "error": {
      "code": "PROCESSING_FAILED",
      "message": "Failed to process text: ...",
      "retry": true
    }
  }
}
```

