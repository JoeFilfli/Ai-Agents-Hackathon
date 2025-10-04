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
      
      // Styling - Dark Mode Theme
      style: [
        // Base node styles
        {
          selector: 'node',
          style: {
            'background-color': '#6366F1', // Indigo-500
            'label': 'data(label)',
            'color': '#F1F5F9', // Slate-100
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-weight': '600',
            'width': '60px',
            'height': '60px',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            'border-width': 2,
            'border-color': '#818CF8', // Indigo-400
            'text-outline-width': 2,
            'text-outline-color': '#1e293b', // Slate-800 for dark background
          } as any,
        },
        // Tier 1 nodes (core concepts) - larger and brighter
        {
          selector: 'node.tier-1',
          style: {
            'width': '80px',
            'height': '80px',
            'font-size': '14px',
            'font-weight': '700',
            'background-color': '#8B5CF6', // Purple-500 (brighter)
            'border-color': '#A78BFA', // Purple-400
            'border-width': 3,
            'text-max-width': '100px',
          } as any,
        },
        // Tier 2 nodes (detail concepts) - normal size
        {
          selector: 'node.tier-2',
          style: {
            'width': '60px',
            'height': '60px',
            'font-size': '11px',
            'background-color': '#6366F1', // Indigo-500
            'border-color': '#818CF8', // Indigo-400
          } as any,
        },
        // Selected node style
        {
          selector: 'node:selected',
          style: {
            'background-color': '#EF4444', // Red-500
            'border-color': '#F87171', // Red-400
            'border-width': 3,
          } as any,
        },
        // Highlighted node style
        {
          selector: 'node.highlighted',
          style: {
            'background-color': '#F59E0B', // Amber-500
            'border-color': '#FBBF24', // Amber-400
            'border-width': 3,
          } as any,
        },
        // Hovered node style
        {
          selector: 'node.hovered',
          style: {
            'background-color': '#A78BFA', // Purple-400
            'border-color': '#C4B5FD', // Purple-300
            'border-width': 3,
          } as any,
        },
        // Connected nodes (when hovering)
        {
          selector: 'node.connected',
          style: {
            'background-color': '#10B981', // Emerald-500
            'border-color': '#34D399', // Emerald-400
            'border-width': 2,
          } as any,
        },
        // Dimmed nodes (not connected)
        {
          selector: 'node.dimmed',
          style: {
            'opacity': 0.2,
          } as any,
        },
        // Edge styles
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#64748B', // Slate-500
            'target-arrow-color': '#64748B',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#94A3B8', // Slate-400
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
          } as any,
        },
        // Selected edge style
        {
          selector: 'edge:selected',
          style: {
            'width': 3,
            'line-color': '#EF4444', // Red-500
            'target-arrow-color': '#EF4444',
          } as any,
        },
        // Connected edges (when hovering)
        {
          selector: 'edge.connected',
          style: {
            'width': 3,
            'line-color': '#10B981', // Emerald-500
            'target-arrow-color': '#10B981',
          } as any,
        },
        // Dimmed edges (not connected)
        {
          selector: 'edge.dimmed',
          style: {
            'opacity': 0.15,
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
        tier: node.tier || 2, // Tier 1 = core, 2 = detail
      },
      // Add tier-specific CSS classes
      classes: node.tier === 1 ? 'tier-1' : 'tier-2',
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
          backgroundColor: '#0F172A', // Slate-900
          borderRadius: '8px',
          border: '1px solid #334155', // Slate-700
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
            backgroundColor: '#1E293B', // Slate-800
            border: '1px solid #475569', // Slate-600
            color: '#E2E8F0', // Slate-200
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            fontWeight: 'bold',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
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
            backgroundColor: '#1E293B', // Slate-800
            border: '1px solid #475569', // Slate-600
            color: '#E2E8F0', // Slate-200
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            fontWeight: 'bold',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
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
            backgroundColor: '#1E293B', // Slate-800
            border: '1px solid #475569', // Slate-600
            color: '#E2E8F0', // Slate-200
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
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
            backgroundColor: '#1E293B', // Slate-800
            border: '1px solid #475569', // Slate-600
            color: '#E2E8F0', // Slate-200
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
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
            color: '#64748B', // Slate-500
            pointerEvents: 'none',
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🗺️</div>
          <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: '#94A3B8' }}>
            No Graph Loaded
          </div>
          <div style={{ fontSize: '14px', color: '#64748B' }}>
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
            backgroundColor: '#1E293B', // Slate-800
            borderRadius: '8px',
            border: '1px solid #475569', // Slate-600
            fontSize: '14px',
            fontWeight: '600',
            color: '#E2E8F0', // Slate-200
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          }}
        >
          {nodes.length} nodes • {edges.length} edges
        </div>
      )}
    </div>
  );
}

