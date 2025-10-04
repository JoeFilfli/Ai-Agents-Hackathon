# Components

This directory contains React components for the Interactive Mindmap application.

## Mindmap Component

### `Mindmap.tsx`

The main graph visualization component built with Cytoscape.js.

**Features:**
- ✅ Interactive graph rendering
- ✅ Force-directed layout (fcose)
- ✅ Pan and zoom controls
- ✅ Node selection (click to select)
- ✅ Node expansion (double-click to expand)
- ✅ Hover to highlight connections
- ✅ Visual connection highlighting
- ✅ Dimming of unconnected nodes
- ✅ Node highlighting (programmatic)
- ✅ Smooth animations
- ✅ Empty state display
- ✅ Node/edge count display
- ✅ Control buttons (zoom in/out, fit, reset)

**Props:**
```typescript
interface MindmapProps {
  width?: string | number;   // Default: '100%'
  height?: string | number;  // Default: '100%'
  className?: string;        // Optional CSS class
}
```

**Usage:**
```typescript
import Mindmap from '@/app/components/Mindmap';

function MyPage() {
  return (
    <div style={{ height: '100vh' }}>
      <Mindmap />
    </div>
  );
}
```

**State Integration:**
The component automatically syncs with the Zustand store:
- Reads `nodes` and `edges` from store
- Updates when graph data changes
- Handles node selection via `selectNode` action
- Responds to `highlightedNodeIds` changes

**Styling:**
- Nodes: Blue circles with labels (#4F46E5)
- Selected nodes: Red highlight (#DC2626)
- Hovered nodes: Purple highlight (#8B5CF6)
- Connected nodes: Green highlight (#10B981)
- Highlighted nodes: Orange highlight (#F59E0B)
- Dimmed nodes: 30% opacity (when not connected)
- Edges: Gray arrows with relationship type labels (#9CA3AF)
- Connected edges: Green arrows (#10B981)
- Dimmed edges: 20% opacity
- Background: Light gray (#F9FAFB)

**Controls:**
- **Pan**: Click and drag on empty space
- **Zoom**: Mouse wheel or +/− buttons
- **Select**: Single click on any node (turns red)
- **Expand**: Double-click on any node (bounce animation)
- **Hover**: Move mouse over node to highlight connections (purple/green)
- **Deselect**: Click on empty space
- **Fit View**: Click ⊡ button to fit all nodes in view
- **Reset Layout**: Click ↻ button to recalculate positions

**Layout Algorithm:**
Uses Cytoscape's fcose (fast Compound Spring Embedder):
- Force-directed positioning
- Automatic edge length optimization
- Collision avoidance
- Smooth animations during layout

**Performance:**
- Handles graphs with 100+ nodes smoothly
- Efficient re-rendering (only updates when needed)
- Optimized layout calculations
- GPU-accelerated rendering via Cytoscape

## Testing

Visit the test page to verify functionality:
```
http://localhost:3000/test-mindmap
```

The test page includes:
- Sample graph with 5 nodes and 4 edges
- Buttons to test all features
- Interactive controls
- Visual checklist

**Test Checklist:**
1. Load sample graph - nodes and edges appear
2. Pan by dragging background
3. Zoom with mouse wheel
4. Click zoom controls (+, −, ⊡, ↻)
5. **Single click** node to select (turns red)
6. **Double-click** node to expand (bounce animation)
7. **Hover** over node (turns purple, connected nodes turn green)
8. **Move mouse away** from node (highlights clear)
9. **Hover different nodes** to see different connections
10. Highlight nodes programmatically (turns orange)
11. Clear highlights
12. Fit to view
13. Reset layout (recalculates positions)
14. Clear graph (shows empty state)

## Integration Example

Complete integration with store and API:

```typescript
'use client';

import { useState } from 'react';
import Mindmap from '@/app/components/Mindmap';
import { useMindmapStore } from '@/app/store/graphStore';

export default function GraphPage() {
  const { setGraph, setProcessingText } = useMindmapStore();
  const [text, setText] = useState('');

  const processText = async () => {
    setProcessingText(true);
    
    try {
      const response = await fetch('/api/py/text/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text,
          min_importance: 0.0,  // 0.0 = LLM decides (unlimited concepts)
          min_strength: 0.0,    // 0.0 = keep all relationships
          extract_relationships: true,
          generate_embeddings: true
        }),
      });
      
      const data = await response.json();
      setGraph(data.graph_id, data.nodes, data.edges);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setProcessingText(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{ padding: '1rem' }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to analyze..."
          style={{ width: '100%', height: '100px', padding: '0.5rem' }}
        />
        <button onClick={processText}>Generate Graph</button>
      </div>
      
      <div style={{ flex: 1, padding: '1rem' }}>
        <Mindmap />
      </div>
    </div>
  );
}
```

## Customization

### Custom Styling

Override node/edge styles:
```typescript
// In Mindmap.tsx, modify the style array:
{
  selector: 'node',
  style: {
    'background-color': '#YOUR_COLOR',
    'font-size': '14px',
    // ... other styles
  }
}
```

### Layout Options

Adjust layout parameters:
```typescript
cy.layout({
  name: 'fcose',
  idealEdgeLength: 200,  // Increase for more spacing
  nodeRepulsion: 8000,   // Increase to push nodes apart
  gravity: 0.1,          // Lower for looser layout
  // ... other options
}).run();
```

### Alternative Layouts

Cytoscape supports multiple layouts:
- `fcose` - Force-directed (default)
- `cose` - Compound spring embedder
- `circle` - Circular arrangement
- `grid` - Grid arrangement
- `breadthfirst` - Hierarchical tree
- `concentric` - Concentric circles

## Dependencies

- `cytoscape`: ^3.30.2
- `cytoscape-fcose`: ^2.2.0
- `react`: ^18.0.0
- `zustand`: ^5.0.1

## Future Enhancements

Planned features:
- [ ] Node expansion animation
- [ ] Minimap for navigation
- [ ] Custom node shapes
- [ ] Edge bundling for dense graphs
- [ ] Export to image (PNG/SVG)
- [ ] Graph search/filter
- [ ] Multiple selection
- [ ] Node grouping/clustering

