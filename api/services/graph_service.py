"""
Graph Service for managing knowledge graph structures.

This service uses NetworkX to:
1. Build and store graph structures from nodes and edges
2. Perform graph traversal and analysis
3. Extract subgraphs and paths
4. Calculate graph metrics

Graphs are stored in-memory for fast access.
"""

import networkx as nx
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class GraphService:
    """
    Service for managing and analyzing knowledge graphs.
    
    Uses NetworkX for efficient graph operations and stores graphs
    in-memory for fast access.
    """
    
    def __init__(self):
        """Initialize the graph service with in-memory storage."""
        # In-memory storage: graph_id -> {graph: NetworkX graph, metadata: dict}
        self._graphs: Dict[str, Dict[str, Any]] = {}
    
    def create_graph(
        self,
        graph_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        directed: bool = True
    ) -> nx.Graph:
        """
        Create a NetworkX graph from nodes and edges.
        
        Args:
            graph_id: Unique identifier for the graph
            nodes: List of node dictionaries with 'id', 'label', etc.
            edges: List of edge dictionaries with 'source', 'target', etc.
            directed: Whether to create a directed graph (default: True)
            
        Returns:
            NetworkX graph object
            
        Raises:
            ValueError: If graph_id already exists or if data is invalid
        """
        if graph_id in self._graphs:
            raise ValueError(f"Graph with ID '{graph_id}' already exists")
        
        # Create NetworkX graph
        G = nx.DiGraph() if directed else nx.Graph()
        
        # Add nodes with attributes
        for node in nodes:
            node_id = node.get('id')
            if not node_id:
                raise ValueError("Each node must have an 'id' field")
            
            # Extract node attributes (exclude 'id' since it's the node identifier)
            attributes = {k: v for k, v in node.items() if k != 'id'}
            G.add_node(node_id, **attributes)
        
        # Add edges with attributes
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            
            if not source or not target:
                raise ValueError("Each edge must have 'source' and 'target' fields")
            
            # Check if nodes exist
            if source not in G:
                raise ValueError(f"Source node '{source}' not found in graph")
            if target not in G:
                raise ValueError(f"Target node '{target}' not found in graph")
            
            # Extract edge attributes (exclude 'source' and 'target')
            attributes = {k: v for k, v in edge.items() if k not in ['source', 'target']}
            G.add_edge(source, target, **attributes)
        
        # Store graph with metadata
        self._graphs[graph_id] = {
            'graph': G,
            'metadata': {
                'graph_id': graph_id,
                'node_count': G.number_of_nodes(),
                'edge_count': G.number_of_edges(),
                'directed': directed,
                'created_at': datetime.now().isoformat()
            }
        }
        
        return G
    
    def get_graph(self, graph_id: str) -> Optional[nx.Graph]:
        """
        Retrieve a graph by its ID.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            NetworkX graph object or None if not found
        """
        graph_data = self._graphs.get(graph_id)
        return graph_data['graph'] if graph_data else None
    
    def get_graph_metadata(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a graph.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            Metadata dictionary or None if not found
        """
        graph_data = self._graphs.get(graph_id)
        return graph_data['metadata'] if graph_data else None
    
    def graph_exists(self, graph_id: str) -> bool:
        """
        Check if a graph exists.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            True if graph exists, False otherwise
        """
        return graph_id in self._graphs
    
    def delete_graph(self, graph_id: str) -> bool:
        """
        Delete a graph from storage.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            True if graph was deleted, False if it didn't exist
        """
        if graph_id in self._graphs:
            del self._graphs[graph_id]
            return True
        return False
    
    def list_graphs(self) -> List[str]:
        """
        List all graph IDs in storage.
        
        Returns:
            List of graph IDs
        """
        return list(self._graphs.keys())
    
    def get_node(self, graph_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific node.
        
        Args:
            graph_id: Unique identifier for the graph
            node_id: Unique identifier for the node
            
        Returns:
            Node data dictionary or None if not found
        """
        G = self.get_graph(graph_id)
        if not G or node_id not in G:
            return None
        
        # Return node data with the node_id included
        node_data = dict(G.nodes[node_id])
        node_data['id'] = node_id
        return node_data
    
    def get_node_data(self, graph_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific node (alias for get_node).
        
        Args:
            graph_id: Unique identifier for the graph
            node_id: Unique identifier for the node
            
        Returns:
            Node data dictionary or None if not found
        """
        return self.get_node(graph_id, node_id)
    
    def get_all_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        """
        Get all nodes in a graph.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            List of node dictionaries
        """
        G = self.get_graph(graph_id)
        if not G:
            return []
        
        # Convert all nodes to dictionaries
        nodes = []
        for node_id in G.nodes():
            node_data = dict(G.nodes[node_id])
            node_data['id'] = node_id
            nodes.append(node_data)
        
        return nodes
    
    def get_edge(
        self,
        graph_id: str,
        source: str,
        target: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific edge.
        
        Args:
            graph_id: Unique identifier for the graph
            source: Source node ID
            target: Target node ID
            
        Returns:
            Edge data dictionary or None if not found
        """
        G = self.get_graph(graph_id)
        if not G or not G.has_edge(source, target):
            return None
        
        # Return edge data with source and target included
        edge_data = dict(G.edges[source, target])
        edge_data['source'] = source
        edge_data['target'] = target
        return edge_data
    
    def get_all_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        """
        Get all edges in a graph.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            List of edge dictionaries
        """
        G = self.get_graph(graph_id)
        if not G:
            return []
        
        # Convert all edges to dictionaries
        edges = []
        for source, target in G.edges():
            edge_data = dict(G.edges[source, target])
            edge_data['source'] = source
            edge_data['target'] = target
            edges.append(edge_data)
        
        return edges
    
    def get_neighbors(
        self,
        graph_id: str,
        node_id: str,
        direction: str = 'both'
    ) -> List[str]:
        """
        Get neighboring nodes.
        
        Args:
            graph_id: Unique identifier for the graph
            node_id: Node to get neighbors for
            direction: 'in', 'out', or 'both' (for directed graphs)
            
        Returns:
            List of neighbor node IDs
        """
        G = self.get_graph(graph_id)
        if not G or node_id not in G:
            return []
        
        if isinstance(G, nx.DiGraph):
            if direction == 'in':
                return list(G.predecessors(node_id))
            elif direction == 'out':
                return list(G.successors(node_id))
            else:  # both
                return list(set(G.predecessors(node_id)) | set(G.successors(node_id)))
        else:
            # Undirected graph
            return list(G.neighbors(node_id))
    
    def get_edges_for_node(
        self,
        graph_id: str,
        node_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all edges connected to a node.
        
        Args:
            graph_id: Unique identifier for the graph
            node_id: Node to get edges for
            
        Returns:
            List of edge dictionaries
        """
        G = self.get_graph(graph_id)
        if not G or node_id not in G:
            return []
        
        edges = []
        
        # Outgoing edges
        for target in G.successors(node_id) if isinstance(G, nx.DiGraph) else G.neighbors(node_id):
            edge_data = dict(G.edges[node_id, target])
            edge_data.update({
                'source': node_id,
                'target': target
            })
            edges.append(edge_data)
        
        # Incoming edges (for directed graphs)
        if isinstance(G, nx.DiGraph):
            for source in G.predecessors(node_id):
                edge_data = dict(G.edges[source, node_id])
                edge_data.update({
                    'source': source,
                    'target': node_id
                })
                edges.append(edge_data)
        
        return edges
    
    def get_subgraph(
        self,
        graph_id: str,
        node_ids: List[str]
    ) -> Optional[nx.Graph]:
        """
        Extract a subgraph containing specified nodes.
        
        Args:
            graph_id: Unique identifier for the graph
            node_ids: List of node IDs to include
            
        Returns:
            NetworkX subgraph or None if graph not found
        """
        G = self.get_graph(graph_id)
        if not G:
            return None
        
        # Filter node_ids to only those that exist in the graph
        valid_nodes = [nid for nid in node_ids if nid in G]
        
        if not valid_nodes:
            return None
        
        return G.subgraph(valid_nodes).copy()
    
    def expand_node(
        self,
        graph_id: str,
        node_id: str,
        depth: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Expand a node to get its local subgraph (node + neighbors).
        
        This is useful for UI node expansion - get the node and all
        connected nodes within a specified depth.
        
        Args:
            graph_id: Unique identifier for the graph
            node_id: Node to expand
            depth: How many hops to include (default: 1)
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists, or None if not found
        """
        G = self.get_graph(graph_id)
        if not G or node_id not in G:
            return None
        
        # Get all nodes within depth
        nodes_to_include = {node_id}
        nodes_to_include.update(
            self.get_nodes_within_distance(graph_id, node_id, depth)
        )
        
        # Extract subgraph
        subgraph = self.get_subgraph(graph_id, list(nodes_to_include))
        
        if not subgraph:
            return None
        
        # Convert to node/edge format
        nodes = []
        for nid in subgraph.nodes():
            node_data = dict(subgraph.nodes[nid])
            node_data['id'] = nid
            nodes.append(node_data)
        
        edges = []
        for source, target in subgraph.edges():
            edge_data = dict(subgraph.edges[source, target])
            edge_data['source'] = source
            edge_data['target'] = target
            edges.append(edge_data)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'center_node': node_id,
            'depth': depth
        }
    
    def bfs_traversal(
        self,
        graph_id: str,
        start_node: str
    ) -> List[str]:
        """
        Perform breadth-first search (BFS) traversal from a starting node.
        
        BFS explores nodes level by level, visiting all neighbors before
        moving to the next level. Good for finding shortest paths.
        
        Args:
            graph_id: Unique identifier for the graph
            start_node: Node to start traversal from
            
        Returns:
            List of node IDs in BFS order
        """
        G = self.get_graph(graph_id)
        if not G or start_node not in G:
            return []
        
        # Use NetworkX BFS
        bfs_order = list(nx.bfs_tree(G, start_node).nodes())
        return bfs_order
    
    def dfs_traversal(
        self,
        graph_id: str,
        start_node: str
    ) -> List[str]:
        """
        Perform depth-first search (DFS) traversal from a starting node.
        
        DFS explores as far as possible along each branch before backtracking.
        Good for exploring graph structure and finding cycles.
        
        Args:
            graph_id: Unique identifier for the graph
            start_node: Node to start traversal from
            
        Returns:
            List of node IDs in DFS order
        """
        G = self.get_graph(graph_id)
        if not G or start_node not in G:
            return []
        
        # Use NetworkX DFS
        dfs_order = list(nx.dfs_tree(G, start_node).nodes())
        return dfs_order
    
    def get_path(
        self,
        graph_id: str,
        source: str,
        target: str
    ) -> Optional[List[str]]:
        """
        Find shortest path between two nodes.
        
        Args:
            graph_id: Unique identifier for the graph
            source: Source node ID
            target: Target node ID
            
        Returns:
            List of node IDs in the path, or None if no path exists
        """
        G = self.get_graph(graph_id)
        if not G or source not in G or target not in G:
            return None
        
        try:
            path = nx.shortest_path(G, source, target)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_all_paths(
        self,
        graph_id: str,
        source: str,
        target: str,
        max_length: int = 5
    ) -> List[List[str]]:
        """
        Find all simple paths between two nodes.
        
        Args:
            graph_id: Unique identifier for the graph
            source: Source node ID
            target: Target node ID
            max_length: Maximum path length
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        G = self.get_graph(graph_id)
        if not G or source not in G or target not in G:
            return []
        
        try:
            paths = list(nx.all_simple_paths(G, source, target, cutoff=max_length))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_nodes_within_distance(
        self,
        graph_id: str,
        node_id: str,
        distance: int = 1
    ) -> List[str]:
        """
        Get all nodes within a specified distance (number of hops).
        
        Args:
            graph_id: Unique identifier for the graph
            node_id: Starting node ID
            distance: Maximum distance (number of hops)
            
        Returns:
            List of node IDs within the specified distance
        """
        G = self.get_graph(graph_id)
        if not G or node_id not in G:
            return []
        
        # Use BFS to find nodes within distance
        visited = {node_id}
        current_level = {node_id}
        
        for _ in range(distance):
            next_level = set()
            for node in current_level:
                neighbors = set(G.neighbors(node)) if not isinstance(G, nx.DiGraph) \
                    else set(G.successors(node)) | set(G.predecessors(node))
                next_level.update(neighbors - visited)
            
            visited.update(next_level)
            current_level = next_level
            
            if not current_level:
                break
        
        # Remove the starting node from results
        result = list(visited - {node_id})
        return result
    
    def get_graph_statistics(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """
        Calculate statistics for the graph.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            Dictionary of graph statistics or None if graph not found
        """
        G = self.get_graph(graph_id)
        if not G:
            return None
        
        stats = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'density': nx.density(G),
            'is_connected': nx.is_weakly_connected(G) if isinstance(G, nx.DiGraph) else nx.is_connected(G)
        }
        
        # Add degree statistics
        degrees = [G.degree(n) for n in G.nodes()]
        if degrees:
            stats['avg_degree'] = sum(degrees) / len(degrees)
            stats['max_degree'] = max(degrees)
            stats['min_degree'] = min(degrees)
        
        return stats


# Convenience function for quick graph creation
def create_graph_from_data(
    graph_id: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    service: Optional[GraphService] = None
) -> nx.Graph:
    """
    Convenience function to create a graph.
    
    Args:
        graph_id: Unique identifier for the graph
        nodes: List of node dictionaries
        edges: List of edge dictionaries
        service: GraphService instance (creates new one if not provided)
        
    Returns:
        NetworkX graph object
    """
    if service is None:
        service = GraphService()
    
    return service.create_graph(graph_id, nodes, edges)

