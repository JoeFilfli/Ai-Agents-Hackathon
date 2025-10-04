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
    <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
      <h1 style={{ marginBottom: '1rem' }}>Graph Store Test Suite</h1>
      
      <button
        onClick={runTests}
        disabled={isRunning}
        style={{
          padding: '0.5rem 1rem',
          fontSize: '1rem',
          backgroundColor: isRunning ? '#ccc' : '#0070f3',
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
            backgroundColor: '#1e1e1e',
            color: '#d4d4d4',
            padding: '1rem',
            borderRadius: '4px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
          }}
        >
          {testResults}
        </pre>
      )}
      
      <div style={{ marginTop: '2rem', color: '#666' }}>
        <p>This page runs the Zustand store tests defined in:</p>
        <code>app/store/graphStore.test.tsx</code>
      </div>
    </div>
  );
}

