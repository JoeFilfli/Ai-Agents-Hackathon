"""
LLM Service for generating natural language explanations and Q&A.

This service uses GPT-4 to:
1. Generate natural language explanations for relationships between nodes
2. Answer questions about the knowledge graph
3. Provide context-aware responses using graph structure
"""

import os
from typing import Dict, List, Any, Optional
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv


class LLMService:
    """Service for LLM-powered explanations and Q&A."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize the LLM service.
        
        Args:
            model: OpenAI model to use (default: from env or gpt-4o-mini)
        """
        # Load environment variables
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / '.env.local'
        load_dotenv(env_path)
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def explain_relationship(
        self,
        source_node: Dict[str, Any],
        target_node: Dict[str, Any],
        path: List[Dict[str, Any]],
        relationship_type: Optional[str] = None
    ) -> str:
        """
        Generate a natural language explanation of the relationship between two nodes.
        
        This method uses the graph structure (path between nodes) and node metadata
        to create a clear, contextual explanation of how concepts are related.
        
        Args:
            source_node: Source node data (must include 'label' and optionally 'description')
            target_node: Target node data (must include 'label' and optionally 'description')
            path: List of nodes in the path from source to target
            relationship_type: Optional explicit relationship type
            
        Returns:
            Natural language explanation string
        """
        # Build the prompt with graph context
        prompt = self._build_relationship_prompt(
            source_node, target_node, path, relationship_type
        )
        
        try:
            # Call GPT-4 for explanation
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at explaining complex relationships between concepts. Provide clear, concise explanations that help users understand how different ideas are connected."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            explanation = response.choices[0].message.content.strip()
            return explanation
            
        except Exception as e:
            raise Exception(f"Failed to generate explanation: {str(e)}")
    
    def _build_relationship_prompt(
        self,
        source_node: Dict[str, Any],
        target_node: Dict[str, Any],
        path: List[Dict[str, Any]],
        relationship_type: Optional[str] = None
    ) -> str:
        """
        Build a prompt for relationship explanation.
        
        Args:
            source_node: Source node data
            target_node: Target node data
            path: List of nodes in the path
            relationship_type: Optional relationship type
            
        Returns:
            Formatted prompt string
        """
        # Extract node labels and descriptions
        source_label = source_node.get('label', 'Unknown')
        target_label = target_node.get('label', 'Unknown')
        
        source_desc = source_node.get('description', '')
        target_desc = target_node.get('description', '')
        
        # Build the prompt
        prompt = f"Explain the relationship between these two concepts:\n\n"
        prompt += f"**Concept 1: {source_label}**\n"
        if source_desc:
            prompt += f"Description: {source_desc}\n"
        
        prompt += f"\n**Concept 2: {target_label}**\n"
        if target_desc:
            prompt += f"Description: {target_desc}\n"
        
        # Add relationship type if provided
        if relationship_type:
            prompt += f"\nRelationship type: {relationship_type}\n"
        
        # Add path information if there are intermediate nodes
        if len(path) > 2:
            prompt += f"\n**Connection path:**\n"
            path_labels = [node.get('label', 'Unknown') for node in path]
            prompt += " → ".join(path_labels)
            prompt += "\n"
        
        prompt += "\nProvide a clear, 2-3 sentence explanation of how these concepts are related. "
        prompt += "Focus on practical understanding and real-world connections."
        
        return prompt
    
    def answer_question(
        self,
        question: str,
        graph_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Answer a question about the knowledge graph with conversation history support.
        
        Uses the graph structure, node/edge data, and previous conversation
        to provide contextually accurate answers to user questions.
        
        Args:
            question: User's question
            graph_context: Relevant graph data (nodes, edges, paths)
            conversation_history: Previous Q&A pairs for context
            max_tokens: Maximum tokens for response
            
        Returns:
            Dictionary with 'answer', 'confidence', 'sources', and 'citations'
        """
        # Build the prompt with graph context
        prompt = self._build_qa_prompt(question, graph_context)
        
        try:
            # Build messages with conversation history
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on a knowledge graph. Use the provided graph data to give accurate, well-sourced answers. If the graph doesn't contain enough information, say so clearly. Always cite specific concepts when answering."
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for entry in conversation_history[-5:]:  # Keep last 5 exchanges
                    if 'question' in entry:
                        messages.append({
                            "role": "user",
                            "content": entry['question']
                        })
                    if 'answer' in entry:
                        messages.append({
                            "role": "assistant",
                            "content": entry['answer']
                        })
            
            # Add current question
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Call GPT-4 for answer
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Extract mentioned concepts for source tracking
            sources = self._extract_sources(answer, graph_context)
            
            # Build citations from sources
            citations = self._build_citations(sources, graph_context)
            
            return {
                "answer": answer,
                "confidence": "high" if len(sources) > 0 else "medium",
                "sources": sources,
                "citations": citations,
                "model": self.model
            }
            
        except Exception as e:
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def _build_qa_prompt(
        self,
        question: str,
        graph_context: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for Q&A with graph context.
        
        Args:
            question: User's question
            graph_context: Graph data including nodes and edges
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Question: {question}\n\n"
        prompt += "**Available Knowledge Graph Data:**\n\n"
        
        # Add nodes
        if 'nodes' in graph_context and graph_context['nodes']:
            prompt += "**Concepts:**\n"
            for node in graph_context['nodes'][:10]:  # Limit to 10 nodes
                label = node.get('label', 'Unknown')
                desc = node.get('description', '')
                prompt += f"- {label}"
                if desc:
                    prompt += f": {desc}"
                prompt += "\n"
            prompt += "\n"
        
        # Add relationships
        if 'edges' in graph_context and graph_context['edges']:
            prompt += "**Relationships:**\n"
            for edge in graph_context['edges'][:10]:  # Limit to 10 edges
                source = edge.get('source', 'Unknown')
                target = edge.get('target', 'Unknown')
                rel_type = edge.get('relationship_type', 'related to')
                prompt += f"- {source} {rel_type} {target}\n"
            prompt += "\n"
        
        # Add paths if available
        if 'paths' in graph_context and graph_context['paths']:
            prompt += "**Connection Paths:**\n"
            for i, path_info in enumerate(graph_context['paths'][:5], 1):
                path = path_info.get('path', [])
                prompt += f"{i}. {' → '.join(path)}\n"
            prompt += "\n"
        
        prompt += "Based on this knowledge graph, please answer the question. "
        prompt += "Reference specific concepts and relationships in your answer. "
        prompt += "If the graph doesn't contain enough information to answer fully, say so."
        
        return prompt
    
    def _extract_sources(
        self,
        answer: str,
        graph_context: Dict[str, Any]
    ) -> List[str]:
        """
        Extract source nodes mentioned in the answer.
        
        Args:
            answer: Generated answer text
            graph_context: Graph context with node information
            
        Returns:
            List of node IDs that were referenced
        """
        sources = []
        
        if 'nodes' not in graph_context:
            return sources
        
        # Check which node labels appear in the answer
        for node in graph_context['nodes']:
            label = node.get('label', '')
            node_id = node.get('id', '')
            
            if label and label.lower() in answer.lower():
                sources.append(node_id)
        
        return sources
    
    def _build_citations(
        self,
        sources: List[str],
        graph_context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Build detailed citations for source nodes.
        
        Args:
            sources: List of node IDs that were used
            graph_context: Graph context with full node information
            
        Returns:
            List of citation dictionaries with node details
        """
        citations = []
        
        if 'nodes' not in graph_context:
            return citations
        
        # Build citations for each source
        for source_id in sources:
            for node in graph_context['nodes']:
                if node.get('id') == source_id:
                    citations.append({
                        'node_id': source_id,
                        'label': node.get('label', 'Unknown'),
                        'description': node.get('description', ''),
                        'source_text': node.get('source_text', '')
                    })
                    break
        
        return citations
    
    def get_node_context(
        self,
        graph_service,
        graph_id: str,
        node_id: str,
        max_hops: int = 2
    ) -> Dict[str, Any]:
        """
        Get enriched context for a node including its neighbors.
        
        This method gathers all relevant information about a node
        and its neighborhood (up to max_hops) to provide context
        for Q&A.
        
        Args:
            graph_service: GraphService instance
            graph_id: Graph identifier
            node_id: Node to get context for
            max_hops: Maximum number of hops to include (default: 2)
            
        Returns:
            Dictionary with nodes, edges, and paths in the neighborhood
        """
        # Get the main node
        main_node = graph_service.get_node(graph_id, node_id)
        if not main_node:
            return {"nodes": [], "edges": [], "paths": []}
        
        # Get nodes within max_hops
        nearby_node_ids = graph_service.get_nodes_within_distance(
            graph_id, node_id, distance=max_hops
        )
        nearby_node_ids.insert(0, node_id)  # Include the main node
        
        # Get full node data for all nearby nodes
        nodes = []
        for nid in nearby_node_ids:
            node_data = graph_service.get_node(graph_id, nid)
            if node_data:
                nodes.append(node_data)
        
        # Get edges between these nodes
        edges = []
        for source_id in nearby_node_ids:
            neighbors = graph_service.get_neighbors(graph_id, source_id)
            for target_id in neighbors:
                if target_id in nearby_node_ids:
                    edge = graph_service.get_edge(graph_id, source_id, target_id)
                    if edge and edge not in edges:
                        edges.append(edge)
        
        # Get paths from the main node to other nearby nodes
        paths = []
        for target_id in nearby_node_ids:
            if target_id != node_id:
                path = graph_service.get_path(graph_id, node_id, target_id)
                if path and len(path) <= max_hops + 1:
                    paths.append({
                        'target': target_id,
                        'path': path,
                        'length': len(path) - 1
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "paths": paths,
            "focus_node": node_id
        }
    
    def generate_summary(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        max_tokens: int = 300
    ) -> str:
        """
        Generate a summary of the entire knowledge graph.
        
        Args:
            nodes: List of all nodes in the graph
            edges: List of all edges in the graph
            max_tokens: Maximum tokens for summary
            
        Returns:
            Natural language summary of the graph
        """
        prompt = self._build_summary_prompt(nodes, edges)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at summarizing complex information. Create clear, concise summaries that highlight key concepts and relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def _build_summary_prompt(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> str:
        """
        Build a prompt for graph summary.
        
        Args:
            nodes: List of nodes
            edges: List of edges
            
        Returns:
            Formatted prompt string
        """
        prompt = "Summarize this knowledge graph in 2-3 paragraphs:\n\n"
        
        prompt += f"**Key Concepts ({len(nodes)} total):**\n"
        for node in nodes[:15]:  # Limit to 15 nodes
            label = node.get('label', 'Unknown')
            desc = node.get('description', '')
            prompt += f"- {label}"
            if desc:
                prompt += f": {desc[:100]}"  # Truncate long descriptions
            prompt += "\n"
        
        if len(nodes) > 15:
            prompt += f"... and {len(nodes) - 15} more concepts\n"
        
        prompt += f"\n**Key Relationships ({len(edges)} total):**\n"
        for edge in edges[:15]:  # Limit to 15 edges
            source = edge.get('source', 'Unknown')
            target = edge.get('target', 'Unknown')
            rel_type = edge.get('relationship_type', 'related to')
            prompt += f"- {source} {rel_type} {target}\n"
        
        if len(edges) > 15:
            prompt += f"... and {len(edges) - 15} more relationships\n"
        
        prompt += "\nProvide an overview that:\n"
        prompt += "1. Identifies the main themes and topics\n"
        prompt += "2. Highlights the most important concepts\n"
        prompt += "3. Explains how the concepts are interconnected"
        
        return prompt

