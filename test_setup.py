"""
Simple test script to verify OpenAI API connection and dependencies.
Run this after setting up your .env.local file with OPENAI_API_KEY.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

def test_imports():
    """Test that all required packages can be imported."""
    print("✓ Testing package imports...")
    
    try:
        import fastapi
        print("  ✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"  ✗ FastAPI import failed: {e}")
        return False
    
    try:
        import openai
        print("  ✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"  ✗ OpenAI import failed: {e}")
        return False
    
    try:
        import networkx
        print("  ✓ NetworkX imported successfully")
    except ImportError as e:
        print(f"  ✗ NetworkX import failed: {e}")
        return False
    
    try:
        import pydantic
        print("  ✓ Pydantic imported successfully")
    except ImportError as e:
        print(f"  ✗ Pydantic import failed: {e}")
        return False
    
    return True


import os
from openai import OpenAI

def test_openai_connection():
    """Test OpenAI API connection with a simple request."""
    print("\n✓ Testing OpenAI API connection...")

    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("  ✗ OPENAI_API_KEY not found in environment variables")
        print("  → Please create .env.local file with your API key")
        print("  → Copy env.example to .env.local and add your key")
        return False
    
    if api_key == 'sk-your-api-key-here':
        print("  ✗ OPENAI_API_KEY is still the placeholder value")
        print("  → Please replace with your actual API key in .env.local")
        return False
    
    print(f"  ✓ API key found (starts with: {api_key[:10]}...)")

    # Get model from environment or use default
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    print(f"  ✓ Using model: {model}")

    # Test a simple API call
    try:
        client = OpenAI(api_key=api_key)

        print("  → Making a test API call...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'API connection successful!'"}
            ],
            max_tokens=20
        )

        result = response.choices[0].message.content
        print(f"  ✓ OpenAI API response: {result}")
        return True

    except Exception as e:
        print(f"  ✗ OpenAI API call failed: {e}")
        return False


def test_networkx():
    """Test NetworkX graph creation."""
    print("\n✓ Testing NetworkX graph creation...")
    
    try:
        import networkx as nx
        
        # Create a simple test graph
        G = nx.Graph()
        G.add_node("Python", type="language")
        G.add_node("Machine Learning", type="field")
        G.add_edge("Python", "Machine Learning", relationship="used_in")
        
        print(f"  ✓ Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Test path finding
        if nx.has_path(G, "Python", "Machine Learning"):
            print("  ✓ Path finding works correctly")
        
        return True
        
    except Exception as e:
        print(f"  ✗ NetworkX test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Project Setup")
    print("=" * 60)
    
    # Run tests
    imports_ok = test_imports()
    openai_ok = test_openai_connection()
    networkx_ok = test_networkx()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"  Package Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"  OpenAI Connection: {'✓ PASS' if openai_ok else '✗ FAIL'}")
    print(f"  NetworkX Functionality: {'✓ PASS' if networkx_ok else '✗ FAIL'}")
    
    if imports_ok and openai_ok and networkx_ok:
        print("\n🎉 All tests passed! Setup is complete.")
        print("   You can now proceed to Task 2.")
        return True
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

