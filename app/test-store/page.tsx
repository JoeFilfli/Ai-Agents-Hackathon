/**
 * Test page for Graph Store
 * Visit: http://localhost:3000/test-store
 */

'use client';

import { useEffect, useState } from 'react';
import { runAllStoreTests } from '../store/graphStore.test';

export default function TestStorePage() {
  const [testResults, setTestResults] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);

  const runTests = () => {
    setIsRunning(true);
    setTestResults('Running tests...\n\n');
    
    // Capture console output
    const logs: string[] = [];
    const originalLog = console.log;
    console.log = (...args: any[]) => {
      logs.push(args.join(' '));
      originalLog(...args);
    };
    
    try {
      // Run the tests
      const result = runAllStoreTests();
      
      // Restore console.log
      console.log = originalLog;
      
      setTestResults(logs.join('\n'));
      setIsRunning(false);
    } catch (error) {
      console.log = originalLog;
      setTestResults(`Error running tests: ${error}`);
      setIsRunning(false);
    }
  };

  return (
    <div style={{ 
      padding: '2rem', 
      fontFamily: 'monospace',
      minHeight: '100vh',
      backgroundColor: '#0f172a', // Slate-900
      color: '#f1f5f9', // Slate-100
    }}>
      <h1 style={{ marginBottom: '1rem', color: '#f1f5f9' }}>Graph Store Test Suite</h1>
      
      <button
        onClick={runTests}
        disabled={isRunning}
        style={{
          padding: '0.5rem 1rem',
          fontSize: '1rem',
          backgroundColor: isRunning ? '#475569' : '#6366f1', // Slate-600 or Indigo-500
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isRunning ? 'not-allowed' : 'pointer',
          marginBottom: '1rem',
        }}
      >
        {isRunning ? 'Running Tests...' : 'Run Tests'}
      </button>
      
      {testResults && (
        <pre
          style={{
            backgroundColor: '#1e293b', // Slate-800
            color: '#e2e8f0', // Slate-200
            padding: '1rem',
            borderRadius: '4px',
            border: '1px solid #334155', // Slate-700
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
          }}
        >
          {testResults}
        </pre>
      )}
      
      <div style={{ marginTop: '2rem', color: '#94a3b8' }}> {/* Slate-400 */}
        <p>This page runs the Zustand store tests defined in:</p>
        <code style={{ 
          backgroundColor: '#1e293b', 
          padding: '0.25rem 0.5rem',
          borderRadius: '4px',
          color: '#fbbf24', // Amber-400
        }}>
          app/store/graphStore.test.tsx
        </code>
      </div>
    </div>
  );
}

