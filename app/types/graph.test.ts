/**
 * Test file to verify TypeScript type definitions compile correctly.
 * 
 * This file creates sample instances of all types to ensure:
 * 1. Types are properly defined
 * 2. TypeScript compiler accepts them
 * 3. IntelliSense works correctly
 * 
 * Run: npx tsc --noEmit to check for type errors
 */

import type {
  Node,
  Edge,
  Graph,
  TextProcessRequest,
  TextProcessResponse,
  NodeExpansionResponse,
  RelationshipExplanationResponse,
  QARequest,
  QAResponse,
  APIError
} from './graph';

// Test Node type
const testNode: Node = {
  id: 'node_1',
  label: 'Machine Learning',
  description: 'A field of AI focused on algorithms that learn from data',
  sourceText: 'Machine learning is a subset of artificial intelligence...',
  embedding: [0.1, 0.2, 0.3, 0.4, 0.5],
  confidence: 0.95,
  metadata: {
    category: 'technology',
    importance: 'high'
  },
  hasChildren: true,
  createdAt: new Date().toISOString(),
  position: {
    x: 100,
    y: 200
  }
};

// Test Node without optional fields
const minimalNode: Node = {
  id: 'node_2',
  label: 'Python',
  description: 'A high-level programming language',
  sourceText: 'Python is widely used...',
  confidence: 0.9,
  metadata: {},
  hasChildren: false
};

// Test Edge type
const testEdge: Edge = {
  id: 'edge_1',
  source: 'node_1',
  target: 'node_2',
  relationshipType: 'related-to',
  weight: 0.85,
  confidence: 0.9,
  metadata: {
    bidirectional: false
  },
  createdAt: new Date().toISOString()
};

// Test different relationship types
const relationshipTypes = ['is-a', 'part-of', 'causes', 'contradicts', 'supports'] as const;
const edgesWithDifferentTypes: Edge[] = relationshipTypes.map((type, index) => ({
  id: `edge_${index}`,
  source: 'node_a',
  target: 'node_b',
  relationshipType: type,
  weight: 0.8,
  confidence: 0.85,
  metadata: {}
}));

// Test Graph type
const testGraph: Graph = {
  graphId: 'graph_123',
  nodes: [testNode, minimalNode],
  edges: [testEdge],
  metadata: {
    title: 'AI Concepts',
    nodeCount: 2,
    edgeCount: 1,
    source: 'user_input'
  },
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
};

// Test TextProcessRequest type
const textProcessRequest: TextProcessRequest = {
  text: 'Machine learning is a subset of artificial intelligence that focuses on algorithms that learn from data.',
  options: {
    maxNodes: 10,
    minConfidence: 0.7
  }
};

// Test TextProcessRequest without options
const minimalTextRequest: TextProcessRequest = {
  text: 'Some text to process...'
};

// Test TextProcessResponse type
const textProcessResponse: TextProcessResponse = {
  graphId: 'graph_456',
  nodes: [testNode],
  edges: [testEdge],
  metadata: {
    processingTime: 2.5,
    modelUsed: 'gpt-4o-mini'
  }
};

// Test NodeExpansionResponse type
const nodeExpansionResponse: NodeExpansionResponse = {
  subnodes: [minimalNode],
  edges: [testEdge]
};

// Test RelationshipExplanationResponse type
const relationshipExplanation: RelationshipExplanationResponse = {
  explanation: 'Machine Learning is related to Python because Python is commonly used for ML development.',
  paths: [
    {
      nodes: ['node_1', 'node_2'],
      relationships: ['related-to']
    },
    {
      nodes: ['node_1', 'node_3', 'node_2'],
      relationships: ['uses', 'implemented-in']
    }
  ],
  relatedNodes: [testNode, minimalNode]
};

// Test QARequest type
const qaRequest: QARequest = {
  question: 'What is machine learning?',
  history: [
    {
      role: 'user',
      content: 'Tell me about AI'
    },
    {
      role: 'assistant',
      content: 'AI is the simulation of human intelligence...'
    }
  ],
  contextDepth: 2
};

// Test QARequest without optional fields
const minimalQARequest: QARequest = {
  question: 'What is this concept?'
};

// Test QAResponse type
const qaResponse: QAResponse = {
  answer: 'Machine learning is a field of AI that focuses on algorithms that can learn from and make predictions on data.',
  sources: [testNode, minimalNode],
  confidence: 0.92
};

// Test APIError type
const apiError: APIError = {
  error: {
    code: 'GRAPH_GENERATION_FAILED',
    message: 'Failed to generate graph from input text',
    details: 'Insufficient concepts extracted (min: 3, found: 1)',
    retry: true,
    suggestions: [
      'Try providing more detailed text',
      'Ensure text is at least 100 characters'
    ]
  }
};

// Test APIError without optional fields
const minimalError: APIError = {
  error: {
    code: 'INVALID_INPUT',
    message: 'Input validation failed'
  }
};

// Type checking functions to ensure proper typing
function processNode(node: Node): string {
  return `Processing ${node.label} (confidence: ${node.confidence})`;
}

function processEdge(edge: Edge): string {
  return `${edge.source} --[${edge.relationshipType}]--> ${edge.target}`;
}

function processGraph(graph: Graph): number {
  return graph.nodes.length + graph.edges.length;
}

// Test type inference
const nodeCount = testGraph.nodes.length; // should be number
const firstNode = testGraph.nodes[0]; // should be Node | undefined
const graphTitle = testGraph.metadata.title; // should be any (from Record<string, any>)

// Test function calls with proper types
const nodeDescription = processNode(testNode);
const edgeDescription = processEdge(testEdge);
const totalElements = processGraph(testGraph);

// Export a test function that can be called
export function runTypeTests(): boolean {
  console.log('✓ All TypeScript types compile successfully!');
  console.log(`✓ Test node: ${testNode.label}`);
  console.log(`✓ Test edge: ${testEdge.relationshipType}`);
  console.log(`✓ Test graph: ${testGraph.graphId}`);
  console.log(`✓ Node count: ${nodeCount}`);
  return true;
}

// Ensure this file is treated as a module
export {};

