# Graph Store (State Management)

This directory contains the Zustand store for managing the application state.

## Store Structure

### `graphStore.ts`

Main Zustand store with three main sections:

#### 1. Graph State
Manages the knowledge graph data:
- `graphId`: Current graph identifier
- `nodes`: Array of all nodes in the graph
- `edges`: Array of all edges/relationships
- `selectedNodeId`: Currently selected node
- `selectedEdgeId`: Currently selected edge
- `highlightedNodeIds`: Array of highlighted node IDs

**Actions:**
- `setGraph(graphId, nodes, edges)` - Load a complete graph
- `addNodes(nodes)` - Add new nodes to existing graph
- `addEdges(edges)` - Add new edges to existing graph
- `updateNode(nodeId, updates)` - Update specific node properties
- `clearGraph()` - Clear all graph data
- `selectNode(nodeId)` - Select a node
- `selectEdge(edgeId)` - Select an edge
- `highlightNodes(nodeIds)` - Highlight specific nodes
- `clearHighlights()` - Clear all highlights

#### 2. UI State
Manages UI component states:
- `sidePanelOpen`: Side panel visibility
- `chatPanelOpen`: Chat panel visibility
- `loading`: General loading state
- `processingText`: Text processing in progress
- `expandingNode`: Node expansion in progress
- `generatingExplanation`: Explanation generation in progress
- `error`: Error message (if any)
- `viewMode`: Current view mode ('graph' | 'list' | 'hybrid')

**Actions:**
- `setSidePanelOpen(open)` - Toggle side panel
- `setChatPanelOpen(open)` - Toggle chat panel
- `setLoading(loading)` - Set general loading state
- `setProcessingText(processing)` - Set text processing state
- `setExpandingNode(expanding)` - Set node expansion state
- `setGeneratingExplanation(generating)` - Set explanation state
- `setError(error)` - Set error message
- `setViewMode(mode)` - Change view mode
- `clearError()` - Clear error

#### 3. Conversation State
Manages Q&A conversation history:
- `messages`: Array of Q&A exchanges
- `currentQuestion`: Question currently being processed

**Actions:**
- `addMessage(message)` - Add Q&A exchange to history
- `setCurrentQuestion(question)` - Set current question
- `clearConversation()` - Clear all messages

## Usage

### Basic Usage

```typescript
import { useMindmapStore } from '@/app/store/graphStore';

function MyComponent() {
  // Get state and actions
  const { nodes, edges, setGraph, selectNode } = useMindmapStore();
  
  // Use in component
  return (
    <div>
      <p>Nodes: {nodes.length}</p>
      <button onClick={() => selectNode('node_0')}>
        Select Node
      </button>
    </div>
  );
}
```

### Optimized Selectors

Use provided selector hooks for better performance:

```typescript
import { 
  useSelectedNode, 
  useHighlightedNodes,
  useIsLoading 
} from '@/app/store/graphStore';

function NodeDetails() {
  // Only re-renders when selected node changes
  const selectedNode = useSelectedNode();
  
  if (!selectedNode) return null;
  
  return <div>{selectedNode.label}</div>;
}

function LoadingIndicator() {
  // Combines all loading states
  const isLoading = useIsLoading();
  
  return isLoading ? <Spinner /> : null;
}
```

### Subscribing to Specific State

```typescript
// Only re-render when nodes change
const nodes = useMindmapStore((state) => state.nodes);

// Only re-render when selectedNodeId changes
const selectedId = useMindmapStore((state) => state.selectedNodeId);
```

### Accessing Store Outside Components

```typescript
import { useMindmapStore } from '@/app/store/graphStore';

// Get current state
const state = useMindmapStore.getState();

// Call actions
useMindmapStore.getState().setGraph('graph_123', nodes, edges);
```

## Testing

Run the test suite to verify store functionality:

```typescript
import { runAllStoreTests } from '@/app/store/graphStore.test';

// In browser console or test file
runAllStoreTests();
```

Or test individual functions:
```typescript
import { testNodeSelection, testUIState } from '@/app/store/graphStore.test';

testNodeSelection();
testUIState();
```

## State Flow Example

```typescript
// 1. User inputs text
useMindmapStore.getState().setProcessingText(true);

// 2. API call to process text
const result = await fetch('/api/py/text/process', {...});

// 3. Store the graph
useMindmapStore.getState().setGraph(
  result.graph_id,
  result.nodes,
  result.edges
);

// 4. Clear loading state
useMindmapStore.getState().setProcessingText(false);

// 5. User clicks a node
useMindmapStore.getState().selectNode('node_0');

// 6. UI automatically updates via subscriptions
```

## Best Practices

1. **Use Selectors**: Use selector hooks (`useSelectedNode`, etc.) instead of accessing full state
2. **Granular Subscriptions**: Subscribe only to the state you need
3. **Batch Updates**: When making multiple state changes, Zustand automatically batches them
4. **Error Handling**: Always set error state and clear loading states on failures
5. **Type Safety**: TypeScript interfaces ensure type-safe state access

## Integration with Components

The store is designed to work seamlessly with the graph visualization and UI components:

- **Mindmap Component**: Reads `nodes` and `edges`, calls `selectNode` on click
- **Side Panel**: Reads `selectedNodeId` and `useSelectedNode()`
- **Text Input**: Calls `setProcessingText` and `setGraph`
- **Chat Panel**: Uses conversation state and `addMessage`
- **Loading Indicators**: Use `useIsLoading()` or specific loading states

## Performance Considerations

- Zustand is lightweight and fast
- Selector hooks prevent unnecessary re-renders
- State updates are automatically optimized
- No need for manual memoization in most cases

