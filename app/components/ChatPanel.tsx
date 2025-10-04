/**
 * Chat Panel Component - Global Q&A for the Entire Graph
 * 
 * This component provides a conversation interface for asking questions
 * about the entire knowledge graph (not tied to a specific node).
 * 
 * Features:
 * - Full conversation history
 * - Context-aware responses using the entire graph
 * - Smooth slide-in/out animation
 * - Independent of node selection
 */

'use client';

import React, { useState } from 'react';
import { useMindmapStore } from '@/app/store/graphStore';

export default function ChatPanel() {
  // Get store state and actions
  const { 
    chatPanelOpen, 
    setChatPanelOpen,
    graphId,
    messages,
    addMessage
  } = useMindmapStore();
  
  // Local state for question input
  const [question, setQuestion] = useState<string>('');
  const [isAskingQuestion, setIsAskingQuestion] = useState<boolean>(false);
  
  /**
   * Handle closing the panel
   */
  const handleClose = () => {
    setChatPanelOpen(false);
  };
  
  /**
   * Handle asking a question about the graph
   * Minimum 3 characters required by backend validation
   */
  const handleAskQuestion = async () => {
    const trimmedQuestion = question.trim();
    
    // Validate question length (backend requires 3-500 characters)
    if (!trimmedQuestion || trimmedQuestion.length < 3) {
      return;
    }
    
    if (!graphId) {
      addMessage({
        question: trimmedQuestion,
        answer: 'Please generate a graph first before asking questions.',
        sources: [],
        citations: [],
      });
      setQuestion('');
      return;
    }
    
    setIsAskingQuestion(true);
    
    try {
      // Prepare conversation history for API
      const conversationHistory = messages.map(msg => ({
        question: msg.question,
        answer: msg.answer,
      }));
      
      // Call the Q&A endpoint (without node_id for global context)
      const response = await fetch('/api/py/llm/qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          graph_id: graphId,
          question: trimmedQuestion,
          // No node_id - use entire graph as context
          conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
          context_hops: 2,
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Q&A API Error:', response.status, errorText);
        throw new Error(`Failed to get answer (${response.status})`);
      }
      
      const data = await response.json();
      
      // Add to conversation history
      addMessage({
        question: trimmedQuestion,
        answer: data.answer,
        sources: data.sources || [],
        citations: data.citations || [],
      });
      
      // Clear input
      setQuestion('');
      
    } catch (error: any) {
      console.error('Error asking question:', error);
      // Add error message to conversation
      addMessage({
        question: trimmedQuestion,
        answer: 'Sorry, I encountered an error while processing your question. Please try again.',
        sources: [],
        citations: [],
      });
    } finally {
      setIsAskingQuestion(false);
    }
  };
  
  /**
   * Handle Enter key in question input
   */
  const handleQuestionKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskQuestion();
    }
  };
  
  return (
    <>
      {/* Chat Panel */}
      <div
        className={`fixed top-0 left-0 h-screen w-96 bg-slate-900 border-r border-slate-700 shadow-2xl z-50 flex flex-col transition-transform duration-300 ease-in-out ${
          chatPanelOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 pt-6 pb-4 border-b border-slate-700 bg-slate-800">
          <div>
            <h2 className="text-lg font-bold text-slate-100">💬 Graph Q&A</h2>
            <p className="text-xs text-slate-400 mt-0.5">Ask anything about the graph</p>
          </div>
          <button
            onClick={handleClose}
            className="p-2 rounded-lg hover:bg-slate-700 transition-colors text-slate-400 hover:text-slate-200"
            title="Close panel"
          >
            <svg
              className="w-5 h-5"
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
        
        {/* Conversation History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-6xl mb-4">💭</div>
                <h3 className="text-lg font-semibold text-slate-300 mb-2">
                  Start a Conversation
                </h3>
                <p className="text-slate-400 text-sm max-w-xs">
                  Ask questions about the concepts in your knowledge graph.
                  I'll help you understand connections and relationships.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className="space-y-2">
                  {/* Question */}
                  <div className="flex justify-end">
                    <div className="bg-indigo-600 rounded-lg p-3 max-w-[85%]">
                      <p className="text-white text-sm">
                        {msg.question}
                      </p>
                    </div>
                  </div>
                  
                  {/* Answer */}
                  <div className="flex justify-start">
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 max-w-[85%]">
                      <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
                        {msg.answer}
                      </p>
                      
                      {/* Sources */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-700">
                          <p className="text-xs text-slate-400">
                            📚 Sources: {msg.sources.join(', ')}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Question Input Footer */}
        <div className="p-4 border-t border-slate-700 bg-slate-800">
          <div className="flex space-x-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleQuestionKeyDown}
              placeholder="Ask a question..."
              disabled={isAskingQuestion}
              className="flex-1 bg-slate-900 border border-slate-700 text-slate-200 placeholder-slate-500 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleAskQuestion}
              disabled={question.trim().length < 3 || isAskingQuestion}
              className={`px-4 py-3 rounded-lg font-semibold text-white transition-all ${
                question.trim().length < 3 || isAskingQuestion
                  ? 'bg-slate-700 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-500'
              }`}
            >
              {isAskingQuestion ? (
                <svg
                  className="animate-spin h-5 w-5"
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
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              )}
            </button>
          </div>
          
          {/* Validation message and hint */}
          {question.trim().length > 0 && question.trim().length < 3 ? (
            <p className="text-xs text-amber-400 mt-2">
              ⚠️ Question must be at least 3 characters long
            </p>
          ) : (
            <p className="text-xs text-slate-500 mt-2">
              Press Enter to send • Ask about concepts and relationships
            </p>
          )}
        </div>
      </div>
    </>
  );
}

