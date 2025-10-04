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
import SidePanel from '@/app/components/SidePanel';
import ChatPanel from '@/app/components/ChatPanel';
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
    clearError,
    chatPanelOpen,
    setChatPanelOpen
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
      // NEW: No max_concepts - unlimited extraction (LLM decides)
      // NOTE: This can take 30-120 seconds for long texts with many concepts
      
      // Create abort controller for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minute timeout
      
      // Use direct backend URL to bypass Next.js proxy timeout
      // Proxy has ~30s timeout, but direct call respects our 3min timeout
      const apiUrl = process.env.NODE_ENV === 'development' 
        ? 'http://127.0.0.1:8000/api/py/text/process'  // Direct backend in dev
        : '/api/py/text/process';  // Proxy in production
      
      console.log('Calling API:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          min_importance: 0.0,  // 0.0 = keep all concepts (LLM decides)
          min_strength: 0.0,    // 0.0 = keep all relationships
          extract_relationships: true,
          generate_embeddings: true,
        }),
        signal: controller.signal,  // Attach abort signal
      });
      
      clearTimeout(timeoutId);  // Clear timeout if request completes
      
      // Get response text first (can only read body once)
      const responseText = await response.text();
      
      // Check if request was successful
      if (!response.ok) {
        // Try to parse error as JSON
        try {
          const errorData = JSON.parse(responseText);
          throw new Error(errorData.error?.message || 'Failed to process text');
        } catch (parseError) {
          // If not JSON, show raw text
          throw new Error(`Server error: ${responseText.substring(0, 200)}`);
        }
      }
      
      // Parse the response - with better error handling
      let data: TextProcessResponse;
      try {
        data = JSON.parse(responseText);
      } catch (jsonError) {
        // If JSON parsing fails, show what we got
        console.error('Failed to parse JSON response. First 500 chars:', responseText.substring(0, 500));
        throw new Error(`Invalid JSON response from server. Response starts with: ${responseText.substring(0, 100)}`);
      }
      
      console.log('Raw API response:', data);
      
      // Get graphId (handle both snake_case and camelCase)
      const graphId = (data as any).graph_id || data.graphId;
      console.log('Graph ID:', graphId);
      
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
      setGraph(graphId, transformedNodes, transformedEdges);
      
      console.log('Store updated. Current state:', { 
        showInput, 
        nodesLength: transformedNodes.length,
        graphId: graphId
      });
      
      // Hide the input form and show the graph
      setShowInput(false);
      
      console.log('Graph generated successfully:', {
        graphId: graphId,
        nodeCount: transformedNodes.length,
        edgeCount: transformedEdges.length,
        showInput: false,
      });
      
    } catch (err: any) {
      console.error('Error processing text:', err);
      
      // Handle specific error types
      if (err.name === 'AbortError') {
        setError('Request timed out. The text may be too long or complex. Try: 1) Shorter text, 2) Higher min_importance (0.3-0.5), or 3) Wait and retry.');
      } else {
        setError(err.message || 'An error occurred while processing the text');
      }
    } finally {
      setProcessingText(false);
    }
  };
  
  /**
   * Handle starting over (clear graph and show input form)
   * Also closes the chat panel if it's open
   */
  const handleStartOver = () => {
    clearGraph();
    setInputText('');
    setShowInput(true);
    clearError();
    setChatPanelOpen(false); // Close chat panel
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
    <main className={`flex min-h-screen flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 transition-all duration-300 ${
      chatPanelOpen ? 'ml-96' : 'ml-0'
    }`}>
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 shadow-lg z-50 relative">
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
      
      {/* Side Panel */}
      <SidePanel />
      
      {/* Chat Panel */}
      <ChatPanel />
      
      {/* Hover Trigger for Chat Panel - Left Edge */}
      {!showInput && nodes.length > 0 && (
        <div
          onMouseEnter={() => setChatPanelOpen(true)}
          className="fixed left-0 top-0 h-full w-8 z-40 group"
          title="Hover to open Q&A Chat"
        >
          {/* Visual indicator */}
          <div className="absolute left-0 top-1/2 -translate-y-1/2 bg-indigo-600/50 group-hover:bg-indigo-600 rounded-r-lg px-1 py-8 transition-all group-hover:px-2">
            <svg
              className="w-4 h-4 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
      </div>
      )}
    </main>
  );
}
