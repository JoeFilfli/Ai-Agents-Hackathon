# Lean Hackathon Implementation Plan

**Goal**: Build a demo-ready interactive mindmap system in 2-3 days that maximizes originality, polish, and presentation impact.

**Philosophy**: Core features first, stretch goals if time permits. Focus on what judges will see in the demo.

---

## Core Tasks (Must Have for Demo)

### Phase 1: Setup & Backend Foundation (Day 1 Morning)

- [ ] 1. Project setup
  - Install minimal dependencies: `openai`, `networkx`, `fastapi`, `uvicorn`
  - Update package.json: add `cytoscape` for graph visualization
  - Create .env.local with OPENAI_API_KEY
  - _Test_: Run `pip install -r requirements.txt` and `npm install`. Test OpenAI connection with simple API call.

- [ ] 2. Core data models
  - Create api/models/graph_models.py with Node, Edge, Graph Pydantic models
  - Create app/types/graph.ts with TypeScript interfaces
  - _Test_: Import models, create sample instances, verify TypeScript compiles.

### Phase 2: Text-to-Graph Pipeline (Day 1 Afternoon)

- [ ] 3. Implement GPT-4 concept extraction
  - Create api/services/text_processing.py
  - Use GPT-4 with prompt: "Extract key concepts as JSON: {concepts: [{name, description, importance}]}"
  - Basic input validation (100-50k chars)
  - _Test_: Process sample text about "machine learning". Verify returns concepts with names and descriptions.

- [ ] 4. Implement GPT-4 relationship extraction
  - Add relationship extraction to text_processing.py
  - Use GPT-4 prompt: "Identify relationships as JSON: {relationships: [{source, target, type, strength}]}"
  - _Test_: Process text "Python is a programming language". Verify extracts (Python, is-a, programming language).

- [ ] 5. Generate OpenAI embeddings
  - Add embedding generation using text-embedding-3-small
  - Store embeddings with each node
  - _Test_: Generate embeddings for 2 concepts. Verify 1536-dim vectors. Check similar concepts have high cosine similarity.

- [ ] 6. Create text processing API endpoint
  - Add POST /api/py/text/process endpoint
  - Integrate concept extraction, relationships, embeddings
  - Return graph_id, nodes, edges
  - _Test_: POST sample text via curl. Verify returns structured graph data. Check logs show processing.

### Phase 3: Graph Service (Day 1 Evening)

- [ ] 7. Build NetworkX graph service
  - Create api/services/graph_service.py with GraphBuilder
  - Build NetworkX graph from nodes/edges
  - Store graphs in-memory with dict (graph_id -> Graph)
  - _Test_: Create graph with 10 nodes. Verify NetworkX graph has correct structure.

- [ ] 8. Implement graph traversal
  - Add BFS, DFS, shortest path methods
  - Implement subgraph extraction for node expansion
  - Find paths up to 3 hops for relationship explanations
  - _Test_: Create graph A->B->C->D. BFS from A returns [A,B,C,D]. Expand B returns subgraph.

- [ ] 9. Create graph API endpoints
  - GET /api/py/graph/{graph_id} - retrieve graph
  - POST /api/py/graph/{graph_id}/expand/{node_id} - expand node
  - POST /api/py/graph/{graph_id}/relationships/{node_id} - get relationship paths
  - _Test_: Use curl to test all endpoints. Verify correct responses.

### Phase 4: LLM Integration (Day 2 Morning)

- [ ] 10. Implement relationship explanation
  - Create api/services/llm_service.py
  - Build prompts with graph context (node + connected nodes + paths)
  - Use GPT-4 to generate natural language explanations
  - _Test_: Request explanation for node with 3 connections. Verify explanation mentions all related nodes.

- [ ] 11. Implement Q&A functionality
  - Add Q&A method with conversation history
  - Include graph context (node + 2-hop neighbors)
  - Return answers with citations
  - _Test_: Ask "What is this?" about a node. Verify answer uses node content. Ask follow-up - uses history.

- [ ] 12. Create LLM API endpoints
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

- [ ] 30. Record demo video
  - 3-5 minute walkthrough
  - Show: text input → graph generation → node expansion → relationships → Q&A → TTS
  - Highlight graph representation learning and originality
  - _Test_: Video is clear, covers all features, good quality. Upload and link in README.

---

## Stretch Goals (If Time Permits)

- [ ] S1. Add control panel with zoom/reset buttons
  - _Test_: Buttons work, improve UX.

- [ ] S2. Implement basic caching (in-memory dict)
  - Cache LLM responses to avoid duplicate API calls
  - _Test_: Same question twice returns instantly second time.

- [ ] S3. Add example text presets
  - Dropdown with sample texts (ML, history, science)
  - _Test_: Select preset, auto-fills textarea.

- [ ] S4. Show node count and graph stats
  - Display metadata (X nodes, Y edges)
  - _Test_: Stats update when graph changes.

- [ ] S5. Add "Similar Nodes" feature
  - Use cosine similarity on embeddings
  - Show top 3 similar nodes
  - _Test_: Click node, see similar nodes highlighted.

- [ ] S6. Improve mobile responsiveness
  - Test on tablet size
  - Adjust layout for smaller screens
  - _Test_: Works reasonably on iPad.

---

## Testing Strategy (Minimal)

**Smoke Tests Only** - No comprehensive test suite needed for hackathon:
- Manual testing of each feature as you build it
- End-to-end test: paste text → generate graph → expand node → ask question → play audio
- Test with 2-3 different text samples (different topics)
- Test error cases: empty input, very long input, API failures
- Final run-through before demo

---

## Time Estimates

**Day 1** (8 hours):
- Setup: 0.5h
- Text-to-graph pipeline: 3h
- Graph service: 2h
- LLM integration: 2h
- Buffer: 0.5h

**Day 2** (8 hours):
- Frontend visualization: 3h
- Side panel & features: 3h
- Voice-over: 1.5h
- Buffer: 0.5h

**Day 3** (6 hours):
- Polish & styling: 2h
- Error handling: 1h
- Docker setup: 1h
- README: 0.5h
- Demo video: 1h
- Final testing: 0.5h

**Total**: ~22 hours of focused work

---

## Success Criteria

✅ **Core Demo Flow Works**:
1. User pastes text
2. Graph generates and displays beautifully
3. User clicks node → side panel opens
4. User expands node → subnodes appear
5. User clicks "Explain Relationships" → explanation appears + audio plays
6. User asks question → gets intelligent answer
7. Everything looks polished and professional

✅ **Hackathon Judging Criteria Met**:
- **Originality**: Graph representation learning + LLM integration (unique approach)
- **Technical Complexity**: GPT-4 extraction, embeddings, graph traversal, TTS
- **UI/UX Polish**: Smooth animations, clean design, intuitive interactions
- **Reproducibility**: Docker setup, clear README, demo video
- **Demo Impact**: Impressive visual, clear value proposition, works reliably

---

## What We Cut (And Why It's OK)

❌ **Database persistence** - In-memory is fine for demo, graphs regenerate quickly
❌ **Redis caching** - Not needed for demo, API calls are fast enough
❌ **Clustering/Louvain** - Overkill, basic graph layout is sufficient
❌ **Advanced similarity search** - Simple embedding similarity is enough
❌ **Comprehensive testing** - Manual testing sufficient for hackathon
❌ **Security/auth** - Just sanitize input, no user accounts needed
❌ **Performance optimization** - Works fine for demo-sized graphs (<100 nodes)
❌ **Accessibility** - Nice to have, but not judging criteria
❌ **Node2Vec** - OpenAI embeddings alone are sufficient and simpler

**Result**: Lean, focused implementation that delivers maximum demo impact with minimum complexity.
