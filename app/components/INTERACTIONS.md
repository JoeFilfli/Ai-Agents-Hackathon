# Node Interactions (Task 15)

This document describes the interactive features implemented in the Mindmap component.

## Interactive Features

### 1. Single Click - Node Selection

**Behavior:**
- Click any node to select it
- Selected node turns red (#DC2626)
- Previously selected node is deselected
- Clicking empty space deselects all nodes

**Visual Feedback:**
- Red background color
- Red border (3px wide)
- Smooth camera pan to center the selected node

**Use Cases:**
- Select a node to view details
- Prepare for expansion
- Focus attention on specific concept

### 2. Double Click - Node Expansion

**Behavior:**
- Double-click any node to expand it
- Node bounces with animation (60px → 80px → 60px)
- Calls `handleNodeExpand(nodeId)` function
- Sets `expandingNode` loading state
- Console logs expansion intent

**Visual Feedback:**
- Bounce animation (400ms total)
- First grow to 80px (200ms)
- Then shrink back to 60px (200ms)

**Implementation Status:**
- ✅ Animation working
- ✅ Handler called
- ⏳ API integration (placeholder - to be implemented)

**Future Enhancement:**
```typescript
// Will call API endpoint:
const response = await fetch(`/api/py/graph/${graphId}/expand/${nodeId}`, {
  method: 'POST',
  body: JSON.stringify({ depth: 1 })
});

// Add returned nodes and edges to the graph
addNodes(response.nodes);
addEdges(response.edges);
```

### 3. Hover - Connection Highlighting

**Behavior:**
- Hover over any node to highlight its connections
- Hovered node turns purple
- Connected nodes turn green
- Connected edges turn green and thicker
- All other nodes/edges dim (30% and 20% opacity)
- Move mouse away to clear highlights

**Visual Feedback:**
- **Hovered node**: Purple (#8B5CF6) with purple border
- **Connected nodes**: Green (#10B981) with green border
- **Connected edges**: Green (#10B981), 3px wide
- **Dimmed nodes**: 30% opacity
- **Dimmed edges**: 20% opacity

**Use Cases:**
- Quickly see relationships
- Understand graph structure
- Identify connected concepts
- Visual exploration without selection

### 4. Programmatic Highlighting

**Behavior:**
- Call `highlightNodes([nodeIds])` from store
- Specified nodes turn orange
- Remains highlighted until cleared
- Independent of hover/selection state

**Visual Feedback:**
- Orange background (#F59E0B)
- Orange border (#FBBF24)
- 3px border width

**Use Cases:**
- Highlight search results
- Show path between nodes
- Mark nodes in Q&A answers
- Visual feedback for operations

## Color Scheme

| State | Color | Hex | Border |
|-------|-------|-----|--------|
| Normal | Blue | #4F46E5 | #6366F1 |
| Selected | Red | #DC2626 | #EF4444 |
| Hovered | Purple | #8B5CF6 | #A78BFA |
| Connected | Green | #10B981 | #34D399 |
| Highlighted | Orange | #F59E0B | #FBBF24 |
| Dimmed | - | - | 30% opacity |

## Event Handlers

### Implemented Events:
```typescript
// Single click (tap)
cy.on('tap', 'node', (event) => {
  selectNode(event.target.id());
});

// Double click (dbltap)
cy.on('dbltap', 'node', async (event) => {
  await handleNodeExpand(event.target.id());
});

// Mouse over
cy.on('mouseover', 'node', (event) => {
  highlightConnections(event.target);
});

// Mouse out
cy.on('mouseout', 'node', () => {
  clearConnectionHighlights();
});

// Background click
cy.on('tap', (event) => {
  if (event.target === cy) {
    selectNode(null);
  }
});
```

## Testing

Visit `http://localhost:3000/test-mindmap` and try:

1. **Single Click Test:**
   - Click "Python" node → should turn red
   - Click "Data Science" node → Python deselects, Data Science turns red
   - Click empty space → Data Science deselects

2. **Double Click Test:**
   - Double-click any node → should bounce
   - Check console for "Expanding node: ..." message
   - Node should have animated scale effect

3. **Hover Test:**
   - Hover over "Python" node → turns purple
   - Connected nodes ("Data Science", "Web Development") turn green
   - All other nodes fade to 30% opacity
   - Move mouse away → all highlights clear
   - Repeat with different nodes to see different connections

4. **Programmatic Highlight Test:**
   - Click "Highlight Nodes" button
   - "Data Science" and "Machine Learning" turn orange
   - Orange highlight persists during hover
   - Click "Clear Highlights" to remove

## Performance Considerations

- All animations use CSS transforms (GPU-accelerated)
- Event handlers are debounced naturally by browser
- Hover state doesn't trigger store updates (local state only)
- Selection triggers single store update
- Efficient class-based styling changes

## Accessibility

- Visual feedback for all interactions
- Clear color differentiation (WCAG AA compliant)
- Keyboard support (to be added in future)
- Screen reader support (to be added in future)

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile: ⚠️ Touch events work (tap = click, no hover)

## Known Limitations

1. **Mobile hover**: No hover state on touch devices (by design)
2. **Multi-select**: Not yet implemented (future enhancement)
3. **Keyboard navigation**: Not yet implemented (future enhancement)
4. **Expansion API**: Placeholder implementation (needs backend integration)

## Future Enhancements

- [ ] Right-click context menu
- [ ] Drag nodes to reposition
- [ ] Multi-select with Ctrl+Click
- [ ] Keyboard navigation (arrow keys)
- [ ] Touch gestures (pinch to zoom)
- [ ] Node locking (prevent layout changes)
- [ ] Connection strength visualization
- [ ] Animated edge transitions

