"""
Test script to verify data models are correctly defined and functional.

This tests:
1. Python Pydantic models can be imported
2. Sample instances can be created
3. Validation works correctly
4. Serialization to JSON works

Run from project root: python -m api.tests.test_models
Or from anywhere: python api/tests/test_models.py
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all models can be imported."""
    print("=" * 60)
    print("Testing Model Imports")
    print("=" * 60)
    
    try:
        from api.models.graph_models import Node, Edge, Graph
        print("✓ Successfully imported Node, Edge, Graph from api.models")
        return True
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False


def test_node_creation():
    """Test creating Node instances."""
    print("\n" + "=" * 60)
    print("Testing Node Creation")
    print("=" * 60)
    
    try:
        from api.models.graph_models import Node
        
        # Create a simple node
        node = Node(
            id="test_node_1",
            label="Python Programming",
            description="Python is a high-level programming language",
            source_text="Python is widely used for web development and data science.",
            confidence=0.95,
            metadata={"category": "technology", "importance": "high"}
        )
        
        print(f"✓ Created node: {node.label}")
        print(f"  - ID: {node.id}")
        print(f"  - Confidence: {node.confidence}")
        print(f"  - Has children: {node.has_children}")
        
        # Test with embedding
        node_with_embedding = Node(
            id="test_node_2",
            label="Machine Learning",
            description="ML is a subset of AI",
            source_text="Machine learning algorithms learn from data.",
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            confidence=0.88
        )
        
        print(f"✓ Created node with embedding: {node_with_embedding.label}")
        print(f"  - Embedding dimensions: {len(node_with_embedding.embedding)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Node creation failed: {e}")
        return False


def test_edge_creation():
    """Test creating Edge instances."""
    print("\n" + "=" * 60)
    print("Testing Edge Creation")
    print("=" * 60)
    
    try:
        from api.models.graph_models import Edge
        
        # Create an edge
        edge = Edge(
            id="test_edge_1",
            source="test_node_1",
            target="test_node_2",
            relationship_type="related-to",
            weight=0.75,
            confidence=0.9
        )
        
        print(f"✓ Created edge: {edge.source} --[{edge.relationship_type}]--> {edge.target}")
        print(f"  - Weight: {edge.weight}")
        print(f"  - Confidence: {edge.confidence}")
        
        # Test different relationship types
        edge_types = ["is-a", "part-of", "causes", "contradicts"]
        for rel_type in edge_types:
            e = Edge(
                id=f"edge_{rel_type}",
                source="node_a",
                target="node_b",
                relationship_type=rel_type,
                weight=0.8
            )
            print(f"✓ Created {rel_type} relationship")
        
        return True
        
    except Exception as e:
        print(f"✗ Edge creation failed: {e}")
        return False


def test_graph_creation():
    """Test creating Graph instances with nodes and edges."""
    print("\n" + "=" * 60)
    print("Testing Graph Creation")
    print("=" * 60)
    
    try:
        from api.models.graph_models import Node, Edge, Graph
        
        # Create nodes
        nodes = [
            Node(
                id="node_1",
                label="Artificial Intelligence",
                description="The simulation of human intelligence by machines",
                source_text="AI is transforming multiple industries.",
                confidence=0.95,
                has_children=True
            ),
            Node(
                id="node_2",
                label="Machine Learning",
                description="A subset of AI focused on learning from data",
                source_text="ML algorithms can improve with experience.",
                confidence=0.92,
                has_children=True
            ),
            Node(
                id="node_3",
                label="Deep Learning",
                description="ML using neural networks with multiple layers",
                source_text="Deep learning powers many modern AI applications.",
                confidence=0.90
            )
        ]
        
        # Create edges
        edges = [
            Edge(
                id="edge_1",
                source="node_1",
                target="node_2",
                relationship_type="contains",
                weight=0.9,
                confidence=0.95
            ),
            Edge(
                id="edge_2",
                source="node_2",
                target="node_3",
                relationship_type="contains",
                weight=0.85,
                confidence=0.9
            )
        ]
        
        # Create graph
        graph = Graph(
            graph_id="test_graph_1",
            nodes=nodes,
            edges=edges,
            metadata={
                "title": "AI Concepts",
                "source": "test",
                "domain": "technology"
            }
        )
        
        print(f"✓ Created graph: {graph.metadata.get('title', 'Untitled')}")
        print(f"  - Graph ID: {graph.graph_id}")
        print(f"  - Node count: {graph.node_count}")
        print(f"  - Edge count: {graph.edge_count}")
        
        # Test helper methods
        node = graph.get_node_by_id("node_2")
        if node:
            print(f"✓ Found node by ID: {node.label}")
        
        node_edges = graph.get_edges_for_node("node_2")
        print(f"✓ Found {len(node_edges)} edges for node_2")
        
        return True
        
    except Exception as e:
        print(f"✗ Graph creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_serialization():
    """Test that models can be serialized to JSON."""
    print("\n" + "=" * 60)
    print("Testing JSON Serialization")
    print("=" * 60)
    
    try:
        from api.models.graph_models import Node, Edge, Graph
        
        # Create a node
        node = Node(
            id="node_json",
            label="Test Node",
            description="A test node for JSON serialization",
            source_text="This is a test.",
            confidence=0.9
        )
        
        # Convert to JSON
        node_json = node.model_dump_json(indent=2)
        print("✓ Node serialized to JSON:")
        print(node_json[:200] + "...")
        
        # Create a small graph
        graph = Graph(
            graph_id="json_test",
            nodes=[node],
            edges=[],
            metadata={"test": True}
        )
        
        graph_json = graph.model_dump_json(indent=2)
        print("\n✓ Graph serialized to JSON:")
        print(graph_json[:200] + "...")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON serialization failed: {e}")
        return False


def test_validation():
    """Test that Pydantic validation works correctly."""
    print("\n" + "=" * 60)
    print("Testing Validation")
    print("=" * 60)
    
    try:
        from api.models.graph_models import Node
        from pydantic import ValidationError
        
        # Test valid confidence range (should work)
        try:
            node = Node(
                id="valid_node",
                label="Valid",
                description="Test",
                source_text="Test",
                confidence=0.5  # valid: between 0 and 1
            )
            print("✓ Valid confidence value accepted (0.5)")
        except ValidationError as e:
            print(f"✗ Unexpected validation error for valid data: {e}")
            return False
        
        # Test invalid confidence (should fail)
        try:
            node = Node(
                id="invalid_node",
                label="Invalid",
                description="Test",
                source_text="Test",
                confidence=1.5  # invalid: > 1.0
            )
            print("✗ Invalid confidence value was accepted (should have failed)")
            return False
        except ValidationError:
            print("✓ Invalid confidence value correctly rejected (1.5 > 1.0)")
        
        # Test missing required fields (should fail)
        try:
            node = Node(id="incomplete")  # missing required fields
            print("✗ Incomplete node was accepted (should have failed)")
            return False
        except ValidationError:
            print("✓ Missing required fields correctly rejected")
        
        return True
        
    except Exception as e:
        print(f"✗ Validation testing failed: {e}")
        return False


def main():
    """Run all model tests."""
    print("\n" + "=" * 60)
    print("DATA MODELS TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    imports_ok = test_imports()
    node_ok = test_node_creation()
    edge_ok = test_edge_creation()
    graph_ok = test_graph_creation()
    json_ok = test_json_serialization()
    validation_ok = test_validation()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Imports:        {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"  Node Creation:  {'✓ PASS' if node_ok else '✗ FAIL'}")
    print(f"  Edge Creation:  {'✓ PASS' if edge_ok else '✗ FAIL'}")
    print(f"  Graph Creation: {'✓ PASS' if graph_ok else '✗ FAIL'}")
    print(f"  JSON Serial:    {'✓ PASS' if json_ok else '✗ FAIL'}")
    print(f"  Validation:     {'✓ PASS' if validation_ok else '✗ FAIL'}")
    
    all_passed = all([
        imports_ok, node_ok, edge_ok, 
        graph_ok, json_ok, validation_ok
    ])
    
    if all_passed:
        print("\n🎉 All model tests passed!")
        print("   Task 2 is complete. Ready for Task 3!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

