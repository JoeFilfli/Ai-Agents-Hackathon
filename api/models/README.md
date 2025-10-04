# Data Models

This directory contains the Pydantic data models for the mindmap system.

## Models

### `Node`
Represents a concept in the knowledge graph.

**Key fields:**
- `id`: Unique identifier
- `label`: Short name of the concept
- `description`: Detailed explanation
- `source_text`: Original text excerpt
- `embedding`: Vector embedding (1536 dims)
- `confidence`: Extraction confidence (0-1)
- `has_children`: Whether node can be expanded

### `Edge`
Represents a relationship between two nodes.

**Key fields:**
- `id`: Unique identifier
- `source`: Source node ID
- `target`: Target node ID
- `relationship_type`: Type of relationship (e.g., "is-a", "part-of")
- `weight`: Relationship strength
- `confidence`: Relationship confidence (0-1)

### `Graph`
Represents the complete knowledge graph.

**Key fields:**
- `graph_id`: Unique identifier
- `nodes`: List of Node objects
- `edges`: List of Edge objects
- `metadata`: Graph-level information

**Helper methods:**
- `node_count`: Property returning number of nodes
- `edge_count`: Property returning number of edges
- `get_node_by_id(node_id)`: Find a node by ID
- `get_edges_for_node(node_id)`: Get all edges for a node

## Usage Example

```python
from api.models import Node, Edge, Graph

# Create a node
node = Node(
    id="node_1",
    label="Python",
    description="A high-level programming language",
    source_text="Python is used for web development...",
    confidence=0.95
)

# Create an edge
edge = Edge(
    id="edge_1",
    source="node_1",
    target="node_2",
    relationship_type="related-to",
    weight=0.8
)

# Create a graph
graph = Graph(
    graph_id="graph_1",
    nodes=[node],
    edges=[edge],
    metadata={"title": "Programming Concepts"}
)

# Access properties
print(f"Graph has {graph.node_count} nodes")

# Use helper methods
found_node = graph.get_node_by_id("node_1")
```

