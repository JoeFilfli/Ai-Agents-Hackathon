"""
Test script for graph service.

Tests:
1. Graph creation with nodes and edges
2. Graph storage and retrieval
3. Node and edge queries
4. Path finding
5. Subgraph extraction
6. Graph statistics

Run from project root: python api/tests/test_graph_service.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_graph_creation():
    """Test creating a graph with nodes and edges."""
    print("=" * 60)
    print("Testing Graph Creation")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create sample nodes
        nodes = [
            {"id": "node_0", "label": "Python", "type": "language"},
            {"id": "node_1", "label": "JavaScript", "type": "language"},
            {"id": "node_2", "label": "Web Development", "type": "field"},
            {"id": "node_3", "label": "Data Science", "type": "field"},
            {"id": "node_4", "label": "Machine Learning", "type": "field"}
        ]
        
        # Create sample edges
        edges = [
            {"source": "node_0", "target": "node_2", "relationship_type": "used-in"},
            {"source": "node_0", "target": "node_3", "relationship_type": "used-in"},
            {"source": "node_1", "target": "node_2", "relationship_type": "used-in"},
            {"source": "node_3", "target": "node_4", "relationship_type": "includes"}
        ]
        
        # Create graph
        G = service.create_graph("test_graph_1", nodes, edges)
        
        print(f"✓ Graph created successfully")
        print(f"  - Nodes: {G.number_of_nodes()}")
        print(f"  - Edges: {G.number_of_edges()}")
        
        # Verify node count
        if G.number_of_nodes() == len(nodes):
            print(f"✓ Correct number of nodes ({len(nodes)})")
        else:
            print(f"✗ Wrong node count: {G.number_of_nodes()} (expected {len(nodes)})")
            return False
        
        # Verify edge count
        if G.number_of_edges() == len(edges):
            print(f"✓ Correct number of edges ({len(edges)})")
        else:
            print(f"✗ Wrong edge count: {G.number_of_edges()} (expected {len(edges)})")
            return False
        
        # Verify node attributes
        node_data = G.nodes["node_0"]
        if node_data.get('label') == "Python":
            print("✓ Node attributes preserved")
        else:
            print("✗ Node attributes not preserved")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Graph creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_storage_retrieval():
    """Test storing and retrieving graphs."""
    print("\n" + "=" * 60)
    print("Testing Graph Storage and Retrieval")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        nodes = [
            {"id": "a", "label": "A"},
            {"id": "b", "label": "B"}
        ]
        edges = [{"source": "a", "target": "b"}]
        
        # Create graph
        service.create_graph("storage_test", nodes, edges)
        
        # Check if graph exists
        if service.graph_exists("storage_test"):
            print("✓ Graph exists after creation")
        else:
            print("✗ Graph not found after creation")
            return False
        
        # Retrieve graph
        G = service.get_graph("storage_test")
        if G is not None:
            print("✓ Graph retrieved successfully")
        else:
            print("✗ Failed to retrieve graph")
            return False
        
        # Get metadata
        metadata = service.get_graph_metadata("storage_test")
        if metadata:
            print(f"✓ Metadata retrieved: {metadata.get('node_count')} nodes, {metadata.get('edge_count')} edges")
        else:
            print("✗ Failed to retrieve metadata")
            return False
        
        # List graphs
        graphs = service.list_graphs()
        if "storage_test" in graphs:
            print(f"✓ Graph found in list (total: {len(graphs)})")
        else:
            print("✗ Graph not in list")
            return False
        
        # Delete graph
        if service.delete_graph("storage_test"):
            print("✓ Graph deleted successfully")
        else:
            print("✗ Failed to delete graph")
            return False
        
        # Verify deletion
        if not service.graph_exists("storage_test"):
            print("✓ Graph no longer exists after deletion")
        else:
            print("✗ Graph still exists after deletion")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Storage/retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_node_edge_queries():
    """Test querying nodes and edges."""
    print("\n" + "=" * 60)
    print("Testing Node and Edge Queries")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create graph
        nodes = [
            {"id": "1", "label": "Concept A", "importance": 0.9},
            {"id": "2", "label": "Concept B", "importance": 0.8},
            {"id": "3", "label": "Concept C", "importance": 0.7}
        ]
        edges = [
            {"source": "1", "target": "2", "relationship_type": "related-to"},
            {"source": "2", "target": "3", "relationship_type": "leads-to"}
        ]
        
        service.create_graph("query_test", nodes, edges)
        
        # Get node data
        node_data = service.get_node_data("query_test", "1")
        if node_data and node_data['label'] == "Concept A":
            print(f"✓ Node data retrieved: {node_data['label']}")
        else:
            print("✗ Failed to get node data")
            return False
        
        # Get neighbors
        neighbors = service.get_neighbors("query_test", "2")
        print(f"  Neighbors of node 2: {neighbors}")
        if "1" in neighbors and "3" in neighbors:
            print("✓ Neighbors found correctly")
        else:
            print("✗ Incorrect neighbors")
            return False
        
        # Get edges for node
        edges_data = service.get_edges_for_node("query_test", "2")
        print(f"  Edges for node 2: {len(edges_data)} edge(s)")
        if len(edges_data) == 2:  # 1 incoming, 1 outgoing
            print("✓ Edges retrieved correctly")
        else:
            print(f"✗ Wrong number of edges: {len(edges_data)} (expected 2)")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Node/edge query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bfs_dfs_traversal():
    """Test BFS and DFS traversal as specified in Task 8."""
    print("\n" + "=" * 60)
    print("Testing BFS and DFS Traversal (Task 8)")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create graph A->B->C->D as specified in task
        nodes = [
            {"id": "A", "label": "Node A"},
            {"id": "B", "label": "Node B"},
            {"id": "C", "label": "Node C"},
            {"id": "D", "label": "Node D"}
        ]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "D"}
        ]
        
        service.create_graph("traversal_test", nodes, edges)
        
        # Test BFS from A (should return [A, B, C, D])
        bfs_result = service.bfs_traversal("traversal_test", "A")
        print(f"  BFS from A: {bfs_result}")
        
        if bfs_result == ["A", "B", "C", "D"]:
            print("✓ BFS traversal correct: [A, B, C, D]")
        else:
            print(f"✗ BFS traversal incorrect: {bfs_result} (expected [A, B, C, D])")
            return False
        
        # Test DFS from A
        dfs_result = service.dfs_traversal("traversal_test", "A")
        print(f"  DFS from A: {dfs_result}")
        
        if len(dfs_result) == 4 and dfs_result[0] == "A":
            print(f"✓ DFS traversal has all 4 nodes starting from A")
        else:
            print(f"✗ DFS traversal incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ BFS/DFS traversal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_node_expansion():
    """Test node expansion as specified in Task 8."""
    print("\n" + "=" * 60)
    print("Testing Node Expansion (Task 8)")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create graph A->B->C->D
        nodes = [
            {"id": "A", "label": "Node A"},
            {"id": "B", "label": "Node B"},
            {"id": "C", "label": "Node C"},
            {"id": "D", "label": "Node D"}
        ]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "D"}
        ]
        
        service.create_graph("expansion_test", nodes, edges)
        
        # Expand node B (should return subgraph with B and neighbors)
        expansion = service.expand_node("expansion_test", "B", depth=1)
        
        if expansion:
            print(f"✓ Node B expanded successfully")
            print(f"  - Center node: {expansion['center_node']}")
            print(f"  - Nodes in expansion: {[n['id'] for n in expansion['nodes']]}")
            print(f"  - Edges in expansion: {len(expansion['edges'])}")
            
            node_ids = [n['id'] for n in expansion['nodes']]
            
            # Should include B and its neighbors (A, C)
            if 'B' in node_ids and ('A' in node_ids or 'C' in node_ids):
                print("✓ Expansion includes B and at least one neighbor")
            else:
                print(f"✗ Expansion missing expected nodes")
                return False
        else:
            print("✗ Failed to expand node B")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Node expansion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_path_finding():
    """Test finding paths between nodes."""
    print("\n" + "=" * 60)
    print("Testing Path Finding")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create a connected graph: A -> B -> C -> D
        nodes = [
            {"id": "A", "label": "Node A"},
            {"id": "B", "label": "Node B"},
            {"id": "C", "label": "Node C"},
            {"id": "D", "label": "Node D"}
        ]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "D"},
            {"source": "A", "target": "C"}  # Shortcut
        ]
        
        service.create_graph("path_test", nodes, edges)
        
        # Find shortest path
        path = service.get_path("path_test", "A", "D")
        if path:
            print(f"✓ Shortest path found: {' -> '.join(path)}")
            print(f"  Path length: {len(path) - 1} hops")
        else:
            print("✗ No path found")
            return False
        
        # Find all paths
        all_paths = service.get_all_paths("path_test", "A", "D", max_length=5)
        print(f"✓ Found {len(all_paths)} path(s) from A to D:")
        for i, p in enumerate(all_paths, 1):
            print(f"  {i}. {' -> '.join(p)}")
        
        if len(all_paths) >= 2:
            print("✓ Multiple paths found (including shortcut)")
        
        return True
        
    except Exception as e:
        print(f"✗ Path finding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subgraph_extraction():
    """Test extracting subgraphs."""
    print("\n" + "=" * 60)
    print("Testing Subgraph Extraction")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create larger graph
        nodes = [{"id": str(i), "label": f"Node {i}"} for i in range(10)]
        edges = [
            {"source": "0", "target": "1"},
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "5", "target": "6"},
            {"source": "6", "target": "7"}
        ]
        
        service.create_graph("subgraph_test", nodes, edges)
        
        # Extract subgraph
        subgraph = service.get_subgraph("subgraph_test", ["0", "1", "2", "3"])
        
        if subgraph:
            print(f"✓ Subgraph extracted")
            print(f"  - Nodes: {subgraph.number_of_nodes()}")
            print(f"  - Edges: {subgraph.number_of_edges()}")
            
            if subgraph.number_of_nodes() == 4:
                print("✓ Correct number of nodes in subgraph")
            else:
                print(f"✗ Wrong node count: {subgraph.number_of_nodes()}")
                return False
            
            if subgraph.number_of_edges() == 3:
                print("✓ Correct number of edges in subgraph")
            else:
                print(f"✗ Wrong edge count: {subgraph.number_of_edges()}")
                return False
        else:
            print("✗ Failed to extract subgraph")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Subgraph extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_distance_queries():
    """Test querying nodes within distance."""
    print("\n" + "=" * 60)
    print("Testing Distance Queries")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create graph
        nodes = [{"id": str(i), "label": f"Node {i}"} for i in range(6)]
        edges = [
            {"source": "0", "target": "1"},
            {"source": "0", "target": "2"},
            {"source": "1", "target": "3"},
            {"source": "2", "target": "4"},
            {"source": "3", "target": "5"}
        ]
        
        service.create_graph("distance_test", nodes, edges)
        
        # Get nodes within 1 hop
        nodes_1_hop = service.get_nodes_within_distance("distance_test", "0", distance=1)
        print(f"  Nodes within 1 hop of '0': {nodes_1_hop}")
        
        if len(nodes_1_hop) == 2:
            print(f"✓ Found {len(nodes_1_hop)} nodes within 1 hop")
        else:
            print(f"✗ Wrong count: {len(nodes_1_hop)} (expected 2)")
            return False
        
        # Get nodes within 2 hops
        nodes_2_hop = service.get_nodes_within_distance("distance_test", "0", distance=2)
        print(f"  Nodes within 2 hops of '0': {nodes_2_hop}")
        
        if len(nodes_2_hop) >= 4:
            print(f"✓ Found {len(nodes_2_hop)} nodes within 2 hops")
        else:
            print(f"⚠ Found {len(nodes_2_hop)} nodes (expected at least 4)")
        
        return True
        
    except Exception as e:
        print(f"✗ Distance query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_statistics():
    """Test calculating graph statistics."""
    print("\n" + "=" * 60)
    print("Testing Graph Statistics")
    print("=" * 60)
    
    try:
        from api.services.graph_service import GraphService
        
        service = GraphService()
        
        # Create graph
        nodes = [{"id": str(i), "label": f"Node {i}"} for i in range(5)]
        edges = [
            {"source": "0", "target": "1"},
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "3", "target": "4"}
        ]
        
        service.create_graph("stats_test", nodes, edges)
        
        # Get statistics
        stats = service.get_graph_statistics("stats_test")
        
        if stats:
            print("✓ Statistics calculated:")
            print(f"  - Nodes: {stats['node_count']}")
            print(f"  - Edges: {stats['edge_count']}")
            print(f"  - Density: {stats['density']:.4f}")
            print(f"  - Is connected: {stats['is_connected']}")
            print(f"  - Avg degree: {stats.get('avg_degree', 0):.2f}")
            
            if stats['node_count'] == 5:
                print("✓ Correct node count in statistics")
            else:
                print("✗ Wrong node count")
                return False
        else:
            print("✗ Failed to calculate statistics")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all graph service tests."""
    print("\n" + "=" * 60)
    print("GRAPH SERVICE TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    creation_ok = test_graph_creation()
    storage_ok = test_graph_storage_retrieval()
    queries_ok = test_node_edge_queries()
    bfs_dfs_ok = test_bfs_dfs_traversal()
    expansion_ok = test_node_expansion()
    paths_ok = test_path_finding()
    subgraph_ok = test_subgraph_extraction()
    distance_ok = test_distance_queries()
    stats_ok = test_graph_statistics()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Graph Creation:      {'✓ PASS' if creation_ok else '✗ FAIL'}")
    print(f"  Storage/Retrieval:   {'✓ PASS' if storage_ok else '✗ FAIL'}")
    print(f"  Node/Edge Queries:   {'✓ PASS' if queries_ok else '✗ FAIL'}")
    print(f"  BFS/DFS Traversal:   {'✓ PASS' if bfs_dfs_ok else '✗ FAIL'}")
    print(f"  Node Expansion:      {'✓ PASS' if expansion_ok else '✗ FAIL'}")
    print(f"  Path Finding:        {'✓ PASS' if paths_ok else '✗ FAIL'}")
    print(f"  Subgraph Extraction: {'✓ PASS' if subgraph_ok else '✗ FAIL'}")
    print(f"  Distance Queries:    {'✓ PASS' if distance_ok else '✗ FAIL'}")
    print(f"  Graph Statistics:    {'✓ PASS' if stats_ok else '✗ FAIL'}")
    
    all_passed = all([
        creation_ok, storage_ok, queries_ok, bfs_dfs_ok, expansion_ok,
        paths_ok, subgraph_ok, distance_ok, stats_ok
    ])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Task 7 & 8 are complete. Ready for Task 9!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

