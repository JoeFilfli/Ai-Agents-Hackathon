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