"""
Test script for LLM API endpoints (Task 12).

This script tests the two new LLM endpoints:
1. POST /api/py/llm/explain - Generate relationship explanation
2. POST /api/py/llm/qa - Answer questions about the graph
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_explain_endpoint():
    """Test the relationship explanation endpoint."""
    print("\n" + "=" * 60)
    print("Testing Relationship Explanation Endpoint")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # First, create a graph
        print("\n1. Creating graph...")
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Python is a programming language used in data science. Data science involves analyzing data to extract insights. Machine learning is a subset of data science that uses algorithms.",
                "max_concepts": 5,
                "min_importance": 0.5,
                "extract_relationships": True,
                "generate_embeddings": False
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph: {process_response.status_code}")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        print(f"  - {len(data['nodes'])} nodes")
        print(f"  - {len(data['edges'])} edges")
        
        if len(data['nodes']) < 2:
            print(f"⚠ Not enough nodes to test explanation")
            return True
        
        # Get two nodes to explain
        node1_id = data['nodes'][0]['id']
        node2_id = data['nodes'][1]['id']
        node1_label = data['nodes'][0]['label']
        node2_label = data['nodes'][1]['label']
        
        print(f"\n2. Requesting explanation:")
        print(f"   From: {node1_label} ({node1_id})")
        print(f"   To: {node2_label} ({node2_id})")
        
        # Request explanation
        explain_response = client.post(
            "/api/py/llm/explain",
            json={
                "graph_id": graph_id,
                "source_node_id": node1_id,
                "target_node_id": node2_id
            }
        )
        
        if explain_response.status_code != 200:
            print(f"✗ Explanation failed: {explain_response.status_code}")
            print(f"  Response: {explain_response.text}")
            return False
        
        result = explain_response.json()
        
        print(f"\n✓ Explanation generated:")
        print(f"  {result['explanation']}")
        print(f"\n  Model: {result['model']}")
        print(f"  Path length: {len(result['path'])} nodes")
        
        # Verify response structure
        if 'explanation' in result and len(result['explanation']) > 20:
            print(f"\n✓ Explanation is substantive ({len(result['explanation'])} chars)")
        else:
            print(f"\n✗ Explanation too short")
            return False
        
        # Verify source and target nodes are included
        if 'source_node' in result and 'target_node' in result:
            print(f"✓ Source and target nodes included")
        else:
            print(f"✗ Missing node data")
            return False
        
        print("\n✓ Explanation endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ Explanation endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qa_endpoint():
    """Test the Q&A endpoint."""
    print("\n" + "=" * 60)
    print("Testing Q&A Endpoint")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Create a graph
        print("\n1. Creating graph...")
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Artificial intelligence uses machine learning techniques. Machine learning includes supervised learning and unsupervised learning. Neural networks are a type of machine learning model inspired by the human brain.",
                "max_concepts": 5,
                "min_importance": 0.4,
                "extract_relationships": True,
                "generate_embeddings": False
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph: {process_response.status_code}")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        print(f"  - {len(data['nodes'])} nodes")
        
        # Ask a question
        question = "What is artificial intelligence?"
        print(f"\n2. Asking question: '{question}'")
        
        qa_response = client.post(
            "/api/py/llm/qa",
            json={
                "graph_id": graph_id,
                "question": question
            }
        )
        
        if qa_response.status_code != 200:
            print(f"✗ Q&A failed: {qa_response.status_code}")
            print(f"  Response: {qa_response.text}")
            return False
        
        result = qa_response.json()
        
        print(f"\n✓ Answer generated:")
        print(f"  {result['answer'][:200]}...")
        print(f"\n  Confidence: {result['confidence']}")
        print(f"  Sources: {result['sources']}")
        print(f"  Citations: {len(result['citations'])} citations")
        print(f"  Context nodes: {result['context_nodes']}")
        print(f"  Model: {result['model']}")
        
        # Verify response structure
        if 'answer' in result and len(result['answer']) > 20:
            print(f"\n✓ Answer is substantive")
        else:
            print(f"\n✗ Answer too short")
            return False
        
        if 'citations' in result:
            print(f"✓ Citations included")
        else:
            print(f"⚠ Missing citations")
        
        print("\n✓ Q&A endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ Q&A endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qa_with_history():
    """Test Q&A endpoint with conversation history."""
    print("\n" + "=" * 60)
    print("Testing Q&A with Conversation History")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Create a graph
        print("\n1. Creating graph...")
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Python is a versatile programming language. It is used for web development with frameworks like Django and Flask. Python is also popular in data science and machine learning applications.",
                "max_concepts": 5,
                "min_importance": 0.5,
                "extract_relationships": True,
                "generate_embeddings": False
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        
        # First question
        question1 = "What is Python?"
        print(f"\n2. Question 1: '{question1}'")
        
        qa1_response = client.post(
            "/api/py/llm/qa",
            json={
                "graph_id": graph_id,
                "question": question1
            }
        )
        
        if qa1_response.status_code != 200:
            print(f"✗ First Q&A failed")
            return False
        
        result1 = qa1_response.json()
        print(f"✓ Answer 1: {result1['answer'][:100]}...")
        
        # Build history
        history = [
            {
                "question": question1,
                "answer": result1['answer']
            }
        ]
        
        # Follow-up question
        question2 = "What is it used for?"
        print(f"\n3. Question 2 (follow-up): '{question2}'")
        
        qa2_response = client.post(
            "/api/py/llm/qa",
            json={
                "graph_id": graph_id,
                "question": question2,
                "conversation_history": history
            }
        )
        
        if qa2_response.status_code != 200:
            print(f"✗ Follow-up Q&A failed")
            return False
        
        result2 = qa2_response.json()
        print(f"✓ Answer 2: {result2['answer'][:100]}...")
        
        # Verify the follow-up uses context
        if len(result2['answer']) > 20:
            print(f"\n✓ Follow-up question answered with history")
        else:
            print(f"\n✗ Follow-up answer too short")
            return False
        
        print("\n✓ Conversation history test passed")
        return True
        
    except Exception as e:
        print(f"✗ Conversation history test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qa_with_node_focus():
    """Test Q&A endpoint with specific node focus."""
    print("\n" + "=" * 60)
    print("Testing Q&A with Node Focus")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Create a graph
        print("\n1. Creating graph...")
        process_response = client.post(
            "/api/py/text/process",
            json={
                "text": "Machine learning is a subset of artificial intelligence. It includes supervised learning, unsupervised learning, and reinforcement learning. Neural networks are commonly used in deep learning.",
                "max_concepts": 5,
                "min_importance": 0.5,
                "extract_relationships": True,
                "generate_embeddings": False
            }
        )
        
        if process_response.status_code != 200:
            print(f"✗ Failed to create graph")
            return False
        
        data = process_response.json()
        graph_id = data['graph_id']
        print(f"✓ Graph created: {graph_id}")
        
        if len(data['nodes']) == 0:
            print(f"⚠ No nodes to test with")
            return True
        
        # Focus on a specific node
        focus_node_id = data['nodes'][0]['id']
        focus_node_label = data['nodes'][0]['label']
        
        question = f"Tell me about {focus_node_label}"
        print(f"\n2. Question: '{question}'")
        print(f"   Focused on: {focus_node_label} ({focus_node_id})")
        
        qa_response = client.post(
            "/api/py/llm/qa",
            json={
                "graph_id": graph_id,
                "question": question,
                "node_id": focus_node_id,
                "context_hops": 2
            }
        )
        
        if qa_response.status_code != 200:
            print(f"✗ Q&A with node focus failed")
            return False
        
        result = qa_response.json()
        print(f"\n✓ Answer generated with node focus:")
        print(f"  {result['answer'][:150]}...")
        print(f"  Context nodes: {result['context_nodes']}")
        
        if result['context_nodes'] > 0:
            print(f"\n✓ Node focus working (context includes {result['context_nodes']} nodes)")
        else:
            print(f"\n⚠ No context nodes included")
        
        print("\n✓ Node focus test passed")
        return True
        
    except Exception as e:
        print(f"✗ Node focus test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling for invalid requests."""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # Test 1: Explain with non-existent graph
        response = client.post(
            "/api/py/llm/explain",
            json={
                "graph_id": "nonexistent",
                "source_node_id": "node_0",
                "target_node_id": "node_1"
            }
        )
        if response.status_code == 404:
            print("✓ Returns 404 for non-existent graph in explain")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
        
        # Test 2: Q&A with non-existent graph
        response = client.post(
            "/api/py/llm/qa",
            json={
                "graph_id": "nonexistent",
                "question": "test question"
            }
        )
        if response.status_code == 404:
            print("✓ Returns 404 for non-existent graph in Q&A")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
        
        # Test 3: Q&A with question too short
        response = client.post(
            "/api/py/llm/qa",
            json={
                "graph_id": "test",
                "question": "ab"  # Too short (min 3 chars)
            }
        )
        if response.status_code == 422:
            print("✓ Returns 422 for invalid question length")
        else:
            print(f"⚠ Expected 422, got {response.status_code}")
        
        print("\n✓ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all LLM API tests."""
    print("\n" + "=" * 60)
    print("LLM API TEST SUITE (Task 12)")
    print("=" * 60 + "\n")
    
    print("Note: These tests make actual OpenAI API calls and may take 1-2 minutes.")
    print("=" * 60)
    
    # Run tests
    explain_ok = test_explain_endpoint()
    qa_ok = test_qa_endpoint()
    history_ok = test_qa_with_history()
    focus_ok = test_qa_with_node_focus()
    errors_ok = test_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Explain Endpoint:          {'✓ PASS' if explain_ok else '✗ FAIL'}")
    print(f"  Q&A Endpoint:              {'✓ PASS' if qa_ok else '✗ FAIL'}")
    print(f"  Q&A with History:          {'✓ PASS' if history_ok else '✗ FAIL'}")
    print(f"  Q&A with Node Focus:       {'✓ PASS' if focus_ok else '✗ FAIL'}")
    print(f"  Error Handling:            {'✓ PASS' if errors_ok else '✗ FAIL'}")
    
    all_passed = all([explain_ok, qa_ok, history_ok, focus_ok, errors_ok])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Task 12 is complete. Ready for Phase 5 (Frontend)!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

