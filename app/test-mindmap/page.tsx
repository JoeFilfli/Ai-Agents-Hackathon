/**
 * Test page for Mindmap Component (Task 14)
 * Visit: http://localhost:3000/test-mindmap
 */

'use client';

import { useEffect, useState } from 'react';
import Mindmap from '@/app/components/Mindmap';
import { useMindmapStore } from '@/app/store/graphStore';
import { Node, Edge } from '@/app/types/graph';

// Sample graph data for testing
const sampleNodes: Node[] = [
  {
    id: 'node_0',
    label: 'Python',
    description: 'A high-level programming language known for readability',
    sourceText: 'Python is a programming language',
    confidence: 0.95,
    metadata: {},
    hasChildren: true,
  },
  {
    id: 'node_1',
    label: 'Data Science',
    description: 'Field that uses scientific methods to extract insights from data',
    sourceText: 'Data science involves analyzing data',
    confidence: 0.9,
    metadata: {},
    hasChildren: false,
  },
  {
    id: 'node_2',
    label: 'Machine Learning',
    description: 'Subset of AI that enables systems to learn from data',
    sourceText: 'Machine learning uses algorithms',
    confidence: 0.92,
    metadata: {},
    hasChildren: true,
  },
  {
    id: 'node_3',
    label: 'Web Development',
    description: 'Building and maintaining websites and web applications',
    sourceText: 'Web development creates websites',
    confidence: 0.88,
    metadata: {},
    hasChildren: false,
  },
  {
    id: 'node_4',
    label: 'Neural Networks',
    description: 'Computing systems inspired by biological neural networks',
    sourceText: 'Neural networks process information',
    confidence: 0.85,
    metadata: {},
    hasChildren: false,
  },
];

const sampleEdges: Edge[] = [
  {
    id: 'edge_0',
    source: 'node_0',
    target: 'node_1',
    relationshipType: 'used-in',
    weight: 0.9,
    confidence: 0.9,
    metadata: {},
  },
  {
    id: 'edge_1',
    source: 'node_0',
    target: 'node_3',
    relationshipType: 'used-in',
    weight: 0.85,
    confidence: 0.85,
    metadata: {},
  },
  {
    id: 'edge_2',
    source: 'node_1',
    target: 'node_2',
    relationshipType: 'includes',
    weight: 0.95,
    confidence: 0.95,
    metadata: {},
  },
  {
    id: 'edge_3',
    source: 'node_2',
    target: 'node_4',
    relationshipType: 'uses',
    weight: 0.88,
    confidence: 0.88,
    metadata: {},
  },
];

export default function TestMindmapPage() {
  const { setGraph, clearGraph, selectNode, highlightNodes, clearHighlights } = useMindmapStore();
  const [isLoaded, setIsLoaded] = useState(false);

  // Load sample graph on mount
  useEffect(() => {
    loadSampleGraph();
  }, []);

  const loadSampleGraph = () => {
    setGraph('test_graph_' + Date.now(), sampleNodes, sampleEdges);
    setIsLoaded(true);
  };

  const handleClearGraph = () => {
    clearGraph();
    setIsLoaded(false);
  };

  const handleSelectNode = (nodeId: string) => {
    selectNode(nodeId);
  };

  const handleHighlightNodes = () => {
    highlightNodes(['node_1', 'node_2']);
  };

  const handleClearHighlights = () => {
    clearHighlights();
  };

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      backgroundColor: '#f0f0f0',
    }}>
      {/* Header */}
      <div style={{ 
        padding: '1rem', 
        backgroundColor: 'white', 
        borderBottom: '1px solid #e0e0e0',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        <h1 style={{ margin: 0, marginBottom: '1rem', fontSize: '24px' }}>
          Mindmap Component Test (Task 14)
        </h1>
        
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={loadSampleGraph}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#4F46E5',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
            }}
          >
            Load Sample Graph
          </button>
          
          <button
            onClick={handleClearGraph}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#DC2626',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
            }}
          >
            Clear Graph
          </button>
          
          <button
            onClick={() => handleSelectNode('node_0')}
            disabled={!isLoaded}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: isLoaded ? '#059669' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoaded ? 'pointer' : 'not-allowed',
              fontSize: '14px',
              fontWeight: '600',
            }}
          >
            Select "Python"
          </button>
          
          <button
            onClick={handleHighlightNodes}
            disabled={!isLoaded}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: isLoaded ? '#F59E0B' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoaded ? 'pointer' : 'not-allowed',
              fontSize: '14px',
              fontWeight: '600',
            }}
          >
            Highlight Nodes
          </button>
          
          <button
            onClick={handleClearHighlights}
            disabled={!isLoaded}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: isLoaded ? '#6B7280' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoaded ? 'pointer' : 'not-allowed',
              fontSize: '14px',
              fontWeight: '600',
            }}
          >
            Clear Highlights
          </button>
        </div>
        
        <div style={{ 
          marginTop: '1rem', 
          padding: '0.75rem', 
          backgroundColor: '#F3F4F6', 
          borderRadius: '4px',
          fontSize: '14px',
        }}>
          <strong>Test Checklist (Task 15 - Node Interactions):</strong>
          <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
            <li><strong>✓ Single Click:</strong> Click any node → turns red (selected)</li>
            <li><strong>✓ Double Click:</strong> Double-click node → bounce animation (expand)</li>
            <li><strong>✓ Hover:</strong> Hover over node → purple highlight, connected nodes turn green</li>
            <li><strong>✓ Connection Highlight:</strong> Hover shows only connected nodes/edges</li>
            <li><strong>✓ Dimming:</strong> Non-connected nodes fade when hovering</li>
            <li><strong>✓ Mouse Out:</strong> Move mouse away → highlights clear</li>
            <li>✓ Pan by dragging background</li>
            <li>✓ Zoom with mouse wheel or controls</li>
            <li>✓ Smooth animations on all interactions</li>
          </ul>
          
          <div style={{ 
            marginTop: '0.75rem', 
            padding: '0.5rem', 
            backgroundColor: '#DBEAFE', 
            borderRadius: '4px',
            border: '1px solid #3B82F6'
          }}>
            <strong>💡 Interaction Guide:</strong>
            <ul style={{ margin: '0.25rem 0', paddingLeft: '1.5rem' }}>
              <li><strong>Blue:</strong> Normal node</li>
              <li><strong>Red:</strong> Selected node (single click)</li>
              <li><strong>Purple:</strong> Hovered node</li>
              <li><strong>Green:</strong> Connected nodes (when hovering)</li>
              <li><strong>Orange:</strong> Highlighted nodes (via button)</li>
              <li><strong>Faded:</strong> Dimmed (not connected to hovered node)</li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Mindmap */}
      <div style={{ flex: 1, padding: '1rem', overflow: 'hidden' }}>
        <Mindmap />
      </div>
    </div>
  );
}

