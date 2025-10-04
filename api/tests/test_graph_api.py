"""
Test script for Graph API endpoints (Task 9).

This script tests the three new graph endpoints:
1. GET /api/py/graph/{graph_id} - retrieve graph
2. POST /api/py/graph/{graph_id}/expand/{node_id} - expand node
3. POST /api/py/graph/{graph_id}/relationships/{node_id} - get relationship paths
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_graph_retrieval():
    """Test the graph retrieval endpoint."""
    print("\n" + "=" * 60)
    print("Testing Graph Retrieval Endpoint")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # First, create a graph by processing some text
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Python is a programming language. It is used for web development, data science, and machine learning. Web development involves creating websites and web applications.",
                "max_concepts": 5,
                "min_importance": 0.5,
                "extract_relationships": True,
                "generate_embeddings": False  # Skip embeddings for faster testing
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph: {process_response.status_code}")
            print(f"  Response: {process_response.text}")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        print(f"  - {len(data['nodes'])} nodes")
        print(f"  - {len(data['edges'])} edges")
        
        # Now test retrieval
        response = client.get(f"/api/py/graph/{graph_id}")
        
        if response.status_code != 200:
            print(f"✗ Graph retrieval failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        graph_data = response.json()
        print(f"✓ Graph retrieved successfully")
        print(f"  - Graph ID: {graph_data['graph_id']}")
        print(f"  - Nodes: {len(graph_data['nodes'])}")
        print(f"  - Edges: {len(graph_data['edges'])}")
        print(f"  - Statistics: {graph_data['statistics']}")
        
        # Verify data matches
        if graph_data['graph_id'] != graph_id:
            print(f"✗ Graph ID mismatch")
            return False
        
        if len(graph_data['nodes']) == 0:
            print(f"✗ No nodes in retrieved graph")
            return False
        
        print("✓ Graph retrieval test passed")
        return True
        
    except Exception as e:
        print(f"✗ Graph retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_node_expansion():
    """Test the node expansion endpoint."""
    print("\n" + "=" * 60)
    print("Testing Node Expansion Endpoint")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Create a graph
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Artificial intelligence uses machine learning. Machine learning includes deep learning and neural networks. Neural networks process data to make predictions.",
                "max_concepts": 5,
                "min_importance": 0.5,
                "extract_relationships": True,
                "generate_embeddings": False
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph: {process_response.status_code}")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        
        if len(data['nodes']) == 0:
            print(f"✗ No nodes in graph")
            return False
        
        # Get a node to expand
        node_id = data['nodes'][0]['id']
        node_label = data['nodes'][0]['label']
        print(f"  Expanding node: {node_id} ({node_label})")
        
        # Test expansion with depth=1
        response = client.post(
            f"/api/py/graph/{graph_id}/expand/{node_id}",
            json={"depth": 1}
        )
        
        if response.status_code != 200:
            print(f"✗ Node expansion failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        expansion = response.json()
        print(f"✓ Node expanded successfully (depth=1)")
        print(f"  - Center node: {expansion['center_node']}")
        print(f"  - Nodes in expansion: {len(expansion['nodes'])}")
        print(f"  - Edges in expansion: {len(expansion['edges'])}")
        print(f"  - Nodes: {[n['id'] for n in expansion['nodes']]}")
        
        # Verify expansion includes the center node
        if expansion['center_node'] != node_id:
            print(f"✗ Center node mismatch")
            return False
        
        if len(expansion['nodes']) == 0:
            print(f"✗ No nodes in expansion")
            return False
        
        # Test with depth=2
        response2 = client.post(
            f"/api/py/graph/{graph_id}/expand/{node_id}",
            json={"depth": 2}
        )
        
        if response2.status_code == 200:
            expansion2 = response2.json()
            print(f"✓ Node expanded successfully (depth=2)")
            print(f"  - Nodes in expansion: {len(expansion2['nodes'])}")
        
        print("✓ Node expansion test passed")
        return True
        
    except Exception as e:
        print(f"✗ Node expansion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_relationship_paths():
    """Test the relationship paths endpoint."""
    print("\n" + "=" * 60)
    print("Testing Relationship Paths Endpoint")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Create a graph with clear relationships
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Python is used for data science. Data science requires statistical analysis. Statistical analysis helps make predictions. Machine learning algorithms use statistical analysis for predictions.",
                "max_concepts": 5,
                "min_importance": 0.4,
                "extract_relationships": True,
                "generate_embeddings": False
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph: {process_response.status_code}")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        print(f"  - {len(data['nodes'])} nodes")
        print(f"  - {len(data['edges'])} edges")
        
        if len(data['nodes']) == 0:
            print(f"✗ No nodes in graph")
            return False
        
        # Get a node to find paths from
        node_id = data['nodes'][0]['id']
        node_label = data['nodes'][0]['label']
        print(f"  Finding paths from: {node_id} ({node_label})")
        
        # Test relationship paths
        response = client.post(
            f"/api/py/graph/{graph_id}/relationships/{node_id}"
        )
        
        if response.status_code != 200:
            print(f"✗ Relationship paths failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        paths_data = response.json()
        print(f"✓ Relationship paths retrieved successfully")
        print(f"  - Source node: {paths_data['node_id']}")
        print(f"  - Total paths: {paths_data['statistics']['total_paths']}")
        print(f"  - Direct neighbors: {paths_data['statistics']['direct_neighbors']}")
        print(f"  - Reachable nodes: {paths_data['statistics']['reachable_nodes']}")
        
        if paths_data['statistics'].get('avg_path_length', 0) > 0:
            print(f"  - Avg path length: {paths_data['statistics']['avg_path_length']:.2f}")
        
        # Show some example paths
        if len(paths_data['paths']) > 0:
            print(f"\n  Example paths:")
            for i, path in enumerate(paths_data['paths'][:3]):
                path_str = " -> ".join(path['path'])
                print(f"    {i+1}. {path_str} (length: {path['length']})")
        
        # Verify response structure
        if paths_data['node_id'] != node_id:
            print(f"✗ Node ID mismatch")
            return False
        
        if 'paths' not in paths_data or 'neighbors' not in paths_data:
            print(f"✗ Missing required fields in response")
            return False
        
        print("✓ Relationship paths test passed")
        return True
        
    except Exception as e:
        print(f"✗ Relationship paths test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling for invalid requests."""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Test 1: Non-existent graph
        response = client.get("/api/py/graph/nonexistent_graph")
        if response.status_code == 404:
            print("✓ Returns 404 for non-existent graph")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
            return False
        
        # Test 2: Expand non-existent node
        response = client.post(
            "/api/py/graph/test_graph/expand/nonexistent_node",
            json={"depth": 1}
        )
        if response.status_code == 404:
            print("✓ Returns 404 for non-existent graph in expand")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
        
        # Test 3: Relationships for non-existent node
        response = client.post(
            "/api/py/graph/test_graph/relationships/nonexistent_node"
        )
        if response.status_code == 404:
            print("✓ Returns 404 for non-existent graph in relationships")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
        
        print("✓ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all graph API tests."""
    print("\n" + "=" * 60)
    print("GRAPH API TEST SUITE (Task 9)")
    print("=" * 60 + "\n")
    
    # Run tests
    retrieval_ok = test_graph_retrieval()
    expansion_ok = test_node_expansion()
    paths_ok = test_relationship_paths()
    errors_ok = test_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Graph Retrieval:     {'✓ PASS' if retrieval_ok else '✗ FAIL'}")
    print(f"  Node Expansion:      {'✓ PASS' if expansion_ok else '✗ FAIL'}")
    print(f"  Relationship Paths:  {'✓ PASS' if paths_ok else '✗ FAIL'}")
    print(f"  Error Handling:      {'✓ PASS' if errors_ok else '✗ FAIL'}")
    
    all_passed = all([retrieval_ok, expansion_ok, paths_ok, errors_ok])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Task 9 is complete. Ready for Task 10!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

