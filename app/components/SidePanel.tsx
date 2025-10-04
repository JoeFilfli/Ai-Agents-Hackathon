/**
 * Side Panel Component - Interactive Node Information Display
 * 
 * This component displays detailed information about selected nodes:
 * - Details tab: Shows node properties and metadata
 * - Relationships tab: Shows and explains connections
 * 
 * Features:
 * - Smooth slide-in/out animation
 * - Tab-based navigation
 * - Responsive design
 * - Dark mode styling
 */

'use client';

import React, { useState } from 'react';
import { useMindmapStore, useSelectedNode } from '@/app/store/graphStore';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Tab type definition - removed 'qa' tab (now in separate ChatPanel)
type TabType = 'details' | 'relationships';

export default function SidePanel() {
  // Get store state and actions
  const { 
    sidePanelOpen, 
    setSidePanelOpen,
    selectedNodeId,
    edges,
    nodes,
    graphId,
    highlightNodes,
    clearHighlights,
    generatingExplanation,
    setGeneratingExplanation
  } = useMindmapStore();
  
  // Get selected node data
  const selectedNode = useSelectedNode();
  
  // Local state for active tab
  const [activeTab, setActiveTab] = useState<TabType>('details');
  
  // Local state for relationships
  const [relationshipExplanation, setRelationshipExplanation] = useState<string>('');
  const [relatedNodeIds, setRelatedNodeIds] = useState<string[]>([]);
  
  /**
   * Handle closing the panel
   */
  const handleClose = () => {
    setSidePanelOpen(false);
  };
  
  /**
   * Handle tab switching
   */
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    
    // Clear highlights when switching away from relationships tab
    if (tab !== 'relationships') {
      clearHighlights();
    }
  };
  
  /**
   * Get connected nodes for the selected node
   */
  const getConnectedNodes = (): Array<{ node: any; edge: any }> => {
    if (!selectedNode) return [];
    
    const connections: Array<{ node: any; edge: any }> = [];
    
    // Find all edges connected to this node
    edges.forEach(edge => {
      if (edge.source === selectedNode.id) {
        // Outgoing edge
        const targetNode = nodes.find(n => n.id === edge.target);
        if (targetNode) {
          connections.push({ node: targetNode, edge });
        }
      } else if (edge.target === selectedNode.id) {
        // Incoming edge
        const sourceNode = nodes.find(n => n.id === edge.source);
        if (sourceNode) {
          connections.push({ node: sourceNode, edge });
        }
      }
    });
    
    return connections;
  };
  
  /**
   * Handle explaining relationships
   */
  const handleExplainRelationships = async () => {
    if (!selectedNode || !graphId) {
      setRelationshipExplanation('Error: Missing node or graph information.');
      return;
    }
    
    const connections = getConnectedNodes();
    if (connections.length === 0) {
      setRelationshipExplanation('This concept has no direct connections to other concepts in the graph.');
      return;
    }
    
    setGeneratingExplanation(true);
    setRelationshipExplanation('');
    
    try {
      // Use the first connected node for explanation
      const firstConnection = connections[0];
      
      // Call the LLM explain endpoint
      const response = await fetch('/api/py/llm/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          graph_id: graphId,
          source_node_id: selectedNode.id,
          target_node_id: firstConnection.node.id,
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`Failed to generate explanation (${response.status})`);
      }
      
      const data = await response.json();
      setRelationshipExplanation(data.explanation);
      
      // Highlight related nodes on the graph
      const connectedIds = connections.map(c => c.node.id);
      setRelatedNodeIds(connectedIds);
      highlightNodes(connectedIds);
      
    } catch (error: any) {
      console.error('Error generating explanation:', error);
      setRelationshipExplanation(`Failed to generate explanation. Please try again.`);
    } finally {
      setGeneratingExplanation(false);
    }
  };
  
  // Don't render if no node is selected
  if (!selectedNode) {
    return null;
  }
  
  return (
    <>
      {/* Backdrop - click to close */}
      {sidePanelOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-[55] transition-opacity duration-300"
          onClick={handleClose}
        />
      )}
      
      {/* Side Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-full md:w-[500px] bg-slate-800 border-l border-slate-700 shadow-2xl z-[60] transform transition-transform duration-300 ease-in-out ${
          sidePanelOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-900">
          <h2 className="text-xl font-bold text-slate-100">
            Node Details
          </h2>
          
          <button
            onClick={handleClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            aria-label="Close panel"
          >
            <svg
              className="w-6 h-6 text-slate-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        
        {/* Tab Navigation */}
        <div className="flex border-b border-slate-700 bg-slate-900">
          <button
            onClick={() => handleTabChange('details')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'details'
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-slate-800'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800'
            }`}
          >
            Details
          </button>
          
          <button
            onClick={() => handleTabChange('relationships')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'relationships'
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-slate-800'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800'
            }`}
          >
            Relationships
          </button>
        </div>
        
        {/* Tab Content */}
        <div className="p-6 overflow-y-auto h-[calc(100%-140px)]">
          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="space-y-6 animate-fadeIn">
              {/* Node Label */}
              <div>
                <h3 className="text-2xl font-bold text-slate-100 mb-2">
                  {selectedNode.label}
                </h3>
                
                {/* Tier Badge */}
                {selectedNode.tier && (
                  <span
                    className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${
                      selectedNode.tier === 1
                        ? 'bg-purple-900/50 text-purple-300 border border-purple-700'
                        : 'bg-indigo-900/50 text-indigo-300 border border-indigo-700'
                    }`}
                  >
                    {selectedNode.tier === 1 ? 'Core Concept' : 'Detail Concept'}
                  </span>
                )}
              </div>
              
              {/* Description */}
              <div>
                <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-2">
                  Description
                </h4>
                <p className="text-slate-200 leading-relaxed">
                  {selectedNode.description || 'No description available.'}
                </p>
              </div>
              
              {/* Source Text */}
              {selectedNode.sourceText && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-2">
                    Source Text
                  </h4>
                  <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                    <p className="text-slate-300 text-sm italic leading-relaxed">
                      "{selectedNode.sourceText}"
                    </p>
                  </div>
                </div>
              )}
              
              {/* Confidence Score */}
              <div>
                <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-2">
                  Confidence Score
                </h4>
                <div className="flex items-center space-x-3">
                  <div className="flex-1 bg-slate-700 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${(selectedNode.confidence * 100).toFixed(0)}%` }}
                    />
                  </div>
                  <span className="text-slate-200 font-semibold text-sm">
                    {(selectedNode.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              
              {/* Metadata */}
              {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-2">
                    Metadata
                  </h4>
                  <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 space-y-2">
                    {Object.entries(selectedNode.metadata).map(([key, value]) => (
                      <div key={key} className="flex items-start justify-between">
                        <span className="text-slate-400 text-sm capitalize">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-slate-200 text-sm font-mono ml-2">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Relationships Tab */}
          {activeTab === 'relationships' && (
            <div className="space-y-6 animate-fadeIn">
              {/* Connected Nodes List */}
              <div>
                <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                  Connected Concepts ({getConnectedNodes().length})
                </h4>
                
                {getConnectedNodes().length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-3">🔗</div>
                    <p className="text-slate-400 text-sm">
                      This concept has no direct connections yet.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {getConnectedNodes().map(({ node, edge }, index) => (
                      <div
                        key={index}
                        className="bg-slate-900 border border-slate-700 rounded-lg p-3 hover:border-indigo-600 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h5 className="text-slate-200 font-medium text-sm mb-1">
                              {node.label}
                            </h5>
                            <p className="text-slate-400 text-xs">
                              {edge.relationshipType || 'related-to'}
                            </p>
                          </div>
                          {edge.metadata?.inferred && (
                            <span className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded">
                              inferred
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Explain Button */}
              {getConnectedNodes().length > 0 && (
                <div>
                  <button
                    onClick={handleExplainRelationships}
                    disabled={generatingExplanation}
                    className={`w-full px-6 py-3 rounded-lg font-semibold text-white transition-all shadow-lg ${
                      generatingExplanation
                        ? 'bg-slate-700 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-500'
                    }`}
                  >
                    {generatingExplanation ? (
                      <span className="flex items-center justify-center">
                        <svg
                          className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        Generating explanation...
                      </span>
                    ) : (
                      '🤖 Explain Relationships'
                    )}
                  </button>
                </div>
              )}
              
              {/* AI Explanation */}
              {relationshipExplanation && (
                <div className="animate-fadeIn">
                  <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                    AI Explanation
                  </h4>
                  <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 border border-indigo-700 rounded-lg p-4">
                    {/* Render markdown with proper styling */}
                    <div className="text-slate-200 leading-relaxed text-sm prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          // Style headers
                          h1: ({ node, ...props }) => <h1 className="text-lg font-bold text-slate-100 mt-2 mb-1" {...props} />,
                          h2: ({ node, ...props }) => <h2 className="text-base font-bold text-slate-100 mt-2 mb-1" {...props} />,
                          h3: ({ node, ...props }) => <h3 className="text-sm font-semibold text-slate-200 mt-2 mb-1" {...props} />,
                          // Style paragraphs
                          p: ({ node, ...props }) => <p className="mb-2 text-slate-200" {...props} />,
                          // Style lists
                          ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-2 space-y-1 text-slate-200" {...props} />,
                          ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-2 space-y-1 text-slate-200" {...props} />,
                          li: ({ node, ...props }) => <li className="ml-2 text-slate-200" {...props} />,
                          // Style inline code and code blocks
                          code: ({ node, className, ...props }) => {
                            const isInline = !className;
                            return isInline ? (
                              <code className="bg-slate-700 px-1.5 py-0.5 rounded text-indigo-300 text-xs font-mono" {...props} />
                            ) : (
                              <code className="block bg-slate-900 p-2 rounded text-indigo-300 text-xs font-mono overflow-x-auto" {...props} />
                            );
                          },
                          // Style links
                          a: ({ node, ...props }) => <a className="text-indigo-300 hover:text-indigo-200 underline" {...props} />,
                          // Style bold and italic
                          strong: ({ node, ...props }) => <strong className="font-bold text-slate-100" {...props} />,
                          em: ({ node, ...props }) => <em className="italic text-slate-200" {...props} />,
                          // Style blockquotes
                          blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-indigo-500 pl-3 italic text-slate-300 my-2" {...props} />,
                        }}
                      >
                        {relationshipExplanation}
                      </ReactMarkdown>
                    </div>
                  </div>
                  
                  {/* Highlighted Nodes Info */}
                  {relatedNodeIds.length > 0 && (
                    <div className="mt-3 flex items-center text-xs text-slate-400">
                      <svg
                        className="w-4 h-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Related nodes are highlighted in orange on the graph
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
        </div>
      </div>
      
      {/* CSS Animation */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </>
  );
}

