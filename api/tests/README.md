# Test Suite

This directory contains all test files for the API backend.

## Test Files

### `test_setup.py`
Tests the project setup and dependencies.

**What it tests:**
- ✓ Package imports (FastAPI, OpenAI, NetworkX, Pydantic)
- ✓ OpenAI API connection with configured model
- ✓ NetworkX graph functionality

**Run:**
```bash
python api/tests/test_setup.py
```

### `test_models.py`
Tests the Pydantic data models.

**What it tests:**
- ✓ Model imports
- ✓ Node creation and properties
- ✓ Edge creation and relationships
- ✓ Graph creation and helper methods
- ✓ JSON serialization
- ✓ Pydantic validation

**Run:**
```bash
python api/tests/test_models.py
```

### `test_text_processing.py`
Tests the text processing service and concept extraction.

**What it tests:**
- ✓ Input validation (min/max length, empty text)
- ✓ Concept extraction with GPT-4
- ✓ Response format validation
- ✓ Full processing workflow
- ✓ Metadata generation

**Run:**
```bash
python api/tests/test_text_processing.py
```

### `test_relationships.py`
Tests relationship extraction between concepts.

**What it tests:**
- ✓ Simple relationship extraction
- ✓ Various relationship types (is-a, part-of, uses, etc.)
- ✓ Response format validation
- ✓ Full pipeline (concepts + relationships)
- ✓ Source/target validation

**Run:**
```bash
python api/tests/test_relationships.py
```

### `test_embeddings.py`
Tests embedding generation and semantic similarity.

**What it tests:**
- ✓ Single embedding generation
- ✓ Batch embedding generation
- ✓ Embedding dimensions (1536 for text-embedding-3-small)
- ✓ Cosine similarity for similar concepts
- ✓ Cosine similarity for dissimilar concepts
- ✓ Adding embeddings to concepts
- ✓ Full pipeline with embeddings

**Run:**
```bash
python api/tests/test_embeddings.py
```

### `test_api.py`
Tests the FastAPI endpoints.

**What it tests:**
- ✓ Health check endpoint
- ✓ Text processing endpoint with valid input
- ✓ Invalid input handling
- ✓ Response format validation
- ✓ Embeddings integration
- ✓ Error responses

**Run:**
```bash
python api/tests/test_api.py
```

### `test_graph_service.py`
Tests the NetworkX graph service (Tasks 7 & 8).

**What it tests:**
- ✓ Graph creation with nodes and edges
- ✓ Graph storage and retrieval
- ✓ Node and edge queries
- ✓ BFS/DFS traversal (Task 8)
- ✓ Node expansion for UI (Task 8)
- ✓ Path finding (shortest path, all paths)
- ✓ Subgraph extraction
- ✓ Distance queries (n-hop neighbors)
- ✓ Graph statistics

**Run:**
```bash
python api/tests/test_graph_service.py
```

### `test_graph_api.py`
Tests the graph API endpoints (Task 9).

**What it tests:**
- ✓ GET /api/py/graph/{graph_id} - retrieve graph
- ✓ POST /api/py/graph/{graph_id}/expand/{node_id} - expand node
- ✓ POST /api/py/graph/{graph_id}/relationships/{node_id} - get relationship paths
- ✓ Error handling (404 for non-existent graphs/nodes)

**Run:**
```bash
python api/tests/test_graph_api.py
```

### `test_llm_service.py`
Tests the LLM service for relationship explanations and Q&A (Task 10).

**What it tests:**
- ✓ Relationship explanation between two nodes
- ✓ Explanation for node with 3+ connections
- ✓ Q&A functionality with graph context
- ✓ Graph summary generation

**Run:**
```bash
python api/tests/test_llm_service.py
```

**Note:** This test makes actual API calls to OpenAI and may take 30-60 seconds to complete.

## Running All Tests

To run all tests in sequence:

```bash
# Test 1: Setup and dependencies
python api/tests/test_setup.py

# Test 2: Data models
python api/tests/test_models.py

# Test 3: Text processing service
python api/tests/test_text_processing.py

# Test 4: Relationship extraction
python api/tests/test_relationships.py

# Test 5: Embedding generation
python api/tests/test_embeddings.py

# Test 6: API endpoints
python api/tests/test_api.py

# Test 7: Graph service
python api/tests/test_graph_service.py

# Test 8: Graph API endpoints
python api/tests/test_graph_api.py

# Test 9: LLM service (relationship explanations)
python api/tests/test_llm_service.py
```

## Prerequisites

Before running tests:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Copy example file
   copy env.example .env.local
   
   # Edit .env.local and add your OpenAI API key
   ```

3. **Required environment variables:**
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `OPENAI_MODEL` (optional) - Model to use (default: gpt-4o-mini)

## Expected Output

All tests should show:
```
🎉 All tests passed!
```

If any test fails, review the error messages and fix the issues before proceeding.

## Test Organization

Tests are organized by functionality:
- **Setup tests** - Verify environment and dependencies
- **Model tests** - Verify data structures and validation
- **Service tests** - (Coming in future phases)
- **Integration tests** - (Coming in future phases)

