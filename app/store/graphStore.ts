/**
 * Zustand Store for Graph State Management
 * 
 * This store manages:
 * - Graph data (nodes, edges)
 * - Selected node/edge state
 * - UI state (loading, panels, errors)
 * - Conversation history for Q&A
 */

import { create } from 'zustand';
import { Node, Edge } from '@/app/types/graph';

// Graph state interface
interface GraphState {
  // Graph data
  graphId: string | null;
  nodes: Node[];
  edges: Edge[];
  
  // Selection state
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  highlightedNodeIds: string[];
  
  // Actions for graph data
  setGraph: (graphId: string, nodes: Node[], edges: Edge[]) => void;
  addNodes: (nodes: Node[]) => void;
  addEdges: (edges: Edge[]) => void;
  updateNode: (nodeId: string, updates: Partial<Node>) => void;
  clearGraph: () => void;
  
  // Actions for selection
  selectNode: (nodeId: string | null) => void;
  selectEdge: (edgeId: string | null) => void;
  highlightNodes: (nodeIds: string[]) => void;
  clearHighlights: () => void;
}

// UI state interface
interface UIState {
  // Panel states
  sidePanelOpen: boolean;
  chatPanelOpen: boolean;
  
  // Loading states
  loading: boolean;
  processingText: boolean;
  expandingNode: boolean;
  generatingExplanation: boolean;
  
  // Error state
  error: string | null;
  
  // Current view mode
  viewMode: 'graph' | 'list' | 'hybrid';
  
  // Actions for UI
  setSidePanelOpen: (open: boolean) => void;
  setChatPanelOpen: (open: boolean) => void;
  setLoading: (loading: boolean) => void;
  setProcessingText: (processing: boolean) => void;
  setExpandingNode: (expanding: boolean) => void;
  setGeneratingExplanation: (generating: boolean) => void;
  setError: (error: string | null) => void;
  setViewMode: (mode: 'graph' | 'list' | 'hybrid') => void;
  clearError: () => void;
}

// Conversation state interface
interface ConversationState {
  // Q&A history
  messages: Array<{
    id: string;
    question: string;
    answer: string;
    sources: string[];
    citations: any[];
    timestamp: number;
  }>;
  
  // Current question being processed
  currentQuestion: string;
  
  // Actions for conversation
  addMessage: (message: {
    question: string;
    answer: string;
    sources: string[];
    citations: any[];
  }) => void;
  setCurrentQuestion: (question: string) => void;
  clearConversation: () => void;
}

// Combined store type
type MindmapStore = GraphState & UIState & ConversationState;

/**
 * Main Zustand store for the mindmap application
 */
export const useMindmapStore = create<MindmapStore>((set, get) => ({
  // ============================================================================
  // Graph State
  // ============================================================================
  graphId: null,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,
  highlightedNodeIds: [],
  
  setGraph: (graphId, nodes, edges) => {
    set({
      graphId,
      nodes,
      edges,
      selectedNodeId: null,
      selectedEdgeId: null,
      highlightedNodeIds: [],
    });
  },
  
  addNodes: (newNodes) => {
    set((state) => ({
      nodes: [...state.nodes, ...newNodes],
    }));
  },
  
  addEdges: (newEdges) => {
    set((state) => ({
      edges: [...state.edges, ...newEdges],
    }));
  },
  
  updateNode: (nodeId, updates) => {
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId ? { ...node, ...updates } : node
      ),
    }));
  },
  
  clearGraph: () => {
    set({
      graphId: null,
      nodes: [],
      edges: [],
      selectedNodeId: null,
      selectedEdgeId: null,
      highlightedNodeIds: [],
    });
  },
  
  selectNode: (nodeId) => {
    set({
      selectedNodeId: nodeId,
      selectedEdgeId: null, // Clear edge selection when selecting node
    });
  },
  
  selectEdge: (edgeId) => {
    set({
      selectedEdgeId: edgeId,
      selectedNodeId: null, // Clear node selection when selecting edge
    });
  },
  
  highlightNodes: (nodeIds) => {
    set({ highlightedNodeIds: nodeIds });
  },
  
  clearHighlights: () => {
    set({ highlightedNodeIds: [] });
  },
  
  // ============================================================================
  // UI State
  // ============================================================================
  sidePanelOpen: true,
  chatPanelOpen: false,
  loading: false,
  processingText: false,
  expandingNode: false,
  generatingExplanation: false,
  error: null,
  viewMode: 'graph',
  
  setSidePanelOpen: (open) => {
    set({ sidePanelOpen: open });
  },
  
  setChatPanelOpen: (open) => {
    set({ chatPanelOpen: open });
  },
  
  setLoading: (loading) => {
    set({ loading });
  },
  
  setProcessingText: (processing) => {
    set({ processingText: processing });
  },
  
  setExpandingNode: (expanding) => {
    set({ expandingNode: expanding });
  },
  
  setGeneratingExplanation: (generating) => {
    set({ generatingExplanation: generating });
  },
  
  setError: (error) => {
    set({ error });
  },
  
  setViewMode: (mode) => {
    set({ viewMode: mode });
  },
  
  clearError: () => {
    set({ error: null });
  },
  
  // ============================================================================
  // Conversation State
  // ============================================================================
  messages: [],
  currentQuestion: '',
  
  addMessage: (message) => {
    const id = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id,
          timestamp: Date.now(),
        },
      ],
      currentQuestion: '',
    }));
  },
  
  setCurrentQuestion: (question) => {
    set({ currentQuestion: question });
  },
  
  clearConversation: () => {
    set({
      messages: [],
      currentQuestion: '',
    });
  },
}));

// ============================================================================
// Selector Hooks (for optimized re-renders)
// ============================================================================

/**
 * Get selected node data
 */
export const useSelectedNode = () => {
  return useMindmapStore((state) => {
    if (!state.selectedNodeId) return null;
    return state.nodes.find((n) => n.id === state.selectedNodeId) || null;
  });
};

/**
 * Get selected edge data
 */
export const useSelectedEdge = () => {
  return useMindmapStore((state) => {
    if (!state.selectedEdgeId) return null;
    return state.edges.find((e) => e.id === state.selectedEdgeId) || null;
  });
};

/**
 * Get highlighted nodes
 */
export const useHighlightedNodes = () => {
  return useMindmapStore((state) => {
    return state.nodes.filter((n) => state.highlightedNodeIds.includes(n.id));
  });
};

/**
 * Get conversation history formatted for API
 */
export const useConversationHistory = () => {
  return useMindmapStore((state) =>
    state.messages.map((msg) => ({
      question: msg.question,
      answer: msg.answer,
    }))
  );
};

/**
 * Check if any loading operation is in progress
 */
export const useIsLoading = () => {
  return useMindmapStore((state) =>
    state.loading ||
    state.processingText ||
    state.expandingNode ||
    state.generatingExplanation
  );
};

