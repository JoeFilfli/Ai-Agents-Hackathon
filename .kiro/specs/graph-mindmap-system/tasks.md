# Implementation Plan

- [ ] 1. Set up project dependencies and configuration
  - Install Python libraries (openai, networkx, node2vec) - simplified, no spaCy/transformers needed!
  - Install graph visualization libraries for frontend (d3 or cytoscape.js)
  - Create requirements.txt with minimal Python dependencies
  - Update package.json with frontend dependencies
  - Create .env.local with OPENAI_API_KEY (only key needed!)
  - _Requirements: 9.1, 9.5, 17.8_
  - **Test**: Run `pip install -r requirements.txt` and `npm install` successfully. Check .env.local has OPENAI_API_KEY. Test OpenAI connection with simple API call.

- [ ] 2. Implement core data models and types
  - [ ] 2.1 Create Pydantic models for backend
    - Create api/models/graph_models.py with Node, Edge, and Graph classes
    - Add validation rules for node and edge properties
    - Include embedding field types and metadata structures
    - _Requirements: 1.5, 2.1, 2.2_
    - **Test**: Import models in Python REPL. Create sample Node/Edge/Graph instances. Verify validation catches invalid data (e.g., negative confidence scores).
  
  - [ ] 2.2 Create TypeScript interfaces for frontend
    - Create app/types/graph.ts with Node, Edge, GraphResponse interfaces
    - Define GraphState and UIState interfaces for state management
    - Add type definitions for API request/response payloads
    - _Requirements: 3.3, 3.4, 7.1_
    - **Test**: Run `npm run build` to verify TypeScript compiles without errors. Import types in a test component to verify they work.

- [ ] 3. Build text processing service
  - [ ] 3.1 Implement text preprocessing and validation
    - Create api/services/text_processing.py with TextParser class
    - Implement input validation (length checks, sanitization)
    - Add text cleaning and normalization functions
    - Write unit tests for validation edge cases
    - _Requirements: 1.1, 1.2, 1.6, 1.7, 15.1_
    - **Test**: Run unit tests with pytest. Test with text <100 chars (should fail), >50k chars (should fail), with HTML tags (should sanitize), with special characters (should handle gracefully).
  
  - [ ] 3.2 Implement concept extraction
    - Add ConceptExtractor class using OpenAI GPT-4 with structured output
    - Use prompt: "Extract key concepts from this text as JSON: {concepts: [{name, description, importance}]}"
    - Score concepts by importance from GPT-4
    - Filter low-confidence concepts
    - Write unit tests with mocked OpenAI responses
    - _Requirements: 1.3, 1.8_
    - **Test**: Run unit tests. Extract concepts from sample text about "machine learning" - GPT-4 should identify "neural networks", "algorithms", "data" with descriptions. Verify concepts have labels and importance scores. Much simpler than spaCy!
  
  - [ ] 3.3 Implement relationship extraction
    - Add RelationshipExtractor class using OpenAI GPT-4
    - Use prompt: "Identify relationships between these concepts as JSON: {relationships: [{source, target, type, strength}]}"
    - GPT-4 assigns relationship types (is-a, part-of, related-to, etc.)
    - Calculate edge weights from GPT-4 strength scores
    - Write unit tests with mocked OpenAI responses
    - _Requirements: 1.4, 2.2, 2.4_
    - **Test**: Run unit tests. Process text "Python is a programming language" - GPT-4 extracts relationship (Python, is-a, programming language). Verify edges have source, target, type, and weight. Much more accurate than dependency parsing!
  
  - [ ] 3.4 Implement embedding generation
    - Add EmbeddingGenerator class using OpenAI text-embedding-3-small API
    - Generate 1536-dim embeddings for each concept (one API call per concept)
    - Store embeddings with node data
    - Write unit tests with mocked OpenAI responses
    - _Requirements: 13.1, 13.2_
    - **Test**: Run unit tests. Generate embeddings for "machine learning" and "artificial intelligence" - should produce 1536-dim vectors. Verify similar concepts have high cosine similarity (>0.7). Simpler than Sentence-BERT, no local model!
  
  - [ ] 3.5 Create text processing API endpoint
    - Add POST /api/py/text/process endpoint in api/index.py
    - Integrate all text processing components
    - Return structured graph data (nodes, edges, metadata)
    - Add error handling and logging
    - Write integration tests for the endpoint
    - _Requirements: 1.5, 9.1, 9.2, 16.3_
    - **Test**: Start FastAPI server. Use curl or Postman to POST sample text to /api/py/text/process. Verify response contains graph_id, nodes array, edges array. Check logs show processing steps. Test with invalid input (too short) - should return 400 error.

- [ ] 4. Build graph service
  - [ ] 4.1 Implement graph construction and storage
    - Create api/services/graph_service.py with GraphBuilder class
    - Build NetworkX graph from nodes and edges
    - Implement in-memory graph storage with unique IDs
    - Add graph validation logic
    - Write unit tests for graph construction
    - _Requirements: 2.1, 2.5, 14.1_
    - **Test**: Run unit tests. Create graph with 10 nodes and 15 edges. Verify NetworkX graph has correct node/edge count. Check graph_id is unique UUID. Verify isolated nodes are detected.
  
  - [ ] 4.2 Implement graph traversal algorithms
    - Add GraphTraversal class with BFS, DFS, shortest path methods
    - Implement subgraph extraction for node expansion
    - Add multi-hop relationship path finding (up to 3 degrees)
    - Write unit tests for traversal algorithms
    - _Requirements: 5.3, 5.7, 5.8_
    - **Test**: Run unit tests. Create graph A->B->C->D. BFS from A should return [A,B,C,D]. Shortest path A to D should be [A,B,C,D]. Expand node B should return subgraph with B and its neighbors.
  
  - [ ] 4.3 Implement node embedding computation
    - Add GraphEmbedding class using Node2Vec
    - Compute structural embeddings for graph topology
    - Combine textual and structural embeddings (70/30 ratio)
    - Write unit tests for embedding computation
    - _Requirements: 13.1, 13.8_
    - **Test**: Run unit tests. Compute embeddings for sample graph. Verify combined embedding is 768+128=896 dimensions. Check that connected nodes have higher similarity than disconnected ones.
  
  - [ ] 4.4 Implement similarity search
    - Add SimilarityEngine class with cosine similarity
    - Find similar nodes based on embeddings
    - Return top-k similar nodes with scores
    - Optimize for performance (<500ms for 1000 nodes)
    - Write unit tests for similarity search
    - _Requirements: 13.2, 13.3, 13.7_
    - **Test**: Run unit tests. Create graph with 100 nodes. Find top-5 similar to node X. Verify returns 5 nodes with similarity scores in descending order. Benchmark with 1000 nodes - should complete <500ms.
  
  - [ ] 4.5 Implement clustering for large graphs
    - Add ClusteringEngine class using Louvain algorithm
    - Apply clustering when graph exceeds 100 nodes
    - Group related nodes into clusters
    - Write unit tests for clustering
    - _Requirements: 2.8_
    - **Test**: Run unit tests. Create graph with 150 nodes. Apply clustering. Verify nodes are grouped into clusters. Check cluster assignments are consistent across runs.
  
  - [ ] 4.6 Create graph service API endpoints
    - Add GET /api/py/graph/{graph_id} endpoint
    - Add POST /api/py/graph/{graph_id}/expand/{node_id} endpoint
    - Add POST /api/py/graph/{graph_id}/relationships/{node_id} endpoint
    - Add GET /api/py/graph/{graph_id}/similar/{node_id} endpoint
    - Add error handling for invalid graph IDs
    - Write integration tests for all endpoints
    - _Requirements: 4.1, 4.2, 5.1, 9.1, 9.2_
    - **Test**: Use curl/Postman. GET /api/py/graph/{id} returns nodes and edges. POST expand returns subnodes. POST relationships returns explanation and paths. GET similar returns similar nodes. Test with invalid graph_id - should return 404.

- [ ] 5. Build LLM integration service
  - [ ] 5.1 Implement LLM client and prompt builder
    - Create api/services/llm_service.py with LLMClient class
    - Add PromptBuilder for context-aware prompts
    - Integrate OpenAI or Anthropic API
    - Include graph structure in prompts (nodes, edges, paths)
    - Write unit tests with mocked LLM responses
    - _Requirements: 5.4, 6.2_
    - **Test**: Run unit tests with mocked responses. Build prompt for node "Python" with connected nodes. Verify prompt includes node description, connected concepts, and relationship types. Test actual API call returns valid response.
  
  - [ ] 5.2 Implement context retrieval
    - Add ContextRetriever class for graph-based context
    - Fetch relevant nodes within 2 hops
    - Include relationship paths and edge types
    - Write unit tests for context retrieval
    - _Requirements: 6.3, 13.4_
    - **Test**: Run unit tests. For node A in graph A->B->C->D, retrieve context with depth=2. Should return nodes [A,B,C] with paths and edge types. Verify context includes relationship information.
  
  - [ ] 5.3 Implement explanation generation
    - Add method to generate relationship explanations
    - Use graph traversal to analyze connections
    - Format explanations with related concepts
    - Write unit tests for explanation formatting
    - _Requirements: 5.2, 5.4, 5.6_
    - **Test**: Run unit tests. Generate explanation for node with 3 connections. Verify explanation text mentions all related nodes and relationship types. Check explanation is coherent and informative.
  
  - [ ] 5.4 Implement Q&A functionality
    - Add method to answer node-specific questions
    - Maintain conversation history per node
    - Include citations and related node references
    - Handle follow-up questions with context
    - Write unit tests for Q&A logic
    - _Requirements: 6.1, 6.4, 6.5, 6.6, 6.9_
    - **Test**: Run unit tests. Ask "What is this?" about node "Python". Verify answer includes node content and related concepts. Ask follow-up "How is it used?" - verify uses conversation history. Check citations reference source text.
  
  - [ ] 5.5 Add retry logic and error handling
    - Implement exponential backoff for API failures
    - Retry up to 3 times on timeout/connection errors
    - Fall back gracefully when LLM unavailable
    - Write unit tests for retry logic
    - _Requirements: 16.1, 16.5_
    - **Test**: Run unit tests with simulated failures. Mock API to fail twice then succeed - verify retries 3 times. Mock timeout - verify exponential backoff (2s, 4s, 8s). Mock permanent failure - verify graceful fallback.
  
  - [ ] 5.6 Create LLM service API endpoints
    - Add POST /api/py/llm/explain endpoint
    - Add POST /api/py/llm/qa endpoint
    - Return structured responses with confidence scores
    - Add error handling and logging
    - Write integration tests for endpoints
    - _Requirements: 5.1, 6.1, 9.1, 9.2_
    - **Test**: Use curl/Postman. POST to /api/py/llm/explain with graph_id and node_id. Verify returns explanation text and related_concepts array. POST to /api/py/llm/qa with question. Verify returns answer, sources, confidence. Check logs show LLM calls.

- [ ] 6. Build text-to-speech service
  - [ ] 6.1 Implement TTS client
    - Create api/services/tts_service.py with TTSClient class
    - Integrate OpenAI TTS API (tts-1 model with alloy voice)
    - Generate MP3 audio from text explanations
    - Write unit tests with mocked OpenAI responses
    - _Requirements: 8.2_
    - **Test**: Run unit tests with mocked API. Generate audio for "Hello world". Verify returns audio data. Test actual OpenAI TTS call - verify audio file is valid MP3 and playable. Much simpler than ElevenLabs!
  
  - [ ] 6.2 Implement audio caching
    - Add AudioCache class to store generated audio
    - Save audio files to public/audio/ directory
    - Implement cache TTL (7 days)
    - Return audio URLs for frontend access
    - Write unit tests for caching logic
    - _Requirements: 8.3, 8.4_
    - **Test**: Run unit tests. Generate audio for same text twice. Verify second call uses cache (faster). Check public/audio/ directory contains audio file. Verify URL is accessible. Test cache expiry after TTL.
  
  - [ ] 6.3 Create TTS API endpoint
    - Add POST /api/py/tts/synthesize endpoint
    - Accept text, voice, and speed parameters
    - Return audio URL and duration
    - Add error handling for TTS failures
    - Write integration tests for endpoint
    - _Requirements: 8.1, 8.7, 9.1_
    - **Test**: Use curl/Postman. POST to /api/py/tts/synthesize with text="Test audio". Verify returns audio_url and duration. Access URL in browser - should play audio. Test with TTS service down - should return error gracefully.

- [ ] 7. Implement frontend state management
  - [ ] 7.1 Set up state management
    - Create app/store/graphStore.ts using Zustand or React Context
    - Define GraphState with nodes, edges, selectedNode
    - Define UIState with sidePanelOpen, activeTab, loading
    - Add actions for updating state
    - _Requirements: 3.1, 7.1_
    - **Test**: Import store in test component. Set nodes/edges. Verify state updates. Select a node - verify selectedNode updates. Toggle sidePanelOpen - verify UI state changes. Check TypeScript types are enforced.
  
  - [ ] 7.2 Implement API client functions
    - Create app/lib/api.ts with fetch wrappers
    - Add functions for all backend endpoints (/api/py/*)
    - Handle loading states and errors
    - Add request/response type safety
    - _Requirements: 9.1, 9.2, 12.10_
    - **Test**: Start both Next.js and FastAPI servers. Call api.processText() with sample text. Verify returns typed GraphResponse. Call with invalid data - verify error handling works. Check network tab shows requests to /api/py/*.

- [ ] 8. Build graph visualization component
  - [ ] 8.1 Implement base graph renderer
    - Create app/components/Mindmap.tsx with D3.js or Cytoscape.js
    - Render nodes and edges from state
    - Implement force-directed layout algorithm
    - Add pan and zoom capabilities
    - _Requirements: 3.1, 3.4, 3.5, 3.6_
    - **Test**: Run `npm run dev`. Load page with sample graph data. Verify nodes and edges render visually. Drag to pan - canvas should move. Scroll to zoom - should zoom in/out. Check browser console for no errors.
  
  - [ ] 8.2 Implement node component
    - Create app/components/Node.tsx for individual nodes
    - Display node label and visual hierarchy
    - Add expand/collapse button for nodes with children
    - Implement hover effects and highlighting
    - _Requirements: 3.3, 4.1, 7.1_
    - **Test**: View mindmap in browser. Verify nodes show labels clearly. Nodes with children show expand arrow. Hover over node - should highlight. Check visual hierarchy (main nodes larger than subnodes).
  
  - [ ] 8.3 Implement edge rendering
    - Create app/components/Edge.tsx for relationship lines
    - Display edges with labels (relationship types)
    - Highlight edges when nodes are selected
    - _Requirements: 3.4, 7.5_
    - **Test**: View mindmap. Verify edges connect nodes with lines. Edge labels show relationship types ("is-a", "part-of"). Select a node - connected edges should highlight.
  
  - [ ] 8.4 Implement node interactions
    - Add click handler to select nodes
    - Add double-click handler to expand/collapse
    - Add hover handler to highlight connections
    - Add right-click context menu
    - _Requirements: 7.1, 7.2, 7.4_
    - **Test**: Click node - should select and highlight. Double-click node with children - should expand/collapse. Hover node - connections highlight. Right-click - context menu appears with options.
  
  - [ ] 8.5 Implement lazy loading for large graphs
    - Render only visible nodes in viewport
    - Load additional nodes on demand
    - Optimize for 60 FPS performance
    - _Requirements: 12.7, 12.8_
    - **Test**: Load graph with 200+ nodes. Verify only visible nodes render initially. Pan to new area - additional nodes load. Open browser DevTools Performance tab - verify maintains 60 FPS during pan/zoom.

- [ ] 9. Build side panel components
  - [ ] 9.1 Create side panel layout
    - Create app/components/SidePanel.tsx with tabs
    - Add tabs for Q&A, Relationships, Details
    - Implement open/close animation
    - _Requirements: 5.6, 6.1_
    - **Test**: Select a node. Side panel should open with smooth animation. Click tabs - should switch between Q&A, Relationships, Details. Click close button - panel should close with animation.
  
  - [ ] 9.2 Implement node details tab
    - Display selected node information
    - Show label, description, source text
    - Display confidence score and metadata
    - _Requirements: 3.3, 7.1_
    - **Test**: Select node. Open Details tab. Verify shows node label, description, source text excerpt, confidence score (0-1), and metadata. Check formatting is readable.
  
  - [ ] 9.3 Implement relationships tab
    - Create app/components/RelationshipsPanel.tsx
    - Display relationship explanation button
    - Show explanation text with collapsible sections
    - Highlight related nodes on the graph
    - _Requirements: 5.1, 5.2, 5.5, 5.6_
    - **Test**: Select node with connections. Open Relationships tab. Click "Explain Relationships" button. Verify explanation text appears. Related nodes highlight on graph. Collapsible sections work for different relationship types.
  
  - [ ] 9.4 Implement Q&A tab
    - Create app/components/QAPanel.tsx
    - Add question input field
    - Display conversation history with timestamps
    - Show answer with citations and related nodes
    - Add example questions when input is empty
    - _Requirements: 6.1, 6.5, 6.6, 6.7, 6.10_
    - **Test**: Select node. Open Q&A tab. See example questions. Type "What is this?" and submit. Verify answer appears with citations. Ask follow-up question - verify uses conversation context. Check timestamps show for each Q&A.
  
  - [ ] 9.5 Implement audio playback controls
    - Add audio player component
    - Display play/pause/stop controls
    - Auto-play when voice-over is ready
    - Stop current audio when new node selected
    - _Requirements: 8.3, 8.4, 8.6_
    - **Test**: Click node - audio should auto-play. Verify play/pause/stop buttons work. Select different node while audio playing - current audio stops, new audio starts. Check audio progress indicator updates.

- [ ] 10. Build main page and text input interface
  - [ ] 10.1 Create main page layout
    - Replace app/page.tsx with mindmap interface
    - Add text input area for initial text submission
    - Add loading indicator during graph generation
    - Display mindmap after processing
    - _Requirements: 1.1, 3.1, 12.2_
    - **Test**: Visit http://localhost:3000. See text input area. Paste sample text and submit. Loading indicator appears. After processing, mindmap displays. Check layout is clean and intuitive.
  
  - [ ] 10.2 Implement text submission flow
    - Add form with textarea for text input
    - Validate text length (100-50,000 chars)
    - Call /api/py/text/process endpoint
    - Handle errors and display messages
    - Show progress indicator for long texts
    - _Requirements: 1.1, 1.6, 1.7, 12.1, 12.2_
    - **Test**: Enter text <100 chars - should show error "Text must be at least 100 characters". Enter 50k+ chars - should show error. Enter valid text - should process and show mindmap. Test with 5000 word text - progress indicator shows.
  
  - [ ] 10.3 Add control panel
    - Create app/components/ControlPanel.tsx
    - Add zoom in/out buttons
    - Add reset view button
    - Add filter controls
    - _Requirements: 3.6_
    - **Test**: View mindmap. Click zoom in - graph zooms in. Click zoom out - graph zooms out. Pan graph then click reset - returns to original view. Test filter controls - nodes filter correctly.

- [ ] 11. Implement data persistence
  - [ ] 11.1 Set up database schema
    - Create database migration for graphs table
    - Add indexes for graph_id and user_id
    - Set up connection pooling
    - _Requirements: 2.5, 14.1_
    - **Test**: Run database migration. Check graphs table exists with correct columns (id, user_id, title, nodes, edges, created_at, updated_at). Verify indexes on graph_id and user_id. Test connection pool with multiple concurrent queries.
  
  - [ ] 11.2 Implement graph save/load
    - Add save functionality to persist graphs
    - Add load functionality to retrieve graphs
    - Auto-save on graph changes
    - _Requirements: 14.1, 14.2, 14.4_
    - **Test**: Create graph. Verify auto-saves to database. Refresh page. Load saved graph - all nodes and edges intact. Make changes - verify auto-saves within 1 second. Check database contains graph data.
  
  - [ ] 11.3 Create graph list view
    - Add page to display saved graphs
    - Show graph metadata (title, date, node count)
    - Add delete functionality with confirmation
    - _Requirements: 14.3, 14.5_
    - **Test**: Navigate to /graphs page. See list of saved graphs with titles, dates, node counts. Click graph - loads it. Click delete - confirmation dialog appears. Confirm delete - graph removed from list and database.

- [ ] 12. Add caching layer
  - [ ] 12.1 Set up Redis connection
    - Configure Redis client in api/utils/cache.py
    - Add connection health check
    - _Requirements: 9.1_
    - **Test**: Start Redis server. Run health check - should return "healthy". Test set/get operations. Stop Redis - health check should fail gracefully. Check logs show connection status.
  
  - [ ] 12.2 Implement caching for graph data
    - Cache graph structures (TTL: 1 hour)
    - Cache LLM responses (TTL: 24 hours)
    - Cache embeddings permanently
    - _Requirements: 12.3, 12.4, 12.5_
    - **Test**: Load graph twice. Second load should be faster (cache hit). Check Redis contains cached data. Wait 1 hour - graph cache expires. LLM response cached - same question returns instantly. Embeddings persist across restarts.
  
  - [ ] 12.3 Add cache invalidation logic
    - Invalidate cache on graph updates
    - Implement cache warming for frequently accessed graphs
    - _Requirements: 14.2_
    - **Test**: Load graph (cached). Update graph. Reload - should show updated data (cache invalidated). Check frequently accessed graphs pre-load into cache. Verify cache warming improves load times.

- [ ] 13. Implement error handling and logging
  - [ ] 13.1 Add structured logging
    - Set up structlog in api/utils/logger.py
    - Log all API requests and responses
    - Log errors with context
    - _Requirements: 16.4_
    - **Test**: Make API requests. Check logs show structured JSON with request_id, endpoint, status_code, duration. Trigger error - verify logs include error context, stack trace. Verify log levels (INFO, WARNING, ERROR) work correctly.
  
  - [ ] 13.2 Implement error response formatting
    - Create standardized error response format
    - Include error codes, messages, and suggestions
    - Add retry indicators
    - _Requirements: 9.3, 16.2_
    - **Test**: Send invalid request. Verify error response has {error: {code, message, details, retry, suggestions}}. Test different error types - each has appropriate code and message. Check retry indicator shows for transient errors.
  
  - [ ] 13.3 Add frontend error handling
    - Display user-friendly error messages
    - Add retry buttons for failed operations
    - Show fallback UI when services unavailable
    - _Requirements: 16.2, 16.6_
    - **Test**: Trigger API error. Verify user-friendly message displays (not technical details). Click retry button - operation retries. Stop backend - fallback UI shows "Service unavailable". Check error messages are helpful.

- [ ] 14. Add security measures
  - [ ] 14.1 Implement input sanitization
    - Sanitize all text inputs to prevent XSS
    - Validate all API request parameters
    - Add rate limiting middleware
    - _Requirements: 1.2, 15.1, 9.4_
    - **Test**: Submit text with <script> tags - should be sanitized. Send malformed JSON - should return 400. Make 101 requests in 1 minute - should be rate limited. Check XSS attempts are blocked.
  
  - [ ] 14.2 Add CORS configuration
    - Configure CORS policies in FastAPI
    - Restrict allowed origins
    - _Requirements: 15.2_
    - **Test**: Make request from allowed origin (localhost:3000) - should succeed. Make request from disallowed origin - should fail with CORS error. Check CORS headers in response.
  
  - [ ] 14.3 Implement authentication (optional)
    - Add JWT token authentication
    - Protect API endpoints
    - Add user-specific graph access control
    - _Requirements: 15.3, 15.4_
    - **Test**: Access protected endpoint without token - should return 401. Login and get token. Access with valid token - should succeed. Try accessing another user's graph - should return 403. Token expires - should require re-login.

- [ ] 15. Write comprehensive tests
  - [ ] 15.1 Write unit tests for text processing
    - Test concept extraction with various inputs
    - Test relationship extraction accuracy
    - Test edge cases (empty, special chars, multilingual)
    - _Requirements: 1.8_
    - **Test**: Run `pytest tests/test_text_processing.py`. All tests pass. Coverage >80%. Tests cover: English text, multilingual text, special characters, HTML tags, empty input, very long input.
  
  - [ ] 15.2 Write unit tests for graph service
    - Test graph construction and validation
    - Test traversal algorithms
    - Test embedding computation
    - Test similarity search
    - _Requirements: 2.6, 2.7, 13.7_
    - **Test**: Run `pytest tests/test_graph_service.py`. All tests pass. Coverage >80%. Tests cover: graph building, BFS/DFS, shortest path, embeddings, similarity search, clustering.
  
  - [ ] 15.3 Write integration tests
    - Test end-to-end text-to-graph workflow
    - Test node expansion flow
    - Test relationship explanation flow
    - Test Q&A interaction flow
    - _Requirements: 12.1, 12.3, 12.4, 12.5_
    - **Test**: Run `pytest tests/test_integration.py`. All tests pass. Tests verify: text input → graph generation → visualization, node expansion works end-to-end, relationship explanations include LLM calls, Q&A maintains conversation history.
  
  - [ ] 15.4 Write frontend component tests
    - Test node selection and highlighting
    - Test expand/collapse animations
    - Test pan and zoom interactions
    - _Requirements: 7.1, 7.2, 7.3_
    - **Test**: Run `npm test`. All tests pass. Tests verify: clicking node selects it, double-click expands, hover highlights, pan/zoom work correctly. Use React Testing Library or Cypress.

- [ ] 16. Optimize performance
  - [ ] 16.1 Optimize frontend rendering
    - Implement virtual scrolling for node lists
    - Add debouncing for API calls
    - Memoize computed layouts
    - Use Web Workers for layout calculations
    - _Requirements: 12.7, 12.8_
    - **Test**: Load 500 node graph. Check DevTools Performance - maintains 60 FPS. Rapidly type in search - API calls debounced (not called on every keystroke). Layout calculations don't block main thread. Memory usage stays reasonable.
  
  - [ ] 16.2 Optimize backend processing
    - Add async/await for I/O operations
    - Implement background workers for embeddings
    - Optimize database queries with indexes
    - _Requirements: 12.1, 12.9_
    - **Test**: Process 5000 word text - completes <10s. Check logs show async operations. Embedding computation runs in background. Database queries use indexes (check EXPLAIN). Handle 10 concurrent requests without slowdown.
  
  - [ ] 16.3 Add performance monitoring
    - Track API response times
    - Monitor cache hit rates
    - Log slow queries
    - _Requirements: 12.3, 12.4, 12.5_
    - **Test**: Make various API calls. Check logs show response times (p50, p95, p99). Monitor dashboard shows cache hit rate. Slow queries (>1s) logged with details. Metrics exportable for analysis.

- [ ] 17. Create Docker deployment configuration
  - [ ] 17.1 Create Dockerfile
    - Write multi-stage Dockerfile for Next.js and FastAPI
    - Install all dependencies
    - Configure production build
    - _Requirements: 10.1, 10.2_
    - **Test**: Run `docker build -t mindmap .`. Build succeeds without errors. Image size reasonable (<2GB). Run container - both Next.js and FastAPI start. Check production optimizations applied.
  
  - [ ] 17.2 Create docker-compose.yml
    - Define app, db, redis, and neo4j services
    - Configure environment variables
    - Set up volumes for data persistence
    - _Requirements: 10.1, 10.2, 10.3_
    - **Test**: Run `docker-compose up`. All services start (app, db, redis, neo4j). Check logs show no errors. Services can communicate. Volumes persist data across restarts. Environment variables loaded correctly.
  
  - [ ] 17.3 Test Docker deployment
    - Build and run containers
    - Verify all services start correctly
    - Test end-to-end functionality in containers
    - Ensure startup time < 2 minutes
    - _Requirements: 10.2, 10.4_
    - **Test**: Run `docker-compose up` from scratch. Time startup - should be <2 minutes. Access http://localhost:3000. Submit text, generate graph, test all features. Verify everything works in containerized environment. Run `docker-compose down` - clean shutdown.

- [ ] 18. Create comprehensive documentation
  - [ ] 18.1 Write README.md
    - Add project overview and features
    - Include setup instructions for local development
    - Document environment variables
    - Add Docker deployment instructions
    - Include troubleshooting section
    - _Requirements: 17.1, 17.2, 17.8, 17.9_
    - **Test**: Follow README from scratch on clean machine. Verify can set up and run project successfully. Check all commands work. Environment variables documented. Docker instructions work. Troubleshooting section helpful.
  
  - [ ] 18.2 Document API endpoints
    - Create API documentation with examples
    - Include request/response schemas
    - Document error scenarios
    - _Requirements: 9.5, 17.7_
    - **Test**: Visit /api/py/docs (FastAPI auto-docs). All endpoints documented. Try example requests from docs - they work. Error responses documented. Schemas show required/optional fields.
  
  - [ ] 18.3 Add code comments
    - Comment complex algorithms
    - Document graph representation learning techniques
    - Explain design decisions
    - _Requirements: 17.5, 17.6_
    - **Test**: Review code. Complex functions have docstrings. Graph algorithms explained. Node2Vec implementation documented. Design decisions noted in comments. New developer can understand code.
  
  - [ ] 18.4 Create demo video
    - Record walkthrough of all features
    - Show text input to graph generation
    - Demonstrate node expansion and Q&A
    - Show relationship explanations and TTS
    - _Requirements: 17.4_
    - **Test**: Watch demo video. Covers all major features (text input, graph visualization, node expansion, relationships, Q&A, TTS). Clear narration. Good quality. Length 3-5 minutes. Uploaded and linked in README.

- [ ] 19. Polish UI/UX
  - [ ] 19.1 Apply consistent styling
    - Use TailwindCSS for all components
    - Define color palette and typography
    - Ensure consistent spacing and layout
    - _Requirements: 11.3_
    - **Test**: Review all pages. Consistent colors throughout. Typography follows design system. Spacing uniform. No inline styles. TailwindCSS classes used. Dark mode works if implemented.
  
  - [ ] 19.2 Add smooth animations
    - Animate node expansion/collapse
    - Add transitions for panel open/close
    - Implement smooth zoom and pan
    - _Requirements: 4.3, 11.2_
    - **Test**: Expand node - smooth animation. Open side panel - slides in smoothly. Zoom/pan - no jank. All animations 60 FPS. Transitions feel natural (200-300ms duration).
  
  - [ ] 19.3 Implement loading states
    - Add spinners for API calls
    - Show progress bars for long operations
    - Display skeleton screens while loading
    - _Requirements: 11.4, 12.2_
    - **Test**: Submit text - spinner shows during processing. Long operation - progress bar updates. Initial load - skeleton screens appear. No blank screens. Loading states clear and informative.
  
  - [ ] 19.4 Make responsive design
    - Test on desktop and tablet sizes
    - Adjust layout for different screen sizes
    - Ensure touch-friendly interactions
    - _Requirements: 11.5_
    - **Test**: Resize browser from 1920px to 768px. Layout adapts smoothly. Test on tablet - touch interactions work. Buttons large enough for touch. No horizontal scroll. Side panel adapts to screen size.
  
  - [ ] 19.5 Add accessibility features
    - Implement keyboard navigation
    - Add ARIA labels for screen readers
    - Ensure color contrast ratios
    - Add focus indicators
    - _Requirements: 11.1_
    - **Test**: Navigate with Tab key - logical order. Press Enter on node - selects it. Screen reader announces elements correctly. Check contrast ratios with tool (WCAG AA). Focus indicators visible. Keyboard shortcuts documented.

- [ ] 20. Final integration and testing
  - [ ] 20.1 Perform end-to-end testing
    - Test complete user workflows
    - Verify all requirements are met
    - Test error scenarios
    - _Requirements: All_
    - **Test**: Complete full workflow: paste text → generate graph → expand nodes → ask questions → get explanations → play audio. Test error scenarios: invalid input, network failures, service outages. Verify all 17 requirements met. Create test checklist and verify each item.
  
  - [ ] 20.2 Performance testing
    - Test with large texts (50k chars)
    - Test with large graphs (1000+ nodes)
    - Verify response time requirements
    - Test concurrent user sessions
    - _Requirements: 12.1-12.10_
    - **Test**: Submit 50k char text - processes within time limit. Load 1000 node graph - renders smoothly. Measure response times: text processing <10s, node expansion <2s, relationships <3s, Q&A <5s, TTS <2s. Simulate 10 concurrent users - no degradation.
  
  - [ ] 20.3 Security audit
    - Review input validation
    - Test for XSS and injection vulnerabilities
    - Verify CORS and authentication
    - _Requirements: 15.1-15.8_
    - **Test**: Run security scanner (e.g., OWASP ZAP). Test XSS payloads - all blocked. Test SQL injection - prevented. Verify HTTPS enforced. Check authentication tokens secure. Review logs for sensitive data leaks. No critical vulnerabilities.
  
  - [ ] 20.4 Final polish and bug fixes
    - Fix any remaining bugs
    - Optimize performance bottlenecks
    - Improve error messages
    - _Requirements: All_
    - **Test**: Review bug tracker - all critical bugs fixed. Test all features one final time. Error messages clear and helpful. Performance meets requirements. UI polished. Code reviewed. Ready for demo/deployment.
