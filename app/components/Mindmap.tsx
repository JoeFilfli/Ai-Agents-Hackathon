/**
 * Mindmap Component - Interactive Graph Visualization
 * 
 * This component renders the knowledge graph using Cytoscape.js:
 * - Displays nodes and edges from the store
 * - Force-directed layout for automatic positioning
 * - Pan and zoom controls
 * - Interactive node selection
 * - Smooth animations
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, ElementDefinition } from 'cytoscape';
import fcose from 'cytoscape-fcose';
import { useMindmapStore } from '@/app/store/graphStore';
import { Node as GraphNode, Edge as GraphEdge } from '@/app/types/graph';

// Register the fcose layout
if (typeof cytoscape !== 'undefined') {
  cytoscape.use(fcose);
}

interface MindmapProps {
  /** Optional custom width */
  width?: string | number;
  /** Optional custom height */
  height?: string | number;
  /** Optional custom class name */
  className?: string;
}

/**
 * Mindmap Component
 * 
 * Renders an interactive knowledge graph visualization using Cytoscape.js
 */
export default function Mindmap({ 
  width = '100%', 
  height = '100%',
  className = ''
}: MindmapProps) {
  // Container ref for Cytoscape
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  
  // Get graph data from store
  const { 
    nodes, 
    edges, 
    selectedNodeId, 
    selectNode, 
    highlightedNodeIds,
    updateNode,
    setExpandingNode 
  } = useMindmapStore();
  
  // Track if Cytoscape is initialized
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Track hover state
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  /**
   * Initialize Cytoscape instance
   */
  useEffect(() => {
    if (!containerRef.current || cyRef.current) return;

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      
      // Styling
      style: [
        // Node styles
        {
          selector: 'node',
          style: {
            'background-color': '#4F46E5',
            'label': 'data(label)',
            'color': '#1F2937',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-weight': '600',
            'width': '60px',
            'height': '60px',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            'border-width': 2,
            'border-color': '#6366F1',
            'text-outline-width': 2,
            'text-outline-color': '#ffffff',
          } as any,
        },
        // Selected node style
        {
          selector: 'node:selected',
          style: {
            'background-color': '#DC2626',
            'border-color': '#EF4444',
            'border-width': 3,
          } as any,
        },
        // Highlighted node style
        {
          selector: 'node.highlighted',
          style: {
            'background-color': '#F59E0B',
            'border-color': '#FBBF24',
            'border-width': 3,
          } as any,
        },
        // Hovered node style
        {
          selector: 'node.hovered',
          style: {
            'background-color': '#8B5CF6',
            'border-color': '#A78BFA',
            'border-width': 3,
          } as any,
        },
        // Connected nodes (when hovering)
        {
          selector: 'node.connected',
          style: {
            'background-color': '#10B981',
            'border-color': '#34D399',
            'border-width': 2,
          } as any,
        },
        // Dimmed nodes (not connected)
        {
          selector: 'node.dimmed',
          style: {
            'opacity': 0.3,
          } as any,
        },
        // Edge styles
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#9CA3AF',
            'target-arrow-color': '#9CA3AF',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#6B7280',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
          } as any,
        },
        // Selected edge style
        {
          selector: 'edge:selected',
          style: {
            'width': 3,
            'line-color': '#DC2626',
            'target-arrow-color': '#DC2626',
          } as any,
        },
        // Connected edges (when hovering)
        {
          selector: 'edge.connected',
          style: {
            'width': 3,
            'line-color': '#10B981',
            'target-arrow-color': '#10B981',
          } as any,
        },
        // Dimmed edges (not connected)
        {
          selector: 'edge.dimmed',
          style: {
            'opacity': 0.2,
          } as any,
        },
      ],
      
      // Layout configuration (will be applied when data loads)
      layout: {
        name: 'fcose',
        quality: 'default',
        randomize: false,
        animate: true,
        animationDuration: 1000,
        fit: true,
        padding: 50,
        nodeDimensionsIncludeLabels: true,
        idealEdgeLength: 150,
        edgeElasticity: 0.45,
        nestingFactor: 0.1,
        gravity: 0.25,
        numIter: 2500,
        tile: true,
        tilingPaddingVertical: 10,
        tilingPaddingHorizontal: 10,
      } as any,
      
      // Interaction settings
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2,
      boxSelectionEnabled: false,
    });

    // Store reference
    cyRef.current = cy;
    
    // Handle node selection (single click)
    cy.on('tap', 'node', (event) => {
      const nodeId = event.target.id();
      selectNode(nodeId);
    });
    
    // Handle node expansion (double click)
    cy.on('dbltap', 'node', async (event) => {
      const nodeId = event.target.id();
      const node = event.target;
      
      // Visual feedback
      node.animate({
        style: { 
          'width': '80px',
          'height': '80px',
        }
      }, {
        duration: 200,
        complete: () => {
          node.animate({
            style: {
              'width': '60px',
              'height': '60px',
            }
          }, {
            duration: 200,
          });
        }
      });
      
      // Call expand handler
      await handleNodeExpand(nodeId);
    });
    
    // Handle background tap (deselect)
    cy.on('tap', (event) => {
      if (event.target === cy) {
        selectNode(null);
      }
    });
    
    // Handle mouse over node (highlight connections)
    cy.on('mouseover', 'node', (event) => {
      const nodeId = event.target.id();
      setHoveredNodeId(nodeId);
      
      // Get connected nodes and edges
      const node = event.target;
      const connectedEdges = node.connectedEdges();
      const connectedNodes = connectedEdges.connectedNodes();
      
      // Dim all elements
      cy.elements().addClass('dimmed');
      
      // Highlight hovered node
      node.removeClass('dimmed').addClass('hovered');
      
      // Highlight connected elements
      connectedNodes.removeClass('dimmed').addClass('connected');
      connectedEdges.removeClass('dimmed').addClass('connected');
    });
    
    // Handle mouse out node (clear highlights)
    cy.on('mouseout', 'node', () => {
      setHoveredNodeId(null);
      
      // Remove all hover classes
      cy.elements().removeClass('dimmed hovered connected');
    });
    
    setIsInitialized(true);

    // Cleanup
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
        setIsInitialized(false);
      }
    };
  }, [selectNode]);

  /**
   * Handle node expansion
   * This simulates fetching and adding child nodes
   */
  const handleNodeExpand = async (nodeId: string) => {
    console.log(`Expanding node: ${nodeId}`);
    
    // Find the node in state
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    // Check if node has children
    if (!node.hasChildren) {
      console.log('Node has no children to expand');
      return;
    }
    
    // Set loading state
    setExpandingNode(true);
    
    try {
      // TODO: In real implementation, call API to get expanded nodes
      // For now, just simulate with console log
      console.log('TODO: Call /api/py/graph/{graphId}/expand/{nodeId}');
      
      // Mark node as expanded
      updateNode(nodeId, { hasChildren: false });
      
      // Simulate delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.error('Error expanding node:', error);
    } finally {
      setExpandingNode(false);
    }
  };

  /**
   * Update graph data when nodes or edges change
   */
  useEffect(() => {
    if (!cyRef.current || !isInitialized) return;

    const cy = cyRef.current;
    
    // Convert nodes to Cytoscape format
    const cytoscapeNodes: ElementDefinition[] = nodes.map((node: GraphNode) => ({
      data: {
        id: node.id,
        label: node.label,
        description: node.description,
        confidence: node.confidence,
      },
    }));

    // Convert edges to Cytoscape format
    const cytoscapeEdges: ElementDefinition[] = edges.map((edge: GraphEdge) => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.relationshipType,
        weight: edge.weight,
      },
    }));

    // Clear existing elements
    cy.elements().remove();
    
    // Add new elements
    cy.add([...cytoscapeNodes, ...cytoscapeEdges]);
    
    // Run layout if we have nodes
    if (nodes.length > 0) {
      cy.layout({
        name: 'fcose',
        quality: 'default',
        randomize: false,
        animate: true,
        animationDuration: 1000,
        fit: true,
        padding: 50,
        nodeDimensionsIncludeLabels: true,
        idealEdgeLength: 150,
        edgeElasticity: 0.45,
        nestingFactor: 0.1,
        gravity: 0.25,
        numIter: 2500,
        tile: true,
      } as any).run();
    }
  }, [nodes, edges, isInitialized]);

  /**
   * Update selection state
   */
  useEffect(() => {
    if (!cyRef.current || !isInitialized) return;

    const cy = cyRef.current;
    
    // Clear all selections
    cy.$('node:selected').unselect();
    
    // Select the node if one is selected
    if (selectedNodeId) {
      const node = cy.$(`#${selectedNodeId}`);
      if (node.length > 0) {
        node.select();
        
        // Smoothly pan to the selected node
        cy.animate({
          center: { eles: node },
          zoom: cy.zoom(),
        }, {
          duration: 500,
        });
      }
    }
  }, [selectedNodeId, isInitialized]);

  /**
   * Update highlighted nodes
   */
  useEffect(() => {
    if (!cyRef.current || !isInitialized) return;

    const cy = cyRef.current;
    
    // Remove all highlights
    cy.$('node.highlighted').removeClass('highlighted');
    
    // Add highlights to specified nodes
    if (highlightedNodeIds.length > 0) {
      highlightedNodeIds.forEach((nodeId) => {
        cy.$(`#${nodeId}`).addClass('highlighted');
      });
    }
  }, [highlightedNodeIds, isInitialized]);

  /**
   * Zoom controls
   */
  const handleZoomIn = () => {
    if (cyRef.current) {
      const cy = cyRef.current;
      cy.zoom({
        level: cy.zoom() * 1.2,
        renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
      });
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      const cy = cyRef.current;
      cy.zoom({
        level: cy.zoom() * 0.8,
        renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
      });
    }
  };

  const handleFitView = () => {
    if (cyRef.current) {
      cyRef.current.fit(undefined, 50);
    }
  };

  const handleResetLayout = () => {
    if (cyRef.current && nodes.length > 0) {
      cyRef.current.layout({
        name: 'fcose',
        quality: 'default',
        randomize: true,
        animate: true,
        animationDuration: 1000,
        fit: true,
        padding: 50,
      } as any).run();
    }
  };

  return (
    <div style={{ position: 'relative', width, height }} className={className}>
      {/* Cytoscape container */}
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: '100%',
          backgroundColor: '#F9FAFB',
          borderRadius: '8px',
        }}
      />
      
      {/* Control buttons */}
      <div
        style={{
          position: 'absolute',
          bottom: '20px',
          right: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          zIndex: 10,
        }}
      >
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            backgroundColor: 'white',
            border: '1px solid #D1D5DB',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            fontWeight: 'bold',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          +
        </button>
        
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            backgroundColor: 'white',
            border: '1px solid #D1D5DB',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            fontWeight: 'bold',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          −
        </button>
        
        <button
          onClick={handleFitView}
          title="Fit to View"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            backgroundColor: 'white',
            border: '1px solid #D1D5DB',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          ⊡
        </button>
        
        <button
          onClick={handleResetLayout}
          title="Reset Layout"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            backgroundColor: 'white',
            border: '1px solid #D1D5DB',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          ↻
        </button>
      </div>
      
      {/* Empty state */}
      {nodes.length === 0 && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            color: '#9CA3AF',
            pointerEvents: 'none',
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🗺️</div>
          <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            No Graph Loaded
          </div>
          <div style={{ fontSize: '14px' }}>
            Process some text to generate a knowledge graph
          </div>
        </div>
      )}
      
      {/* Node count indicator */}
      {nodes.length > 0 && (
        <div
          style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            padding: '8px 16px',
            backgroundColor: 'white',
            borderRadius: '8px',
            border: '1px solid #D1D5DB',
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          {nodes.length} nodes • {edges.length} edges
        </div>
      )}
    </div>
  );
}

