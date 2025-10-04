"""
FastAPI Backend for the Interactive Mindmap System.

This API provides endpoints for:
- Text processing (concept extraction, relationships, embeddings)
- Graph operations
- Q&A functionality
- Text-to-speech generation
"""

import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.services.text_processing import TextProcessingService
from api.services.graph_service import GraphService
from api.models.graph_models import Node, Edge, Graph

### Create FastAPI instance with custom docs and openapi url
app = FastAPI(
    title="Interactive Mindmap API",
    description="API for text-to-graph conversion with LLM integration",
    version="0.1.0",
    docs_url="/api/py/docs",
    openapi_url="/api/py/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph service instance for in-memory storage
graph_service = GraphService()


# ============================================================================
# Request/Response Models
# ============================================================================

class TextProcessRequest(BaseModel):
    """Request model for text processing endpoint."""
    
    text: str = Field(
        ...,
        description="Raw text to process",
        min_length=100,
        max_length=50000
    )
    
    max_concepts: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of concepts to extract"
    )
    
    min_importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum importance score for concepts (0-1)"
    )
    
    min_strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum strength score for relationships (0-1)"
    )
    
    extract_relationships: bool = Field(
        default=True,
        description="Whether to extract relationships between concepts"
    )
    
    generate_embeddings: bool = Field(
        default=True,
        description="Whether to generate embeddings for semantic similarity"
    )


class TextProcessResponse(BaseModel):
    """Response model for text processing endpoint."""
    
    graph_id: str = Field(..., description="Unique identifier for the generated graph")
    nodes: list = Field(..., description="List of concept nodes")
    edges: list = Field(..., description="List of relationship edges")
    metadata: dict = Field(..., description="Processing metadata")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: dict = Field(..., description="Error details")


class GraphRetrieveResponse(BaseModel):
    """Response model for graph retrieval endpoint."""
    
    graph_id: str = Field(..., description="Unique graph identifier")
    nodes: list = Field(..., description="List of nodes in the graph")
    edges: list = Field(..., description="List of edges in the graph")
    statistics: dict = Field(..., description="Graph statistics")


class NodeExpansionRequest(BaseModel):
    """Request model for node expansion endpoint."""
    
    depth: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Depth of expansion (1-3 hops)"
    )


class NodeExpansionResponse(BaseModel):
    """Response model for node expansion endpoint."""
    
    center_node: str = Field(..., description="The node that was expanded")
    nodes: list = Field(..., description="Nodes in the expansion")
    edges: list = Field(..., description="Edges in the expansion")
    depth: int = Field(..., description="Expansion depth")


class RelationshipPathsResponse(BaseModel):
    """Response model for relationship paths endpoint."""
    
    node_id: str = Field(..., description="Source node ID")
    paths: list = Field(..., description="List of paths from this node")
    neighbors: list = Field(..., description="Direct neighbors")
    statistics: dict = Field(..., description="Path statistics")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    "/api/py/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check():
    """
    Check if the API is running and healthy.
    
    Returns service status and version information.
    """
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/api/py/helloFastApi", tags=["Health"])
def hello_fast_api():
    """Legacy hello endpoint for backward compatibility."""
    return {"message": "Hello from FastAPI"}


@app.post(
    "/api/py/text/process",
    response_model=TextProcessResponse,
    tags=["Text Processing"],
    summary="Process text and extract knowledge graph",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Processing failed"}
    }
)
async def process_text(request: TextProcessRequest):
    """
    Process raw text and extract a knowledge graph.
    
    This endpoint:
    1. Validates input text
    2. Extracts key concepts using GPT-4
    3. Identifies relationships between concepts
    4. Generates embeddings for semantic similarity
    5. Returns structured graph data (nodes and edges)
    
    **Parameters:**
    - **text**: Raw text to process (100-50,000 characters)
    - **max_concepts**: Maximum concepts to extract (1-50)
    - **min_importance**: Minimum importance score (0-1)
    - **min_strength**: Minimum relationship strength (0-1)
    - **extract_relationships**: Whether to extract relationships
    - **generate_embeddings**: Whether to generate embeddings
    
    **Returns:**
    - **graph_id**: Unique identifier for the graph
    - **nodes**: List of concept nodes with embeddings
    - **edges**: List of relationship edges
    - **metadata**: Processing information
    """
    try:
        # Initialize text processing service
        service = TextProcessingService()
        
        # Process text
        result = service.process_text(
            text=request.text,
            max_concepts=request.max_concepts,
            min_importance=request.min_importance,
            min_strength=request.min_strength,
            extract_rels=request.extract_relationships,
            generate_embeddings=request.generate_embeddings
        )
        
        # Generate unique graph ID
        graph_id = f"graph_{uuid.uuid4().hex[:12]}"
        
        # Convert concepts to Node format
        nodes = []
        for i, concept in enumerate(result['concepts']):
            node = {
                "id": f"node_{i}",
                "label": concept['name'],
                "description": concept['description'],
                "source_text": concept['source_text'],
                "confidence": concept['importance'],
                "metadata": {
                    "index": i,
                    "has_embedding": 'embedding' in concept
                },
                "has_children": False  # Will be determined by graph structure
            }
            
            # Add embedding if present
            if 'embedding' in concept:
                node['embedding'] = concept['embedding']
            
            nodes.append(node)
        
        # Convert relationships to Edge format
        edges = []
        for i, rel in enumerate(result.get('relationships', [])):
            # Find node IDs for source and target
            source_idx = next(
                (j for j, c in enumerate(result['concepts']) if c['name'] == rel['source']),
                None
            )
            target_idx = next(
                (j for j, c in enumerate(result['concepts']) if c['name'] == rel['target']),
                None
            )
            
            if source_idx is not None and target_idx is not None:
                edge = {
                    "id": f"edge_{i}",
                    "source": f"node_{source_idx}",
                    "target": f"node_{target_idx}",
                    "relationship_type": rel['type'],
                    "weight": rel['strength'],
                    "confidence": rel['strength'],
                    "metadata": {
                        "description": rel.get('description', '')
                    }
                }
                edges.append(edge)
        
        # Store graph in GraphService for later retrieval
        graph_service.create_graph(graph_id, nodes, edges)
        
        # Build response
        return {
            "graph_id": graph_id,
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                **result['metadata'],
                "graph_id": graph_id,
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
        
    except ValueError as e:
        # Input validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": str(e),
                    "retry": False
                }
            }
        )
    
    except Exception as e:
        # Processing errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "PROCESSING_FAILED",
                    "message": f"Failed to process text: {str(e)}",
                    "retry": True
                }
            }
        )


@app.get(
    "/api/py/graph/{graph_id}",
    response_model=GraphRetrieveResponse,
    tags=["Graph Operations"],
    summary="Retrieve a stored graph",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Graph not found"},
        500: {"model": ErrorResponse, "description": "Retrieval failed"}
    }
)
async def get_graph(graph_id: str):
    """
    Retrieve a previously generated graph by its ID.
    
    This endpoint returns the complete graph structure including:
    - All nodes with their properties
    - All edges and relationships
    - Graph statistics (node count, edge count, density, etc.)
    
    **Parameters:**
    - **graph_id**: Unique identifier of the graph
    
    **Returns:**
    - **graph_id**: The graph identifier
    - **nodes**: List of all nodes in the graph
    - **edges**: List of all edges in the graph
    - **statistics**: Graph statistics and metrics
    """
    try:
        # Check if graph exists
        G = graph_service.get_graph(graph_id)
        if not G:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "GRAPH_NOT_FOUND",
                        "message": f"Graph with ID '{graph_id}' not found",
                        "retry": False
                    }
                }
            )
        
        # Get all nodes
        nodes = graph_service.get_all_nodes(graph_id)
        
        # Get all edges
        edges = graph_service.get_all_edges(graph_id)
        
        # Get statistics
        stats = graph_service.get_graph_statistics(graph_id)
        
        return {
            "graph_id": graph_id,
            "nodes": nodes,
            "edges": edges,
            "statistics": stats
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "RETRIEVAL_FAILED",
                    "message": f"Failed to retrieve graph: {str(e)}",
                    "retry": True
                }
            }
        )


@app.post(
    "/api/py/graph/{graph_id}/expand/{node_id}",
    response_model=NodeExpansionResponse,
    tags=["Graph Operations"],
    summary="Expand a node to get its local subgraph",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Graph or node not found"},
        500: {"model": ErrorResponse, "description": "Expansion failed"}
    }
)
async def expand_node(
    graph_id: str,
    node_id: str,
    request: NodeExpansionRequest = NodeExpansionRequest()
):
    """
    Expand a node to get its local neighborhood subgraph.
    
    This endpoint is useful for interactive UI exploration where users
    click on a node to reveal its connections. It returns the center node
    and all nodes within the specified depth (number of hops).
    
    **Parameters:**
    - **graph_id**: Unique identifier of the graph
    - **node_id**: ID of the node to expand
    - **depth**: Number of hops to include (1-3, default: 1)
    
    **Returns:**
    - **center_node**: The node that was expanded
    - **nodes**: All nodes in the expansion (including center)
    - **edges**: All edges connecting the nodes
    - **depth**: The depth of the expansion
    
    **Example:**
    For depth=1, returns the node and its direct neighbors.
    For depth=2, returns the node, neighbors, and neighbors-of-neighbors.
    """
    try:
        # Check if graph exists
        G = graph_service.get_graph(graph_id)
        if not G:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "GRAPH_NOT_FOUND",
                        "message": f"Graph with ID '{graph_id}' not found",
                        "retry": False
                    }
                }
            )
        
        # Check if node exists
        node = graph_service.get_node(graph_id, node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NODE_NOT_FOUND",
                        "message": f"Node '{node_id}' not found in graph '{graph_id}'",
                        "retry": False
                    }
                }
            )
        
        # Expand the node
        expansion = graph_service.expand_node(graph_id, node_id, depth=request.depth)
        
        if not expansion:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "EXPANSION_FAILED",
                        "message": "Failed to expand node",
                        "retry": True
                    }
                }
            )
        
        return expansion
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "EXPANSION_FAILED",
                    "message": f"Failed to expand node: {str(e)}",
                    "retry": True
                }
            }
        )


@app.post(
    "/api/py/graph/{graph_id}/relationships/{node_id}",
    response_model=RelationshipPathsResponse,
    tags=["Graph Operations"],
    summary="Get relationship paths from a node",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Graph or node not found"},
        500: {"model": ErrorResponse, "description": "Path finding failed"}
    }
)
async def get_relationship_paths(graph_id: str, node_id: str):
    """
    Get relationship paths and connections from a specific node.
    
    This endpoint finds paths up to 3 hops from the given node, useful for:
    - Understanding how concepts are connected
    - Explaining relationships in the UI
    - Finding indirect relationships between concepts
    
    **Parameters:**
    - **graph_id**: Unique identifier of the graph
    - **node_id**: Source node ID to find paths from
    
    **Returns:**
    - **node_id**: The source node
    - **paths**: List of paths (up to 3 hops) from this node
    - **neighbors**: List of direct neighbors (1 hop)
    - **statistics**: Path statistics (total paths, avg length, etc.)
    """
    try:
        # Check if graph exists
        G = graph_service.get_graph(graph_id)
        if not G:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "GRAPH_NOT_FOUND",
                        "message": f"Graph with ID '{graph_id}' not found",
                        "retry": False
                    }
                }
            )
        
        # Check if node exists
        node = graph_service.get_node(graph_id, node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NODE_NOT_FOUND",
                        "message": f"Node '{node_id}' not found in graph '{graph_id}'",
                        "retry": False
                    }
                }
            )
        
        # Get direct neighbors
        neighbors = graph_service.get_neighbors(graph_id, node_id)
        
        # Get nodes within 3 hops
        nodes_within_3_hops = graph_service.get_nodes_within_distance(
            graph_id, node_id, distance=3
        )
        
        # Find paths to all reachable nodes (up to 3 hops)
        paths = []
        for target_node in nodes_within_3_hops:
            if target_node != node_id:
                # Get shortest path
                path = graph_service.get_path(graph_id, node_id, target_node)
                if path and len(path) <= 4:  # Max 3 hops = 4 nodes in path
                    paths.append({
                        "target": target_node,
                        "path": path,
                        "length": len(path) - 1,  # Number of hops
                        "nodes": [graph_service.get_node(graph_id, nid) for nid in path]
                    })
        
        # Sort paths by length
        paths.sort(key=lambda p: p['length'])
        
        # Calculate statistics
        statistics = {
            "total_paths": len(paths),
            "direct_neighbors": len(neighbors),
            "reachable_nodes": len(nodes_within_3_hops),
            "avg_path_length": sum(p['length'] for p in paths) / len(paths) if paths else 0,
            "max_path_length": max((p['length'] for p in paths), default=0),
            "min_path_length": min((p['length'] for p in paths), default=0)
        }
        
        return {
            "node_id": node_id,
            "paths": paths,
            "neighbors": neighbors,
            "statistics": statistics
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "PATH_FINDING_FAILED",
                    "message": f"Failed to find relationship paths: {str(e)}",
                    "retry": True
                }
            }
        )