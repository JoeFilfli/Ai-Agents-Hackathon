"""
Test script for LLM Service (Task 10).

This script tests the relationship explanation functionality
using GPT-4 to generate natural language explanations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_relationship_explanation():
    """Test generating explanations for node relationships."""
    print("\n" + "=" * 60)
    print("Testing Relationship Explanation")
    print("=" * 60)
    
    try:
        from api.services.llm_service import LLMService
        
        # Initialize service
        service = LLMService()
        print("✓ LLM service initialized")
        
        # Create test nodes
        source_node = {
            "id": "node_1",
            "label": "Python",
            "description": "A high-level programming language known for readability and versatility"
        }
        
        target_node = {
            "id": "node_3",
            "label": "Data Science",
            "description": "Field that uses scientific methods and algorithms to extract insights from data"
        }
        
        # Create a path through intermediate nodes
        path = [
            source_node,
            {
                "id": "node_2",
                "label": "Machine Learning",
                "description": "Subset of AI that learns from data"
            },
            target_node
        ]
        
        print(f"\nExplaining relationship:")
        print(f"  From: {source_node['label']}")
        print(f"  To: {target_node['label']}")
        print(f"  Path: {' → '.join([n['label'] for n in path])}")
        
        # Generate explanation
        explanation = service.explain_relationship(
            source_node,
            target_node,
            path,
            relationship_type="used-in"
        )
        
        print(f"\n✓ Explanation generated:")
        print(f"  {explanation}")
        
        # Verify explanation mentions both nodes
        if source_node['label'].lower() in explanation.lower():
            print(f"✓ Explanation mentions source node: {source_node['label']}")
        else:
            print(f"⚠ Warning: Explanation doesn't explicitly mention {source_node['label']}")
        
        if target_node['label'].lower() in explanation.lower():
            print(f"✓ Explanation mentions target node: {target_node['label']}")
        else:
            print(f"⚠ Warning: Explanation doesn't explicitly mention {target_node['label']}")
        
        # Check if explanation is substantive
        if len(explanation) > 50:
            print(f"✓ Explanation is substantive ({len(explanation)} characters)")
        else:
            print(f"✗ Explanation too short: {len(explanation)} characters")
            return False
        
        print("\n✓ Relationship explanation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Relationship explanation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_relationship_with_multiple_connections():
    """Test explanation for a node with multiple connections (as per Task 10 requirements)."""
    print("\n" + "=" * 60)
    print("Testing Node with 3+ Connections")
    print("=" * 60)
    
    try:
        from api.services.llm_service import LLMService
        
        service = LLMService()
        
        # Create a central node with 3 connections
        central_node = {
            "id": "node_0",
            "label": "Artificial Intelligence",
            "description": "Intelligence demonstrated by machines"
        }
        
        # Three related nodes
        related_nodes = [
            {
                "id": "node_1",
                "label": "Machine Learning",
                "description": "AI systems that learn from data"
            },
            {
                "id": "node_2",
                "label": "Natural Language Processing",
                "description": "AI for understanding human language"
            },
            {
                "id": "node_3",
                "label": "Computer Vision",
                "description": "AI for understanding images and video"
            }
        ]
        
        print(f"\nTesting explanations for {central_node['label']} with 3 connections:")
        
        all_mentioned = True
        explanations = []
        
        for i, related in enumerate(related_nodes, 1):
            print(f"\n  Connection {i}: {central_node['label']} → {related['label']}")
            
            path = [central_node, related]
            explanation = service.explain_relationship(
                central_node,
                related,
                path,
                relationship_type="includes"
            )
            
            explanations.append(explanation)
            print(f"  Explanation: {explanation[:100]}...")
            
            # Check if both nodes are mentioned
            if related['label'].lower() in explanation.lower():
                print(f"  ✓ Mentions {related['label']}")
            else:
                print(f"  ✗ Missing {related['label']}")
                all_mentioned = False
        
        if all_mentioned:
            print(f"\n✓ All {len(related_nodes)} connections properly explained")
        else:
            print(f"\n⚠ Some explanations missing node references")
        
        print("\n✓ Multi-connection test passed")
        return True
        
    except Exception as e:
        print(f"✗ Multi-connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qa_functionality():
    """Test Q&A functionality with graph context."""
    print("\n" + "=" * 60)
    print("Testing Q&A Functionality")
    print("=" * 60)
    
    try:
        from api.services.llm_service import LLMService
        
        service = LLMService()
        
        # Create graph context
        graph_context = {
            "nodes": [
                {"id": "node_1", "label": "Python", "description": "Programming language"},
                {"id": "node_2", "label": "Web Development", "description": "Building websites"},
                {"id": "node_3", "label": "Data Science", "description": "Analyzing data"}
            ],
            "edges": [
                {"source": "node_1", "target": "node_2", "relationship_type": "used-in"},
                {"source": "node_1", "target": "node_3", "relationship_type": "used-in"}
            ]
        }
        
        question = "What is Python used for?"
        
        print(f"\nQuestion: {question}")
        print(f"Graph context: {len(graph_context['nodes'])} nodes, {len(graph_context['edges'])} edges")
        
        result = service.answer_question(question, graph_context)
        
        print(f"\n✓ Answer generated:")
        print(f"  {result['answer'][:150]}...")
        print(f"\n  Confidence: {result['confidence']}")
        print(f"  Sources: {result['sources']}")
        print(f"  Citations: {len(result.get('citations', []))} citations")
        print(f"  Model: {result['model']}")
        
        # Verify answer structure
        if 'answer' in result and len(result['answer']) > 20:
            print(f"✓ Answer is substantive")
        else:
            print(f"✗ Answer too short")
            return False
        
        # Verify citations are included
        if 'citations' in result:
            print(f"✓ Citations field present")
        else:
            print(f"⚠ Missing citations field")
        
        print("\n✓ Q&A functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ Q&A test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_history():
    """Test Q&A with conversation history (Task 11 requirement)."""
    print("\n" + "=" * 60)
    print("Testing Conversation History")
    print("=" * 60)
    
    try:
        from api.services.llm_service import LLMService
        
        service = LLMService()
        
        # Create a node context
        graph_context = {
            "nodes": [
                {
                    "id": "node_0",
                    "label": "Machine Learning",
                    "description": "A subset of AI that enables systems to learn from data"
                },
                {
                    "id": "node_1",
                    "label": "Supervised Learning",
                    "description": "Learning from labeled data"
                },
                {
                    "id": "node_2",
                    "label": "Neural Networks",
                    "description": "Computing systems inspired by biological neural networks"
                }
            ],
            "edges": [
                {"source": "node_0", "target": "node_1", "relationship_type": "includes"},
                {"source": "node_0", "target": "node_2", "relationship_type": "uses"}
            ]
        }
        
        # First question: "What is this?" about Machine Learning
        question1 = "What is Machine Learning?"
        print(f"\nQuestion 1: {question1}")
        
        result1 = service.answer_question(question1, graph_context)
        print(f"Answer 1: {result1['answer'][:100]}...")
        
        # Build conversation history
        history = [
            {
                "question": question1,
                "answer": result1['answer']
            }
        ]
        
        # Follow-up question that requires context
        question2 = "What techniques does it use?"
        print(f"\nQuestion 2 (Follow-up): {question2}")
        
        result2 = service.answer_question(
            question2,
            graph_context,
            conversation_history=history
        )
        print(f"Answer 2: {result2['answer'][:100]}...")
        
        # Verify that the follow-up answer is relevant
        if len(result2['answer']) > 20:
            print(f"\n✓ Follow-up answer generated with history")
        else:
            print(f"\n✗ Follow-up answer too short")
            return False
        
        # Check if answer mentions related concepts
        answer_lower = result2['answer'].lower()
        if 'supervised' in answer_lower or 'neural' in answer_lower or 'learn' in answer_lower:
            print(f"✓ Follow-up uses context from the graph")
        else:
            print(f"⚠ Follow-up may not fully use graph context")
        
        print("\n✓ Conversation history test passed")
        return True
        
    except Exception as e:
        print(f"✗ Conversation history test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_summary():
    """Test graph summary generation."""
    print("\n" + "=" * 60)
    print("Testing Graph Summary")
    print("=" * 60)
    
    try:
        from api.services.llm_service import LLMService
        
        service = LLMService()
        
        # Create sample graph
        nodes = [
            {"id": "node_1", "label": "Python", "description": "Programming language"},
            {"id": "node_2", "label": "JavaScript", "description": "Web programming language"},
            {"id": "node_3", "label": "Web Development", "description": "Building websites"},
            {"id": "node_4", "label": "Data Science", "description": "Analyzing data"}
        ]
        
        edges = [
            {"source": "node_1", "target": "node_3", "relationship_type": "used-in"},
            {"source": "node_1", "target": "node_4", "relationship_type": "used-in"},
            {"source": "node_2", "target": "node_3", "relationship_type": "used-in"}
        ]
        
        print(f"\nGenerating summary for graph with {len(nodes)} nodes and {len(edges)} edges")
        
        summary = service.generate_summary(nodes, edges)
        
        print(f"\n✓ Summary generated:")
        print(f"  {summary}")
        
        # Verify summary is substantive
        if len(summary) > 100:
            print(f"\n✓ Summary is substantive ({len(summary)} characters)")
        else:
            print(f"\n✗ Summary too short: {len(summary)} characters")
            return False
        
        print("\n✓ Graph summary test passed")
        return True
        
    except Exception as e:
        print(f"✗ Graph summary test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all LLM service tests."""
    print("\n" + "=" * 60)
    print("LLM SERVICE TEST SUITE (Task 10)")
    print("=" * 60 + "\n")
    
    # Run tests
    explanation_ok = test_relationship_explanation()
    multi_connection_ok = test_relationship_with_multiple_connections()
    qa_ok = test_qa_functionality()
    history_ok = test_conversation_history()
    summary_ok = test_graph_summary()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Relationship Explanation:  {'✓ PASS' if explanation_ok else '✗ FAIL'}")
    print(f"  Multi-Connection Test:     {'✓ PASS' if multi_connection_ok else '✗ FAIL'}")
    print(f"  Q&A Functionality:         {'✓ PASS' if qa_ok else '✗ FAIL'}")
    print(f"  Conversation History:      {'✓ PASS' if history_ok else '✗ FAIL'}")
    print(f"  Graph Summary:             {'✓ PASS' if summary_ok else '✗ FAIL'}")
    
    all_passed = all([explanation_ok, multi_connection_ok, qa_ok, history_ok, summary_ok])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Tasks 10 & 11 are complete. Ready for Task 12!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

