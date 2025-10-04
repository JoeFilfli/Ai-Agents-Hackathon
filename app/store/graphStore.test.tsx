/**
 * Test file for Zustand Graph Store (Task 13)
 * 
 * This file demonstrates how to use the store and verifies
 * that state changes propagate correctly.
 */

import { useMindmapStore, useSelectedNode, useIsLoading } from './graphStore';
import { Node, Edge } from '@/app/types/graph';

// Sample test data
const sampleNodes: Node[] = [
  {
    id: 'node_0',
    label: 'Python',
    description: 'A high-level programming language',
    sourceText: 'Python is a programming language',
    confidence: 0.95,
    metadata: {},
    hasChildren: true,
  },
  {
    id: 'node_1',
    label: 'Data Science',
    description: 'Field of data analysis',
    sourceText: 'Data science involves analyzing data',
    confidence: 0.9,
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
    weight: 0.85,
    confidence: 0.85,
    metadata: {},
  },
];

/**
 * Test 1: Basic store initialization
 */
export function testStoreInitialization() {
  console.log('\n=== Test 1: Store Initialization ===');
  
  const state = useMindmapStore.getState();
  
  console.log('Initial state:');
  console.log('  - graphId:', state.graphId);
  console.log('  - nodes:', state.nodes.length);
  console.log('  - edges:', state.edges.length);
  console.log('  - selectedNodeId:', state.selectedNodeId);
  console.log('  - sidePanelOpen:', state.sidePanelOpen);
  console.log('  - loading:', state.loading);
  
  const passed = 
    state.graphId === null &&
    state.nodes.length === 0 &&
    state.edges.length === 0 &&
    state.selectedNodeId === null &&
    state.sidePanelOpen === true;
  
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  return passed;
}

/**
 * Test 2: Setting graph data
 */
export function testSetGraph() {
  console.log('\n=== Test 2: Set Graph Data ===');
  
  const { setGraph } = useMindmapStore.getState();
  
  // Set the graph
  setGraph('test_graph_123', sampleNodes, sampleEdges);
  
  const state = useMindmapStore.getState();
  
  console.log('After setGraph:');
  console.log('  - graphId:', state.graphId);
  console.log('  - nodes:', state.nodes.length);
  console.log('  - edges:', state.edges.length);
  
  const passed = 
    state.graphId === 'test_graph_123' &&
    state.nodes.length === 2 &&
    state.edges.length === 1;
  
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  return passed;
}

/**
 * Test 3: Node selection
 */
export function testNodeSelection() {
  console.log('\n=== Test 3: Node Selection ===');
  
  const { selectNode, setGraph } = useMindmapStore.getState();
  
  // Ensure we have graph data
  setGraph('test_graph', sampleNodes, sampleEdges);
  
  // Select a node
  selectNode('node_0');
  
  const state = useMindmapStore.getState();
  
  console.log('After selectNode:');
  console.log('  - selectedNodeId:', state.selectedNodeId);
  console.log('  - selectedEdgeId:', state.selectedEdgeId);
  
  const passed = 
    state.selectedNodeId === 'node_0' &&
    state.selectedEdgeId === null;
  
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  return passed;
}

/**
 * Test 4: UI state management
 */
export function testUIState() {
  console.log('\n=== Test 4: UI State Management ===');
  
  const { 
    setLoading, 
    setProcessingText, 
    setSidePanelOpen,
    setError 
  } = useMindmapStore.getState();
  
  // Test loading state
  setLoading(true);
  let state = useMindmapStore.getState();
  console.log('After setLoading(true):', state.loading);
  
  // Test processing state
  setProcessingText(true);
  state = useMindmapStore.getState();
  console.log('After setProcessingText(true):', state.processingText);
  
  // Test panel state
  setSidePanelOpen(false);
  state = useMindmapStore.getState();
  console.log('After setSidePanelOpen(false):', state.sidePanelOpen);
  
  // Test error state
  setError('Test error message');
  state = useMindmapStore.getState();
  console.log('After setError:', state.error);
  
  const passed = 
    state.loading === true &&
    state.processingText === true &&
    state.sidePanelOpen === false &&
    state.error === 'Test error message';
  
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  
  // Clean up
  setLoading(false);
  setProcessingText(false);
  setSidePanelOpen(true);
  state.clearError();
  
  return passed;
}

/**
 * Test 5: Adding nodes dynamically
 */
export function testAddNodes() {
  console.log('\n=== Test 5: Adding Nodes Dynamically ===');
  
  const { setGraph, addNodes } = useMindmapStore.getState();
  
  // Start with one node
  setGraph('test', [sampleNodes[0]], []);
  console.log('Initial nodes:', useMindmapStore.getState().nodes.length);
  
  // Add more nodes
  addNodes([sampleNodes[1]]);
  
  const state = useMindmapStore.getState();
  console.log('After addNodes:', state.nodes.length);
  
  const passed = state.nodes.length === 2;
  
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  return passed;
}

/**
 * Test 6: Conversation state
 */
export function testConversation() {
  console.log('\n=== Test 6: Conversation State ===');
  
  const { addMessage, clearConversation } = useMindmapStore.getState();
  
  // Clear first
  clearConversation();
  
  // Add a message
  addMessage({
    question: 'What is Python?',
    answer: 'Python is a programming language.',
    sources: ['node_0'],
    citations: [],
  });
  
  const state = useMindmapStore.getState();
  
  console.log('After addMessage:');
  console.log('  - messages count:', state.messages.length);
  console.log('  - first message:', state.messages[0]?.question);
  
  const passed = 
    state.messages.length === 1 &&
    state.messages[0].question === 'What is Python?';
  
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  
  // Clean up
  clearConversation();
  
  return passed;
}

/**
 * Test 7: Highlighting nodes
 */
export function testHighlighting() {
  console.log('\n=== Test 7: Node Highlighting ===');
  
  const { setGraph, highlightNodes, clearHighlights } = useMindmapStore.getState();
  
  // Set up graph
  setGraph('test', sampleNodes, sampleEdges);
  
  // Highlight some nodes
  highlightNodes(['node_0', 'node_1']);
  
  let state = useMindmapStore.getState();
  console.log('After highlightNodes:', state.highlightedNodeIds);
  
  const passed1 = state.highlightedNodeIds.length === 2;
  
  // Clear highlights
  clearHighlights();
  state = useMindmapStore.getState();
  console.log('After clearHighlights:', state.highlightedNodeIds.length);
  
  const passed2 = state.highlightedNodeIds.length === 0;
  
  const passed = passed1 && passed2;
  console.log(passed ? '✓ PASS' : '✗ FAIL');
  
  return passed;
}

/**
 * Run all tests
 */
export function runAllStoreTests() {
  console.log('\n' + '='.repeat(60));
  console.log('GRAPH STORE TEST SUITE (Task 13)');
  console.log('='.repeat(60));
  
  const test1 = testStoreInitialization();
  const test2 = testSetGraph();
  const test3 = testNodeSelection();
  const test4 = testUIState();
  const test5 = testAddNodes();
  const test6 = testConversation();
  const test7 = testHighlighting();
  
  console.log('\n' + '='.repeat(60));
  console.log('Test Summary');
  console.log('='.repeat(60));
  console.log(`  Store Initialization:  ${test1 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`  Set Graph Data:        ${test2 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`  Node Selection:        ${test3 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`  UI State Management:   ${test4 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`  Adding Nodes:          ${test5 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`  Conversation State:    ${test6 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`  Node Highlighting:     ${test7 ? '✓ PASS' : '✗ FAIL'}`);
  
  const allPassed = test1 && test2 && test3 && test4 && test5 && test6 && test7;
  
  if (allPassed) {
    console.log('\n🎉 All tests passed!');
    console.log('   Task 13 is complete. Ready for Task 14!');
  } else {
    console.log('\n⚠ Some tests failed. Please review the errors above.');
  }
  
  return allPassed;
}

// Export for console testing
if (typeof window !== 'undefined') {
  (window as any).testGraphStore = runAllStoreTests;
}

