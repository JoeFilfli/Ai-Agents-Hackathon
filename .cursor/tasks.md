# Lean Hackathon Implementation Plan

**Goal**: Build a demo-ready interactive mindmap system in 2-3 days that maximizes originality, polish, and presentation impact.

**Philosophy**: Core features first, stretch goals if time permits. Focus on what judges will see in the demo.

---

## Core Tasks (Must Have for Demo)

### Phase 1: Setup & Backend Foundation (Day 1 Morning)

- [x] 1. Project setup
  - Install minimal dependencies: `openai`, `networkx`, `fastapi`, `uvicorn`
  - Update package.json: add `cytoscape` for graph visualization
  - Create .env.local with OPENAI_API_KEY
  - _Test_: Run `pip install -r requirements.txt` and `npm install`. Test OpenAI connection with simple API call.

- [x] 2. Core data models
  - Create api/models/graph_models.py with Node, Edge, Graph Pydantic models
  - Create app/types/graph.ts with TypeScript interfaces
  - _Test_: Import models, create sample instances, verify TypeScript compiles.

### Phase 2: Text-to-Graph Pipeline (Day 1 Afternoon)

- [x] 3. Implement GPT-4 concept extraction
  - Create api/services/text_processing.py
  - Use GPT-4 with prompt: "Extract key concepts as JSON: {concepts: [{name, description, importance}]}"
  - Basic input validation (100-50k chars)
  - _Test_: Process sample text about "machine learning". Verify returns concepts with names and descriptions.

- [x] 4. Implement GPT-4 relationship extraction
  - Add relationship extraction to text_processing.py
  - Use GPT-4 prompt: "Identify relationships as JSON: {relationships: [{source, target, type, strength}]}"
  - _Test_: Process text "Python is a programming language". Verify extracts (Python, is-a, programming language).

- [x] 5. Generate OpenAI embeddings
  - Add embedding generation using text-embedding-3-small
  - Store embeddings with each node
  - _Test_: Generate embeddings for 2 concepts. Verify 1536-dim vectors. Check similar concepts have high cosine similarity.

- [x] 6. Create text processing API endpoint
  - Add POST /api/py/text/process endpoint
  - Integrate concept extraction, relationships, embeddings
  - Return graph_id, nodes, edges
  - _Test_: POST sample text via curl. Verify returns structured graph data. Check logs show processing.

### Phase 3: Graph Service (Day 1 Evening)

- [x] 7. Build NetworkX graph service
  - Create api/services/graph_service.py with GraphBuilder
  - Build NetworkX graph from nodes/edges
  - Store graphs in-memory with dict (graph_id -> Graph)
  - _Test_: Create graph with 10 nodes. Verify NetworkX graph has correct structure.

- [x] 8. Implement graph traversal
  - Add BFS, DFS, shortest path methods
  - Implement subgraph extraction for node expansion
  - Find paths up to 3 hops for relationship explanations
  - _Test_: Create graph A->B->C->D. BFS from A returns [A,B,C,D]. Expand B returns subgraph.

- [x] 9. Create graph API endpoints
  - GET /api/py/graph/{graph_id} - retrieve graph
  - POST /api/py/graph/{graph_id}/expand/{node_id} - expand node
  - POST /api/py/graph/{graph_id}/relationships/{node_id} - get relationship paths
  - _Test_: Use curl to test all endpoints. Verify correct responses.

### Phase 4: LLM Integration (Day 2 Morning)

- [x] 10. Implement relationship explanation
  - Create api/services/llm_service.py
  - Build prompts with graph context (node + connected nodes + paths)
  - Use GPT-4 to generate natural language explanations
  - _Test_: Request explanation for node with 3 connections. Verify explanation mentions all related nodes.

- [x] 11. Implement Q&A functionality
  - Add Q&A method with conversation history
  - Include graph context (node + 2-hop neighbors)
  - Return answers with citations
  - _Test_: Ask "What is this?" about a node. Verify answer uses node content. Ask follow-up - uses history.

- [x] 12. Create LLM API endpoints
  - POST /api/py/llm/explain - generate relationship explanation
  - POST /api/py/llm/qa - answer questions about nodes
  - _Test_: POST to both endpoints via curl. Verify structured responses with explanations/answers.

### Phase 5: Frontend Visualization (Day 2 Afternoon)

- [ ] 13. Set up state management
  - Create app/store/graphStore.ts with Zustand
  - Define GraphState (nodes, edges, selectedNode)
  - Define UIState (sidePanelOpen, loading)
  - _Test_: Import store, update state, verify changes propagate.

- [ ] 14. Build Cytoscape.js graph renderer
  - Create app/components/Mindmap.tsx
  - Render nodes and edges from state
  - Implement pan and zoom
  - Use force-directed layout
  - _Test_: Load sample graph. Verify nodes/edges render. Pan and zoom work smoothly.

- [ ] 15. Implement node interactions
  - Click to select node
  - Double-click to expand/collapse
  - Hover to highlight connections
  - Visual highlighting for selected nodes
  - _Test_: Click node - selects and highlights. Double-click - expands. Hover - connections highlight.

- [ ] 16. Create main page with text input
  - Replace app/page.tsx with mindmap interface
  - Add textarea for text input
  - Validate length, call /api/py/text/process
  - Show loading spinner, then display graph
  - _Test_: Paste text, submit. Loading appears. Graph displays after processing.

### Phase 6: Side Panel & Features (Day 2 Evening)

- [ ] 17. Build side panel layout
  - Create app/components/SidePanel.tsx with tabs
  - Tabs: Details, Relationships, Q&A
  - Smooth open/close animation
  - _Test_: Select node. Panel opens. Switch tabs. Close panel.

- [ ] 18. Implement Details tab
  - Show node label, description, source text
  - Display confidence/importance score
  - _Test_: Select node. Details tab shows all node information clearly.

- [ ] 19. Implement Relationships tab
  - Button to "Explain Relationships"
  - Call /api/py/llm/explain endpoint
  - Display explanation text
  - Highlight related nodes on graph
  - _Test_: Click explain button. Explanation appears. Related nodes highlight on graph.

- [ ] 20. Implement Q&A tab
  - Input field for questions
  - Display conversation history
  - Call /api/py/llm/qa endpoint
  - Show answers with formatting
  - _Test_: Type question, submit. Answer appears. Ask follow-up - maintains context.

### Phase 7: Voice-Over (Day 3 Morning)

- [ ] 21. Implement OpenAI TTS
  - Create api/services/tts_service.py
  - Use OpenAI TTS API (tts-1 model, alloy voice)
  - Save audio to public/audio/ directory
  - Return audio URL
  - _Test_: Generate audio for "Hello world". Verify MP3 file created and playable.

- [ ] 22. Create TTS API endpoint
  - POST /api/py/tts/synthesize
  - Accept text, return audio_url
  - _Test_: POST text via curl. Verify returns URL. Access URL - audio plays.

- [ ] 23. Add audio player to frontend
  - Create audio player component
  - Auto-play when explanation generated
  - Play/pause/stop controls
  - Stop audio when new node selected
  - _Test_: Click node - audio plays automatically. Controls work. Select new node - audio switches.

### Phase 8: Polish & Demo Prep (Day 3 Afternoon)

- [ ] 24. Apply consistent styling
  - Use TailwindCSS throughout
  - Define color palette (modern, clean)
  - Consistent spacing and typography
  - _Test_: Review all pages. Consistent look and feel. Professional appearance.

- [ ] 25. Add smooth animations
  - Node expansion animation
  - Panel slide-in/out
  - Smooth zoom/pan transitions
  - _Test_: All animations smooth at 60 FPS. No jank.

- [ ] 26. Add loading states
  - Spinner during graph generation
  - Loading indicators for API calls
  - Progress feedback for long operations
  - _Test_: All async operations show loading state. User never confused about what's happening.

- [ ] 27. Basic error handling
  - User-friendly error messages
  - Handle API failures gracefully
  - Input validation with helpful messages
  - _Test_: Test with invalid input. Error messages clear and helpful. No crashes.

- [ ] 28. Create minimal Docker setup
  - Write Dockerfile (Next.js + FastAPI only)
  - Create docker-compose.yml (app service only)
  - _Test_: Run `docker-compose up`. App starts. Test full workflow in container.

- [ ] 29. Write README with setup instructions
  - Project overview and features
  - Quick start: install dependencies, set OPENAI_API_KEY, run
  - Docker instructions
  - _Test_: Follow README on clean machine. Can run project successfully.

## Testing Strategy (Minimal)

**Smoke Tests Only** - No comprehensive test suite needed for hackathon:
- Manual testing of each feature as you build it
- End-to-end test: paste text → generate graph → expand node → ask question → play audio
- Test with 2-3 different text samples (different topics)
- Test error cases: empty input, very long input, API failures
- Final run-through before demo


## Success Criteria

✅ **Core Demo Flow Works**:
1. User pastes text
2. Graph generates and displays beautifully
3. User clicks node → side panel opens
4. User expands node → subnodes appear
5. User clicks "Explain Relationships" → explanation appears + audio plays
6. User asks question → gets intelligent answer
7. Everything looks polished and professional

**Result**: Lean, focused implementation that delivers maximum demo impact with minimum complexity. Perfect for a 2-3 day hackathon sprint! 🚀
