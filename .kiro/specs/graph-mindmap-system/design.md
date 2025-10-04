# Design Document

## Overview

This document outlines the technical design for an interactive mindmap system that transforms unstructured text into explorable knowledge graphs using graph representation learning and LLM integration. The system combines NLP, graph algorithms, and modern web technologies to create a NotebookLLM-inspired experience with advanced graph-based reasoning capabilities.

### Core Design Principles

1. **Graph-First Architecture**: All data structures and algorithms prioritize graph representations and traversal
2. **Incremental Processing**: Support progressive enhancement and lazy loading for large graphs
3. **Modular Services**: Separate concerns into independent, scalable microservices
4. **Real-time Interactivity**: Optimize for sub-second response times on user interactions
5. **Reproducibility**: Containerized deployment with minimal configuration

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI]
        VIS[D3.js/Cytoscape Visualization]
        STATE[State Management - Zustand/Redux]
    end
    
    subgraph "API Gateway"
        GATEWAY[FastAPI Gateway]
        AUTH[Authentication Middleware]
        RATE[Rate Limiter]
    end
    
    subgraph "Core Services"
        TEXT[Text Processing Service]
        GRAPH[Graph Service]
        LLM[LLM Integration Service]
        TTS[Text-to-Speech Service]
    end
    
    subgraph "Data Layer"
        GRAPHDB[(Neo4j/NetworkX)]
        VECTOR[(Vector Store - Pinecone/Chroma)]
        CACHE[(Redis Cache)]
    end
    
    UI --> GATEWAY
    VIS --> GATEWAY
    STATE --> GATEWAY
    
    GATEWAY --> AUTH
    GATEWAY --> RATE
    
    AUTH --> TEXT
    AUTH --> GRAPH
    AUTH --> LLM
    AUTH --> TTS
    
    TEXT --> GRAPHDB
    TEXT --> VECTOR
    GRAPH --> GRAPHDB
    GRAPH --> VECTOR
    LLM --> VECTOR
    
    GRAPH --> CACHE
    LLM --> CACHE
```

### Technology Stack

**Frontend (Next.js 14):**
- Next.js 14.2.13 with App Router for UI framework
- React 18.3.1 with TypeScript for UI components
- D3.js or Cytoscape.js for graph visualization
- Zustand or React Context for state management
- TailwindCSS 3.4.12 for styling (already configured)
- Native fetch with Next.js for API state management

**Backend (FastAPI):**
- FastAPI (Python) for API gateway and services (already set up at /api/py/)
- NetworkX for in-memory graph operations
- Neo4j (optional) for persistent graph storage
- Redis for caching and session management

**ML/AI:**
- OpenAI GPT-4 for LLM and reasoning
- OpenAI text-embedding-3-small for text embeddings (simpler than Sentence-BERT)
- Node2Vec for graph embeddings (lightweight, no training needed)
- OpenAI TTS for voice synthesis (no ElevenLabs needed)

**Infrastructure:**
- Docker & Docker Compose for containerization
- Next.js built-in proxy for API routing (configured in next.config.js)
- PostgreSQL for metadata storage

## Components and Interfaces

### 1. Text Processing Service

**Responsibility**: Extract concepts and relationships from raw text

**Location**: `api/services/text_processing.py`

**Key Components:**
- **TextParser**: Tokenization, sentence segmentation, and preprocessing
- **ConceptExtractor**: Use OpenAI GPT-4 to extract key concepts (simpler than spaCy NER)
- **RelationshipExtractor**: Use OpenAI GPT-4 to identify relationships (simpler than dependency parsing)
- **EmbeddingGenerator**: Use OpenAI text-embedding-3-small API for embeddings

**API Endpoints:**
```
POST /api/py/text/process
Request: { "text": string, "options": { "max_nodes": int, "min_confidence": float } }
Response: { "graph_id": string, "nodes": Node[], "edges": Edge[], "metadata": {} }
```

**Note**: All FastAPI endpoints are prefixed with `/api/py/` and proxied through Next.js in development mode (see next.config.js)

**Algorithm Flow:**
1. Preprocess text (clean, normalize, segment)
2. Use OpenAI GPT-4 to extract key concepts with structured output
3. Use OpenAI GPT-4 to identify relationships between concepts
4. Score concepts by importance (from GPT-4 response)
5. Filter low-confidence concepts and relationships
6. Generate embeddings using OpenAI text-embedding-3-small API
7. Return structured graph data

**Note**: Using OpenAI for extraction is simpler and more accurate than traditional NLP pipelines, requires no model training, and handles edge cases better.

### 2. Graph Service

**Responsibility**: Manage graph structure, traversal, and analysis

**Location**: `api/services/graph_service.py`

**Key Components:**
- **GraphBuilder**: Construct and validate graph structures
- **GraphTraversal**: BFS, DFS, shortest path, and subgraph extraction
- **GraphEmbedding**: Compute node embeddings using Node2Vec or GNN
- **ClusteringEngine**: Group related nodes using Louvain or K-means
- **SimilarityEngine**: Find similar nodes using cosine similarity on embeddings

**API Endpoints:**
```
GET /api/py/graph/{graph_id}
Response: { "nodes": Node[], "edges": Edge[], "metadata": {} }

POST /api/py/graph/{graph_id}/expand/{node_id}
Response: { "subnodes": Node[], "edges": Edge[] }

POST /api/py/graph/{graph_id}/relationships/{node_id}
Response: { "explanation": string, "paths": Path[], "related_nodes": Node[] }

GET /api/py/graph/{graph_id}/similar/{node_id}
Response: { "similar_nodes": Node[], "scores": float[] }
```

**Graph Data Model:**
```python
class Node:
    id: str
    label: str
    description: str
    embedding: List[float]
    metadata: Dict[str, Any]
    source_text: str
    confidence: float
    
class Edge:
    source: str
    target: str
    relationship_type: str
    weight: float
    confidence: float
    metadata: Dict[str, Any]
    
class Graph:
    nodes: List[Node]
    edges: List[Edge]
    metadata: Dict[str, Any]
    embeddings: np.ndarray
```

### 3. LLM Integration Service

**Responsibility**: Generate explanations, answer questions, and provide context

**Location**: `api/services/llm_service.py`

**Key Components:**
- **PromptBuilder**: Construct context-aware prompts with graph structure
- **LLMClient**: Interface with OpenAI/Anthropic APIs
- **ContextRetriever**: Fetch relevant nodes and paths from graph
- **ResponseFormatter**: Structure and format LLM responses

**API Endpoints:**
```
POST /api/py/llm/explain
Request: { "graph_id": string, "node_id": string, "context_depth": int }
Response: { "explanation": string, "related_concepts": string[] }

POST /api/py/llm/qa
Request: { "graph_id": string, "node_id": string, "question": string, "history": Message[] }
Response: { "answer": string, "sources": Node[], "confidence": float }
```

**Prompt Engineering Strategy:**
- Include node content, connected nodes (1-2 hops), and relationship types
- Use graph paths to provide structural context
- Incorporate embeddings to retrieve semantically similar content
- Maintain conversation history for follow-up questions

**Example Prompt Template:**
```
You are analyzing a knowledge graph about [topic].

Current Node: {node.label}
Description: {node.description}
Source Text: {node.source_text}

Connected Concepts:
{for edge in edges}
- {edge.target.label} ({edge.relationship_type}): {edge.target.description}
{endfor}

Graph Context:
{graph_paths}

User Question: {question}

Provide a detailed answer based on the graph structure and content.
```

### 4. Text-to-Speech Service

**Responsibility**: Convert text explanations to audio narration

**Location**: `api/services/tts_service.py`

**Key Components:**
- **TTSClient**: Interface with OpenAI TTS API (simpler, no ElevenLabs needed)
- **AudioCache**: Cache generated audio files in `public/audio/`
- **StreamingHandler**: Support audio streaming for long content (OpenAI TTS supports streaming)

**API Endpoints:**
```
POST /api/py/tts/synthesize
Request: { "text": string, "voice": string, "speed": float }
Response: { "audio_url": string, "duration": float }
```

**Note**: Generated audio files are stored in Next.js `public/audio/` directory for direct access

### 5. Frontend Visualization Component

**Responsibility**: Render interactive mindmap and handle user interactions

**Location**: Next.js App Router structure
- Main page: `app/page.tsx` (replace template content)
- Mindmap component: `app/components/Mindmap.tsx`
- Node component: `app/components/Node.tsx`
- Side panel: `app/components/SidePanel.tsx`
- Layout: `app/layout.tsx` (already configured with Inter font and TailwindCSS)

**Key Components:**
- **GraphRenderer**: D3.js force-directed layout or Cytoscape.js
- **NodeComponent**: Interactive node with expand/collapse, selection
- **EdgeComponent**: Relationship lines with labels
- **ControlPanel**: Zoom, pan, filter, search controls
- **SidePanel**: Q&A interface, relationship explanations, node details

**State Management:**
```typescript
interface GraphState {
  graphId: string;
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  expandedNodes: Set<string>;
  highlightedNodes: Set<string>;
  layout: LayoutConfig;
  filters: FilterConfig;
}

interface UIState {
  sidePanelOpen: boolean;
  activeTab: 'qa' | 'relationships' | 'details';
  audioPlaying: boolean;
  loading: boolean;
}
```

**API Integration**: Use Next.js native fetch to call `/api/py/*` endpoints (automatically proxied in development)

**Interaction Patterns:**
- Click node → Select and show details
- Double-click node → Expand/collapse children
- Hover node → Highlight connections
- Right-click node → Context menu (explain, Q&A, similar)
- Drag → Pan canvas
- Scroll → Zoom in/out

## Data Models

### Graph Storage Schema (Neo4j)

```cypher
// Node structure
CREATE (c:Concept {
  id: string,
  label: string,
  description: string,
  source_text: string,
  confidence: float,
  created_at: datetime,
  embedding: list<float>
})

// Relationship structure
CREATE (c1:Concept)-[r:RELATES_TO {
  type: string,
  weight: float,
  confidence: float,
  created_at: datetime
}]->(c2:Concept)

// Graph metadata
CREATE (g:Graph {
  id: string,
  user_id: string,
  title: string,
  created_at: datetime,
  updated_at: datetime,
  node_count: int,
  edge_count: int
})

CREATE (g)-[:CONTAINS]->(c:Concept)
```

### Vector Store Schema (Pinecone/Chroma)

```python
# Document structure for vector storage
{
  "id": "node_id",
  "values": [0.1, 0.2, ...],  # 768-dim embedding
  "metadata": {
    "graph_id": "graph_123",
    "label": "Machine Learning",
    "description": "...",
    "node_type": "concept",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### API Response Models

```typescript
interface Node {
  id: string;
  label: string;
  description: string;
  sourceText: string;
  confidence: number;
  metadata: Record<string, any>;
  position?: { x: number; y: number };
  hasChildren: boolean;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  relationshipType: string;
  weight: number;
  confidence: number;
}

interface GraphResponse {
  graphId: string;
  nodes: Node[];
  edges: Edge[];
  metadata: {
    nodeCount: number;
    edgeCount: number;
    createdAt: string;
    updatedAt: string;
  };
}
```

## Graph Representation Learning

### Node Embedding Strategy

**Approach**: Hybrid embedding combining textual and structural information

1. **Textual Embeddings**:
   - Use OpenAI text-embedding-3-small for node content (1536 dimensions)
   - Simpler than Sentence-BERT, no local model needed
   - Captures semantic meaning of concepts

2. **Structural Embeddings**:
   - Use Node2Vec for graph structure
   - Random walks: 10 walks per node, length 80
   - Window size: 10, embedding dimension: 128
   - Captures graph topology and neighborhood

3. **Combined Embedding**:
   ```python
   final_embedding = concat([
       text_embedding * 0.7,
       structural_embedding * 0.3
   ])
   ```

### Graph Neural Network (Optional Enhancement)

For more sophisticated graph learning:

```python
class GraphSAGE:
    def __init__(self, input_dim, hidden_dim, output_dim):
        self.conv1 = SAGEConv(input_dim, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, output_dim)
    
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x
```

### Similarity Search

```python
def find_similar_nodes(target_node_id, graph, top_k=5):
    target_embedding = graph.nodes[target_node_id].embedding
    similarities = []
    
    for node_id, node in graph.nodes.items():
        if node_id != target_node_id:
            sim = cosine_similarity(target_embedding, node.embedding)
            similarities.append((node_id, sim))
    
    return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
```

## Error Handling

### Error Categories and Strategies

1. **Input Validation Errors** (4xx):
   - Empty or too short text → Return 400 with min length requirement
   - Text exceeds limit → Return 413 with max length
   - Invalid graph_id → Return 404 with error message

2. **Processing Errors** (5xx):
   - NLP extraction fails → Return partial results with warning
   - Graph generation fails → Return 500 with retry suggestion
   - Embedding computation fails → Fall back to text-only mode

3. **External Service Errors**:
   - LLM API timeout → Retry with exponential backoff (3 attempts)
   - TTS service unavailable → Return text-only response
   - Vector store unavailable → Use in-memory fallback

4. **Performance Degradation**:
   - Graph too large → Apply clustering and show top-level only
   - Query too slow → Return cached results with staleness indicator

### Error Response Format

```json
{
  "error": {
    "code": "GRAPH_GENERATION_FAILED",
    "message": "Failed to generate graph from input text",
    "details": "Insufficient concepts extracted (min: 3, found: 1)",
    "retry": true,
    "suggestions": ["Try providing more detailed text", "Ensure text is at least 100 characters"]
  }
}
```

### Retry Logic

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Timeout, ConnectionError))
)
async def call_llm_api(prompt: str) -> str:
    response = await llm_client.complete(prompt)
    return response.text
```

## Testing Strategy

### Unit Tests

**Text Processing Service:**
- Test concept extraction with various text types
- Test relationship extraction accuracy
- Test embedding generation consistency
- Test edge cases (empty text, special characters, multiple languages)

**Graph Service:**
- Test graph construction from node/edge lists
- Test traversal algorithms (BFS, DFS, shortest path)
- Test embedding computation and similarity search
- Test clustering algorithms
- Test graph persistence and retrieval

**LLM Service:**
- Test prompt construction with different graph structures
- Test context retrieval with various depths
- Test response parsing and formatting
- Mock LLM API calls for deterministic testing

### Integration Tests

**End-to-End Workflows:**
1. Text input → Graph generation → Visualization
2. Node expansion → Subgraph retrieval → UI update
3. Relationship explanation → LLM call → TTS → Audio playback
4. Q&A interaction → Context retrieval → LLM response

**API Integration:**
- Test all API endpoints with valid/invalid inputs
- Test authentication and authorization
- Test rate limiting
- Test concurrent requests

### Performance Tests

**Load Testing:**
- Simulate 10 concurrent users
- Test graph generation with texts of varying sizes (100 chars to 50k chars)
- Measure response times for all operations
- Test memory usage with large graphs (1000+ nodes)

**Benchmarks:**
- Text processing: < 10s for 5000 words
- Node expansion: < 2s
- Relationship explanation: < 3s
- Q&A response: < 5s
- TTS generation: < 2s

### UI/UX Testing

**Interaction Testing:**
- Test node selection and highlighting
- Test expand/collapse animations
- Test pan and zoom smoothness
- Test responsive layout on different screen sizes

**Accessibility Testing:**
- Test keyboard navigation
- Test screen reader compatibility
- Test color contrast ratios
- Test focus indicators

## Performance Optimization

### Frontend Optimizations

1. **Lazy Loading**: Render only visible nodes in viewport
2. **Virtual Scrolling**: For large node lists in side panels
3. **Debouncing**: Delay API calls on rapid interactions
4. **Memoization**: Cache computed layouts and positions
5. **Web Workers**: Offload graph layout calculations

### Backend Optimizations

1. **Caching Strategy**:
   - Cache graph structures in Redis (TTL: 1 hour)
   - Cache LLM responses (TTL: 24 hours)
   - Cache embeddings permanently
   - Cache TTS audio files (TTL: 7 days)

2. **Database Optimization**:
   - Index node IDs and graph IDs
   - Use connection pooling
   - Implement query result pagination

3. **Async Processing**:
   - Use async/await for I/O operations
   - Implement task queues for long-running operations
   - Use background workers for embedding computation

### Scalability Considerations

1. **Horizontal Scaling**: Stateless services behind load balancer
2. **Database Sharding**: Partition graphs by user_id
3. **CDN**: Serve static assets and audio files
4. **Rate Limiting**: 100 requests/minute per user

## Security Measures

### Input Validation

```python
def validate_text_input(text: str) -> tuple[bool, str]:
    if not text or len(text.strip()) == 0:
        return False, "Text cannot be empty"
    
    if len(text) < 100:
        return False, "Text must be at least 100 characters"
    
    if len(text) > 50000:
        return False, "Text cannot exceed 50,000 characters"
    
    # Sanitize HTML and script tags
    text = bleach.clean(text, strip=True)
    
    return True, text
```

### Authentication & Authorization

- JWT tokens for API authentication
- Token expiration: 24 hours
- Refresh token mechanism
- User-specific graph access control

### Data Protection

- HTTPS for all communications
- Encrypt sensitive data at rest
- Sanitize all user inputs
- Implement CORS policies
- Rate limiting per user/IP

## Deployment Architecture

### Project Structure

```
.
├── app/                      # Next.js App Router
│   ├── components/          # React components
│   ├── layout.tsx           # Root layout (already configured)
│   ├── page.tsx             # Main page (to be replaced)
│   └── globals.css          # Global styles (TailwindCSS configured)
├── api/                     # FastAPI backend
│   ├── index.py            # Main FastAPI app (already set up)
│   ├── services/           # Service modules (to be created)
│   │   ├── text_processing.py
│   │   ├── graph_service.py
│   │   ├── llm_service.py
│   │   └── tts_service.py
│   ├── models/             # Pydantic models
│   └── utils/              # Utility functions
├── public/                 # Static assets
│   └── audio/              # Generated TTS audio files
├── next.config.js          # Next.js config (API proxy configured)
├── package.json            # Node dependencies
├── requirements.txt        # Python dependencies (to be updated)
├── docker-compose.yml      # Docker orchestration (to be created)
└── Dockerfile              # Multi-stage build (to be created)
```

### Docker Compose Structure

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/graphdb
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NODE_ENV=production
    depends_on:
      - db
      - redis
    volumes:
      - ./public:/app/public
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=graphdb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  postgres_data:
  neo4j_data:
```

**Note**: The template uses a unified structure where Next.js and FastAPI run together. The Next.js dev server proxies `/api/py/*` requests to FastAPI running on port 8000.

### Environment Variables

Create a `.env.local` file in the root directory:

```bash
# API Keys (only OpenAI needed!)
OPENAI_API_KEY=sk-...

# Database (optional for MVP - can use in-memory storage)
DATABASE_URL=postgresql://user:pass@localhost:5432/graphdb

# Redis (optional for MVP - can skip caching initially)
REDIS_URL=redis://localhost:6379

# Application
NODE_ENV=development
LOG_LEVEL=INFO
```

**Simplified Setup**: For MVP/hackathon, only OPENAI_API_KEY is required. Database and Redis can be added later for persistence and caching.

**Development Setup**:
1. Install Node.js dependencies: `npm install`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Start Next.js dev server: `npm run dev` (runs on port 3000)
4. Start FastAPI server: `uvicorn api.index:app --reload --port 8000`
5. Next.js automatically proxies `/api/py/*` to `http://127.0.0.1:8000/api/py/*`

## Monitoring and Logging

### Logging Strategy

```python
import logging
import structlog

logger = structlog.get_logger()

# Log levels
logger.info("graph_generated", graph_id=graph_id, node_count=len(nodes))
logger.warning("low_confidence_nodes", count=low_conf_count)
logger.error("llm_api_failed", error=str(e), retry_count=retry)
```

### Metrics to Track

- Request latency (p50, p95, p99)
- Error rates by endpoint
- Graph generation success rate
- LLM API call duration
- Cache hit rates
- Active user sessions

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": await check_db_connection(),
            "redis": await check_redis_connection(),
            "llm_api": await check_llm_api()
        }
    }
```

## Future Enhancements

1. **Multi-modal Input**: Support PDF, images, audio transcripts
2. **Collaborative Editing**: Real-time multi-user graph editing
3. **Graph Versioning**: Track changes and allow rollback
4. **Advanced Analytics**: Graph metrics, centrality measures, community detection
5. **Export Options**: Export to PDF, PNG, JSON, GraphML
6. **Custom Styling**: User-defined color schemes and layouts
7. **Integration APIs**: Webhook support for external tools
8. **Mobile App**: Native iOS/Android applications

## Design Decisions and Rationales

### Why FastAPI?
- Async support for concurrent requests
- Automatic API documentation (OpenAPI) at `/api/py/docs`
- Type hints and validation with Pydantic
- High performance comparable to Node.js
- Already integrated in the template with Next.js proxy configuration

### Why NetworkX + Neo4j?
- NetworkX for fast in-memory graph operations
- Neo4j for persistent storage and complex queries
- Hybrid approach balances performance and persistence

### Why D3.js/Cytoscape?
- D3.js: Maximum flexibility for custom visualizations
- Cytoscape.js: Rich graph layout algorithms out-of-the-box
- Both support large graphs with good performance

### Why Node2Vec over GNN?
- Simpler to implement and deploy
- No training required (unsupervised)
- Good performance for moderate-sized graphs
- GNN can be added later as enhancement

### Why Redis for Caching?
- In-memory speed for frequent access
- Built-in TTL support
- Pub/sub for real-time updates
- Simple key-value interface

## Integration with Existing Template

### Current Template Structure
The project uses a Next.js + FastAPI template with the following setup:
- **Next.js 14** with App Router and TypeScript
- **TailwindCSS** pre-configured for styling
- **FastAPI** basic setup at `api/index.py` with example endpoint
- **API Proxy** configured in `next.config.js` to route `/api/py/*` to FastAPI

### Development Workflow
1. **Frontend Development**: Edit files in `app/` directory using Next.js App Router
2. **Backend Development**: Add services in `api/` directory using FastAPI
3. **Styling**: Use TailwindCSS classes (already configured)
4. **API Calls**: Use fetch to call `/api/py/*` endpoints from frontend components
5. **Testing**: Access FastAPI docs at `http://localhost:3000/docs` in development

### Key Modifications Needed
1. Replace template `app/page.tsx` with mindmap interface
2. Add FastAPI service modules in `api/services/`
3. Update `requirements.txt` with ML/NLP dependencies
4. Create React components for graph visualization
5. Add Docker configuration for production deployment

## Conclusion

This design provides a robust, scalable foundation for building an interactive mindmap system with advanced graph representation learning, fully integrated with the existing Next.js + FastAPI template. The modular architecture allows for incremental development and easy testing, while the technology choices balance performance, developer experience, and deployment simplicity. The system leverages the pre-configured template structure to accelerate development while meeting all requirements and maintaining flexibility for future enhancements.
