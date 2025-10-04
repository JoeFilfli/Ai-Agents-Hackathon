/**
 * Main Page - Interactive Mindmap Application
 * 
 * This is the primary user interface that allows users to:
 * - Input text to analyze
 * - Generate knowledge graphs from text
 * - Visualize and interact with the generated graph
 * - Explore relationships between concepts
 */

'use client';

import React, { useState } from 'react';
import Mindmap from '@/app/components/Mindmap';
import { useMindmapStore } from '@/app/store/graphStore';
import { TextProcessResponse } from '@/app/types/graph';

export default function Home() {
  // Get store state and actions
  const { 
    nodes, 
    setGraph, 
    clearGraph,
    processingText,
    setProcessingText,
    error,
    setError,
    clearError
  } = useMindmapStore();
  
  // Local state for text input
  const [inputText, setInputText] = useState('');
  const [showInput, setShowInput] = useState(true);
  
  // Character count validation
  const MIN_CHARS = 100;
  const MAX_CHARS = 50000;
  const charCount = inputText.length;
  const isValidLength = charCount >= MIN_CHARS && charCount <= MAX_CHARS;
  
  /**
   * Handle text submission
   * Validates input and calls the backend API to process text
   */
  const handleSubmit = async () => {
    // Clear any previous errors
    clearError();
    
    // Validate input length
    if (!isValidLength) {
      setError(`Text must be between ${MIN_CHARS} and ${MAX_CHARS} characters. Current: ${charCount}`);
      return;
    }
    
    // Set loading state
    setProcessingText(true);
    
    try {
      // Call the backend API to process text
      const response = await fetch('/api/py/text/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          max_concepts: 10,
          min_importance: 0.5,
          min_strength: 0.5,
          extract_relationships: true,
          generate_embeddings: true,
        }),
      });
      
      // Check if request was successful
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || 'Failed to process text');
      }
      
      // Parse the response
      const data: TextProcessResponse = await response.json();
      
      console.log('Raw API response:', data);
      
      // Transform snake_case to camelCase for TypeScript compatibility
      const transformedNodes = data.nodes.map((node: any) => ({
        ...node,
        sourceText: node.source_text || node.sourceText || '',
        hasChildren: node.has_children !== undefined ? node.has_children : false,
        tier: node.tier || 2, // Default to tier 2 if not specified
      }));
      
      const transformedEdges = data.edges.map((edge: any) => ({
        ...edge,
        relationshipType: edge.relationship_type || edge.relationshipType || 'related-to',
      }));
      
      console.log('Transformed nodes:', transformedNodes);
      console.log('Transformed edges:', transformedEdges);
      
      // Update the store with the generated graph
      setGraph(data.graphId, transformedNodes, transformedEdges);
      
      console.log('Store updated. Current state:', { 
        showInput, 
        nodesLength: transformedNodes.length 
      });
      
      // Hide the input form and show the graph
      setShowInput(false);
      
      console.log('Graph generated successfully:', {
        graphId: data.graphId,
        nodeCount: transformedNodes.length,
        edgeCount: transformedEdges.length,
        showInput: false,
      });
      
    } catch (err: any) {
      console.error('Error processing text:', err);
      setError(err.message || 'An error occurred while processing the text');
    } finally {
      setProcessingText(false);
    }
  };
  
  /**
   * Handle starting over (clear graph and show input form)
   */
  const handleStartOver = () => {
    clearGraph();
    setInputText('');
    setShowInput(true);
    clearError();
  };
  
  /**
   * Handle Enter key in textarea (Ctrl+Enter to submit)
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <main className="flex min-h-screen flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-100">
                Interactive Mindmap
              </h1>
              <p className="text-sm text-slate-300 mt-1">
                Transform text into interactive knowledge graphs
              </p>
            </div>
            
            {/* Show "Start Over" button when graph is displayed */}
            {!showInput && nodes.length > 0 && (
              <button
                onClick={handleStartOver}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-colors font-medium shadow-lg"
              >
                Start Over
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        
        {/* Input Form (shown initially or when starting over) */}
        {showInput && (
          <div className="w-full max-w-4xl">
            <div className="bg-slate-800 border border-slate-700 rounded-xl shadow-2xl p-8">
              <h2 className="text-xl font-semibold text-slate-100 mb-4">
                Enter Text to Analyze
              </h2>
              
              <p className="text-sm text-slate-300 mb-4">
                Paste or type any text you want to analyze. We'll extract key concepts
                and relationships to create an interactive knowledge graph.
              </p>
              
              {/* Text Area */}
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter your text here... (minimum 100 characters)"
                className="w-full h-64 p-4 bg-slate-900 border border-slate-600 text-slate-100 placeholder-slate-500 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none font-mono text-sm"
                disabled={processingText}
              />
              
              {/* Character Counter */}
              <div className="flex items-center justify-between mt-3">
                <div className="text-sm">
                  <span className={`font-medium ${
                    charCount < MIN_CHARS ? 'text-slate-500' :
                    charCount > MAX_CHARS ? 'text-red-400' :
                    'text-green-400'
                  }`}>
                    {charCount.toLocaleString()}
                  </span>
                  <span className="text-slate-400">
                    {' '} / {MIN_CHARS.toLocaleString()} - {MAX_CHARS.toLocaleString()} characters
                  </span>
                </div>
                
                <div className="text-xs text-slate-400">
                  Press <kbd className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-300">Ctrl</kbd> + <kbd className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-300">Enter</kbd> to submit
                </div>
              </div>
              
              {/* Error Message */}
              {error && (
                <div className="mt-4 p-4 bg-red-900/30 border border-red-700 rounded-lg">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-red-200">
                        {error}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                disabled={!isValidLength || processingText}
                className={`w-full mt-6 py-3 px-6 rounded-lg font-semibold text-white transition-all ${
                  !isValidLength || processingText
                    ? 'bg-slate-700 cursor-not-allowed opacity-50'
                    : 'bg-indigo-600 hover:bg-indigo-500 hover:shadow-lg shadow-indigo-500/50'
                }`}
              >
                {processingText ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing text...
                  </span>
                ) : (
                  'Generate Knowledge Graph'
                )}
              </button>
            </div>
            
            {/* Sample Text Examples */}
            <div className="mt-6 text-center text-sm text-slate-400">
              Try it with articles, documentation, research papers, or any informative text
            </div>
          </div>
        )}
        
        {/* Graph Visualization (shown after processing) */}
        {!showInput && nodes.length > 0 && (
          <div style={{ 
            width: '100%', 
            height: 'calc(100vh - 120px)', // Full viewport height minus header
            padding: '1rem',
            position: 'relative',
          }}>
            {/* Debug info */}
            <div style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              padding: '0.5rem',
              backgroundColor: '#1e293b',
              color: '#94a3b8',
              fontSize: '12px',
              borderRadius: '4px',
              zIndex: 1000,
            }}>
              Debug: {nodes.length} nodes loaded
            </div>
            
            <Mindmap 
              width="100%" 
              height="100%"
              className="rounded-lg shadow-lg"
            />
          </div>
        )}
        
        {/* Debug state display */}
        {!showInput && nodes.length === 0 && (
          <div style={{
            color: '#ef4444',
            padding: '2rem',
            textAlign: 'center',
          }}>
            ⚠️ Graph container visible but no nodes loaded. Check console for errors.
          </div>
        )}
        
        {/* Loading Overlay */}
        {processingText && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-slate-800 border border-slate-700 rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
              <div className="flex flex-col items-center">
                {/* Animated spinner */}
                <svg className="animate-spin h-16 w-16 text-indigo-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                
                <h3 className="text-xl font-semibold text-slate-100 mb-2">
                  Generating Knowledge Graph
                </h3>
                
                <p className="text-sm text-slate-300 text-center">
                  Analyzing text, extracting concepts, and building relationships...
                </p>
                
                <div className="mt-4 w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                  <div className="bg-indigo-500 h-2 rounded-full animate-pulse shadow-lg shadow-indigo-500/50" style={{ width: '70%' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
