# TypeScript Type Definitions

This directory contains TypeScript type definitions for the mindmap system.

## Files

### `graph.ts`
Core type definitions for the graph data structures and API contracts.

**Exported Types:**
- `Node` - Concept node in the knowledge graph
- `Edge` - Relationship between two nodes
- `Graph` - Complete knowledge graph structure
- `TextProcessRequest/Response` - Text processing API
- `NodeExpansionResponse` - Node expansion API
- `RelationshipExplanationResponse` - Relationship explanation API
- `QARequest/Response` - Q&A functionality API
- `APIError` - Error response structure

### `graph.test.ts`
Test file to verify all types compile correctly.

## Testing

### Check TypeScript Compilation

To verify all types are correct and there are no type errors:

```bash
npx tsc --noEmit
```

This will:
- ✓ Check all TypeScript files compile
- ✓ Verify type definitions are correct
- ✓ Ensure no type errors exist

### Run Type Tests

The `graph.test.ts` file includes:
- Sample instances of all types
- Type inference checks
- Function type checking
- Optional field handling

## Usage Example

```typescript
import type { Node, Edge, Graph } from './types/graph';

// Create a node
const node: Node = {
  id: 'node_1',
  label: 'Machine Learning',
  description: 'A field of AI...',
  sourceText: 'ML is...',
  confidence: 0.95,
  metadata: {},
  hasChildren: true
};

// Create an edge
const edge: Edge = {
  id: 'edge_1',
  source: 'node_1',
  target: 'node_2',
  relationshipType: 'related-to',
  weight: 0.8,
  confidence: 0.9,
  metadata: {}
};

// Create a graph
const graph: Graph = {
  graphId: 'graph_1',
  nodes: [node],
  edges: [edge],
  metadata: { title: 'My Graph' }
};
```

## API Request Examples

### Text Processing
```typescript
const request: TextProcessRequest = {
  text: 'Your text here...',
  options: {
    maxNodes: 10,
    minConfidence: 0.7
  }
};
```

### Q&A
```typescript
const qaRequest: QARequest = {
  question: 'What is this concept?',
  history: [
    { role: 'user', content: 'Previous question' },
    { role: 'assistant', content: 'Previous answer' }
  ],
  contextDepth: 2
};
```

