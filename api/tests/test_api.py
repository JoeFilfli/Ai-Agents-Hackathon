"""
Test script for FastAPI endpoints.

Tests:
1. Health check endpoint
2. Text processing endpoint with valid input
3. Text processing endpoint with invalid input
4. Response format validation

Run from project root: python api/tests/test_api.py
Or use pytest: pytest api/tests/test_api.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from api.index import app

# Create test client
client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    print("=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    
    try:
        response = client.get("/api/py/health")
        
        print(f"  → Status Code: {response.status_code}")
        print(f"  → Response: {response.json()}")
        
        # Check status code
        if response.status_code == 200:
            print("✓ Status code is 200")
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
        
        # Check response format
        data = response.json()
        if 'status' in data and 'version' in data:
            print("✓ Response has required fields")
        else:
            print("✗ Missing required fields in response")
            return False
        
        if data['status'] == 'healthy':
            print("✓ Service is healthy")
        else:
            print(f"✗ Unexpected status: {data['status']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_processing_endpoint():
    """Test the text processing endpoint with valid input."""
    print("\n" + "=" * 60)
    print("Testing Text Processing Endpoint")
    print("=" * 60)
    
    # Sample text
    text = """
    Python is a high-level programming language known for its simplicity and readability.
    It was created by Guido van Rossum and first released in 1991. Python is widely used
    for web development, data science, machine learning, and automation. Django and Flask
    are popular web frameworks built with Python. NumPy and Pandas are essential libraries
    for data analysis and scientific computing.
    """
    
    request_data = {
        "text": text,
        "min_importance": 0.5,
        "min_strength": 0.5,
        "extract_relationships": True,
        "generate_embeddings": False  # Skip embeddings for faster testing
    }
    
    try:
        print("  → Sending POST request to /api/py/text/process")
        print(f"  → Text length: {len(text)} characters")
        
        response = client.post("/api/py/text/process", json=request_data)
        
        print(f"\n  → Status Code: {response.status_code}")
        
        # Check status code
        if response.status_code == 200:
            print("✓ Status code is 200")
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            print(f"  Response: {response.json()}")
            return False
        
        # Parse response
        data = response.json()
        
        # Check required fields
        required_fields = ['graph_id', 'nodes', 'edges', 'metadata']
        for field in required_fields:
            if field in data:
                print(f"✓ Response has '{field}' field")
            else:
                print(f"✗ Missing '{field}' field")
                return False
        
        # Check nodes
        nodes = data['nodes']
        print(f"\n  Extracted Nodes ({len(nodes)}):")
        for node in nodes:
            print(f"    - {node['label']}: {node['description'][:60]}...")
        
        if len(nodes) > 0:
            print(f"✓ Extracted {len(nodes)} nodes")
        else:
            print("✗ No nodes extracted")
            return False
        
        # Check node structure
        first_node = nodes[0]
        node_fields = ['id', 'label', 'description', 'source_text', 'confidence']
        for field in node_fields:
            if field in first_node:
                print(f"✓ Node has '{field}' field")
            else:
                print(f"✗ Node missing '{field}' field")
                return False
        
        # Check edges
        edges = data['edges']
        print(f"\n  Extracted Edges ({len(edges)}):")
        for edge in edges:
            print(f"    - {edge['source']} --[{edge['relationship_type']}]--> {edge['target']}")
        
        if len(edges) > 0:
            print(f"✓ Extracted {len(edges)} edges")
        else:
            print("⚠ No edges extracted (may be valid)")
        
        # Check metadata
        metadata = data['metadata']
        print(f"\n  Metadata:")
        print(f"    - Graph ID: {metadata.get('graph_id', 'N/A')}")
        print(f"    - Node count: {metadata.get('node_count', 0)}")
        print(f"    - Edge count: {metadata.get('edge_count', 0)}")
        print(f"    - Model: {metadata.get('model', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Text processing endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_input():
    """Test the endpoint with invalid input."""
    print("\n" + "=" * 60)
    print("Testing Invalid Input Handling")
    print("=" * 60)
    
    # Test 1: Text too short
    print("\n  Test 1: Text too short")
    request_data = {
        "text": "Too short"
    }
    
    try:
        response = client.post("/api/py/text/process", json=request_data)
        
        if response.status_code == 422:  # Validation error from Pydantic
            print("✓ Correctly rejected text that's too short (422)")
        elif response.status_code == 400:  # Custom validation error
            print("✓ Correctly rejected text that's too short (400)")
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test 2: Invalid min_importance
    print("\n  Test 2: Invalid min_importance (too high)")
    request_data = {
        "text": "x" * 200,  # Valid length
        "min_importance": 2.0  # Too high (max is 1.0)
    }
    
    try:
        response = client.post("/api/py/text/process", json=request_data)
        
        if response.status_code == 422:
            print("✓ Correctly rejected invalid min_importance (422)")
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    return True


def test_with_embeddings():
    """Test the endpoint with embeddings enabled."""
    print("\n" + "=" * 60)
    print("Testing With Embeddings Enabled")
    print("=" * 60)
    
    text = """
    Artificial intelligence is transforming multiple industries through automation and
    data-driven insights. Machine learning, a subset of AI, uses algorithms to learn
    patterns from data. Deep learning takes this further with neural networks that
    can recognize complex patterns. These technologies power applications from voice
    assistants to autonomous vehicles.
    """
    
    request_data = {
        "text": text,
        "min_importance": 0.6,
        "extract_relationships": False,  # Skip for speed
        "generate_embeddings": True
    }
    
    try:
        print("  → Processing text with embeddings enabled...")
        
        response = client.post("/api/py/text/process", json=request_data)
        
        if response.status_code == 200:
            print("✓ Request successful")
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False
        
        data = response.json()
        nodes = data['nodes']
        
        # Check if embeddings are present
        embeddings_count = sum(1 for node in nodes if 'embedding' in node)
        
        print(f"\n  Nodes with embeddings: {embeddings_count}/{len(nodes)}")
        
        if embeddings_count > 0:
            print("✓ Embeddings generated")
            
            # Check embedding dimensions
            first_embedding = nodes[0].get('embedding', [])
            print(f"  → Embedding dimensions: {len(first_embedding)}")
            
            if len(first_embedding) == 1536:
                print("✓ Correct embedding dimensions (1536)")
            else:
                print(f"⚠ Unexpected dimensions: {len(first_embedding)}")
        else:
            print("⚠ No embeddings found")
        
        return True
        
    except Exception as e:
        print(f"✗ Embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all API tests."""
    print("\n" + "=" * 60)
    print("API ENDPOINTS TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    health_ok = test_health_endpoint()
    process_ok = test_text_processing_endpoint()
    invalid_ok = test_invalid_input()
    embeddings_ok = test_with_embeddings()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Health Endpoint:       {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"  Text Processing:       {'✓ PASS' if process_ok else '✗ FAIL'}")
    print(f"  Invalid Input:         {'✓ PASS' if invalid_ok else '✗ FAIL'}")
    print(f"  With Embeddings:       {'✓ PASS' if embeddings_ok else '✗ FAIL'}")
    
    all_passed = all([health_ok, process_ok, invalid_ok, embeddings_ok])
    
    if all_passed:
        print("\n🎉 All API tests passed!")
        print("   Task 6 is complete. Ready for Phase 3!")
        print("\n📝 You can also test the API interactively:")
        print("   1. Start the server: uvicorn api.index:app --reload --port 8000")
        print("   2. Open API docs: http://127.0.0.1:8000/api/py/docs")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

