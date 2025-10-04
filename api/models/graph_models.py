"""
Graph data models for the mindmap system.

This module defines the core data structures used throughout the application:
- Node: Represents a concept in the knowledge graph
- Edge: Represents a relationship between two nodes
- Graph: Represents the complete knowledge graph structure

All models use Pydantic for validation and serialization.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Node(BaseModel):
    """
    Represents a concept node in the knowledge graph.
    
    Each node contains:
    - Basic info: id, label, description
    - Context: source_text from the original input
    - ML features: embedding vector for similarity search
    - Quality metrics: confidence score
    - Metadata: additional flexible data
    """
    
    id: str = Field(
        ..., 
        description="Unique identifier for the node"
    )
    
    label: str = Field(
        ..., 
        description="Short name or title of the concept"
    )
    
    description: str = Field(
        ..., 
        description="Detailed explanation of the concept"
    )
    
    source_text: str = Field(
        ..., 
        description="Original text excerpt this concept was extracted from"
    )
    
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding for semantic similarity (1536 dimensions for OpenAI)"
    )
    
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this concept extraction (0-1)"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional flexible metadata (position, type, etc.)"
    )
    
    has_children: bool = Field(
        default=False,
        description="Whether this node has child nodes for expansion"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when this node was created"
    )
    
    class Config:
        # Allow the model to be used with arbitrary types
        json_schema_extra = {
            "example": {
                "id": "node_1",
                "label": "Machine Learning",
                "description": "A field of AI focused on algorithms that learn from data",
                "source_text": "Machine learning is a subset of artificial intelligence...",
                "embedding": [0.1, 0.2, 0.3],  # shortened for example
                "confidence": 0.95,
                "metadata": {"importance": "high", "category": "technology"},
                "has_children": True
            }
        }


class Edge(BaseModel):
    """
    Represents a relationship between two nodes in the knowledge graph.
    
    Each edge contains:
    - Connection: source and target node IDs
    - Semantics: relationship_type describing the connection
    - Quality metrics: weight and confidence scores
    - Metadata: additional flexible data
    """
    
    id: str = Field(
        ...,
        description="Unique identifier for the edge"
    )
    
    source: str = Field(
        ...,
        description="ID of the source node"
    )
    
    target: str = Field(
        ...,
        description="ID of the target node"
    )
    
    relationship_type: str = Field(
        ...,
        description="Type of relationship (e.g., 'is-a', 'part-of', 'related-to', 'causes')"
    )
    
    weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Strength or importance of this relationship"
    )
    
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this relationship (0-1)"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional flexible metadata"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when this edge was created"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "edge_1",
                "source": "node_1",
                "target": "node_2",
                "relationship_type": "is-a",
                "weight": 0.8,
                "confidence": 0.9,
                "metadata": {"bidirectional": False}
            }
        }


class Graph(BaseModel):
    """
    Represents the complete knowledge graph structure.
    
    Contains:
    - Nodes: all concepts in the graph
    - Edges: all relationships between concepts
    - Metadata: graph-level information (title, stats, timestamps)
    """
    
    graph_id: str = Field(
        ...,
        description="Unique identifier for this graph"
    )
    
    nodes: List[Node] = Field(
        default_factory=list,
        description="List of all nodes in the graph"
    )
    
    edges: List[Edge] = Field(
        default_factory=list,
        description="List of all edges in the graph"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Graph-level metadata (title, source, statistics)"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when this graph was created"
    )
    
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when this graph was last updated"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "graph_id": "graph_123",
                "nodes": [],  # would contain Node objects
                "edges": [],  # would contain Edge objects
                "metadata": {
                    "title": "Machine Learning Concepts",
                    "node_count": 10,
                    "edge_count": 15,
                    "source": "user_input"
                }
            }
        }
    
    @property
    def node_count(self) -> int:
        """Returns the number of nodes in the graph."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Returns the number of edges in the graph."""
        return len(self.edges)
    
    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """
        Find and return a node by its ID.
        
        Args:
            node_id: The ID of the node to find
            
        Returns:
            The Node object if found, None otherwise
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_edges_for_node(self, node_id: str) -> List[Edge]:
        """
        Get all edges connected to a specific node.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            List of edges where the node is either source or target
        """
        return [
            edge for edge in self.edges 
            if edge.source == node_id or edge.target == node_id
        ]

