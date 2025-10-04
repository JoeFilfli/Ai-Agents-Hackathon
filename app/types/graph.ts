/**
 * Graph data type definitions for the mindmap system.
 * 
 * These interfaces mirror the Pydantic models on the backend:
 * - Node: Represents a concept in the knowledge graph
 * - Edge: Represents a relationship between two nodes
 * - Graph: Represents the complete knowledge graph structure
 * 
 * All interfaces are designed for TypeScript type safety and IntelliSense.
 */

/**
 * Represents a concept node in the knowledge graph.
 * 
 * Each node contains:
 * - Basic info: id, label, description
 * - Context: sourceText from the original input
 * - ML features: embedding vector for similarity search
 * - Quality metrics: confidence score
 * - Metadata: additional flexible data
 */
export interface Node {
  /** Unique identifier for the node */
  id: string;
  
  /** Short name or title of the concept */
  label: string;
  
  /** Detailed explanation of the concept */
  description: string;
  
  /** Original text excerpt this concept was extracted from */
  sourceText: string;
  
  /** Vector embedding for semantic similarity (1536 dimensions for OpenAI) */
  embedding?: number[];
  
  /** Confidence score for this concept extraction (0-1) */
  confidence: number;
  
  /** Additional flexible metadata (position, type, etc.) */
  metadata: Record<string, any>;
  
  /** Whether this node has child nodes for expansion */
  hasChildren: boolean;
  
  /** Hierarchical tier: 1 = core concept, 2 = detail concept */
  tier?: number;
  
  /** Timestamp when this node was created */
  createdAt?: string;
  
  /** Optional: Visual position in the graph (x, y coordinates) */
  position?: {
    x: number;
    y: number;
  };
}

/**
 * Represents a relationship between two nodes in the knowledge graph.
 * 
 * Each edge contains:
 * - Connection: source and target node IDs
 * - Semantics: relationshipType describing the connection
 * - Quality metrics: weight and confidence scores
 * - Metadata: additional flexible data
 */
export interface Edge {
  /** Unique identifier for the edge */
  id: string;
  
  /** ID of the source node */
  source: string;
  
  /** ID of the target node */
  target: string;
  
  /** Type of relationship (e.g., 'is-a', 'part-of', 'related-to', 'causes') */
  relationshipType: string;
  
  /** Strength or importance of this relationship */
  weight: number;
  
  /** Confidence score for this relationship (0-1) */
  confidence: number;
  
  /** Additional flexible metadata */
  metadata: Record<string, any>;
  
  /** Timestamp when this edge was created */
  createdAt?: string;
}

/**
 * Represents the complete knowledge graph structure.
 * 
 * Contains:
 * - Nodes: all concepts in the graph
 * - Edges: all relationships between concepts
 * - Metadata: graph-level information (title, stats, timestamps)
 */
export interface Graph {
  /** Unique identifier for this graph */
  graphId: string;
  
  /** List of all nodes in the graph */
  nodes: Node[];
  
  /** List of all edges in the graph */
  edges: Edge[];
  
  /** Graph-level metadata (title, source, statistics) */
  metadata: Record<string, any>;
  
  /** Timestamp when this graph was created */
  createdAt?: string;
  
  /** Timestamp when this graph was last updated */
  updatedAt?: string;
}

/**
 * API response when processing text into a graph.
 */
export interface TextProcessResponse {
  /** ID of the generated graph */
  graphId: string;
  
  /** Extracted nodes */
  nodes: Node[];
  
  /** Extracted edges */
  edges: Edge[];
  
  /** Processing metadata */
  metadata: Record<string, any>;
}

/**
 * API request for text processing.
 */
export interface TextProcessRequest {
  /** Raw text to process (100-50,000 characters) */
  text: string;
  
  /** Minimum importance score for concepts (0-1). Default 0.0 = LLM decides all concepts */
  min_importance?: number;
  
  /** Minimum strength score for relationships (0-1). Default 0.0 = keep all edges */
  min_strength?: number;
  
  /** Whether to extract relationships between concepts */
  extract_relationships?: boolean;
  
  /** Whether to generate embeddings for semantic similarity */
  generate_embeddings?: boolean;
}

/**
 * API response for node expansion.
 */
export interface NodeExpansionResponse {
  /** Expanded subnodes */
  subnodes: Node[];
  
  /** New edges connecting to subnodes */
  edges: Edge[];
}

/**
 * API response for relationship explanation.
 */
export interface RelationshipExplanationResponse {
  /** Natural language explanation of relationships */
  explanation: string;
  
  /** Graph paths showing connections */
  paths: {
    nodes: string[];
    relationships: string[];
  }[];
  
  /** Related nodes involved in the explanation */
  relatedNodes: Node[];
}

/**
 * API request for Q&A functionality.
 */
export interface QARequest {
  /** The question to ask */
  question: string;
  
  /** Conversation history for context */
  history?: {
    role: 'user' | 'assistant';
    content: string;
  }[];
  
  /** Context depth (number of hops to include) */
  contextDepth?: number;
}

/**
 * API response for Q&A functionality.
 */
export interface QAResponse {
  /** The generated answer */
  answer: string;
  
  /** Source nodes used to generate the answer */
  sources: Node[];
  
  /** Confidence in the answer (0-1) */
  confidence: number;
}

/**
 * Error response structure from API.
 */
export interface APIError {
  error: {
    /** Error code (e.g., 'GRAPH_GENERATION_FAILED') */
    code: string;
    
    /** Human-readable error message */
    message: string;
    
    /** Additional error details */
    details?: string;
    
    /** Whether the operation can be retried */
    retry?: boolean;
    
    /** Suggestions for resolving the error */
    suggestions?: string[];
  };
}

