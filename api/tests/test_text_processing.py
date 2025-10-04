"""
Test script for text processing service.

Tests:
1. Input validation
2. Concept extraction from sample text
3. Response format validation

Run from project root: python api/tests/test_text_processing.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')


def test_validation():
    """Test input validation."""
    print("=" * 60)
    print("Testing Input Validation")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        # Test empty text
        is_valid, msg = service.validate_text_input("")
        if not is_valid and "empty" in msg.lower():
            print("✓ Empty text correctly rejected")
        else:
            print("✗ Empty text validation failed")
            return False
        
        # Test too short text
        short_text = "Too short"
        is_valid, msg = service.validate_text_input(short_text)
        if not is_valid and "100" in msg:
            print(f"✓ Short text correctly rejected ({len(short_text)} chars)")
        else:
            print("✗ Short text validation failed")
            return False
        
        # Test too long text
        long_text = "x" * 51000
        is_valid, msg = service.validate_text_input(long_text)
        if not is_valid and "50,000" in msg or "50000" in msg:
            print(f"✓ Long text correctly rejected ({len(long_text)} chars)")
        else:
            print("✗ Long text validation failed")
            return False
        
        # Test valid text
        valid_text = "x" * 150
        is_valid, msg = service.validate_text_input(valid_text)
        if is_valid and msg == "":
            print(f"✓ Valid text accepted ({len(valid_text)} chars)")
        else:
            print(f"✗ Valid text validation failed: {msg}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Validation testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concept_extraction():
    """Test concept extraction with sample text about machine learning."""
    print("\n" + "=" * 60)
    print("Testing Concept Extraction")
    print("=" * 60)
    
    # Sample text about machine learning
    sample_text = """
Machine learning is a subset of artificial intelligence that focuses on enabling 
computers to learn from data without being explicitly programmed. It uses algorithms 
that can identify patterns and make decisions with minimal human intervention.

There are three main types of machine learning: supervised learning, unsupervised 
learning, and reinforcement learning. Supervised learning uses labeled data to train 
models, where the algorithm learns to map inputs to known outputs. Unsupervised 
learning works with unlabeled data to discover hidden patterns or groupings. 
Reinforcement learning trains agents to make sequences of decisions by rewarding 
desired behaviors and penalizing undesired ones.

Neural networks are a key technology in modern machine learning, inspired by the 
structure of the human brain. Deep learning, which uses neural networks with many 
layers, has achieved remarkable success in areas like computer vision, natural 
language processing, and speech recognition. These technologies are transforming 
industries from healthcare to finance to autonomous vehicles.
"""
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        print(f"  → Input text length: {len(sample_text)} characters")
        print("  → Calling GPT-4 to extract concepts...")
        
        # Extract concepts (unlimited - LLM decides)
        concepts = service.extract_concepts(
            text=sample_text,
            min_importance=0.6
        )
        
        print(f"\n✓ Extraction successful! Found {len(concepts)} concepts:\n")
        
        # Display extracted concepts
        for i, concept in enumerate(concepts, 1):
            name = concept.get('name', 'Unknown')
            description = concept.get('description', 'No description')
            importance = concept.get('importance', 0)
            source_text = concept.get('source_text', 'No source')
            
            print(f"  {i}. {name}")
            print(f"     Importance: {importance:.2f}")
            print(f"     Description: {description}")
            print(f"     Source: \"{source_text[:100]}...\"")
            print()
        
        # Validate response format
        if len(concepts) > 0:
            first_concept = concepts[0]
            
            # Check required fields
            required_fields = ['name', 'description', 'importance', 'source_text']
            missing_fields = [f for f in required_fields if f not in first_concept]
            
            if missing_fields:
                print(f"✗ Missing required fields: {missing_fields}")
                return False
            
            print("✓ All required fields present (name, description, importance, source_text)")
            
            # Check importance is in valid range
            if 0 <= first_concept['importance'] <= 1:
                print("✓ Importance scores in valid range (0-1)")
            else:
                print(f"✗ Invalid importance score: {first_concept['importance']}")
                return False
            
            return True
        else:
            print("✗ No concepts extracted (expected at least 1)")
            return False
        
    except Exception as e:
        print(f"✗ Concept extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_process_text():
    """Test the full process_text method."""
    print("\n" + "=" * 60)
    print("Testing Full Text Processing")
    print("=" * 60)
    
    sample_text = """
Python is a high-level, interpreted programming language known for its simplicity 
and readability. Created by Guido van Rossum and first released in 1991, Python 
emphasizes code readability with its use of significant indentation. It supports 
multiple programming paradigms including procedural, object-oriented, and functional 
programming.

Python has become one of the most popular languages for data science, machine learning, 
and web development. Its extensive standard library and vast ecosystem of third-party 
packages make it suitable for a wide range of applications. Popular frameworks like 
Django and Flask have made Python a go-to choice for web development, while libraries 
like NumPy, Pandas, and TensorFlow dominate the data science landscape.
"""
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        print("  → Processing text...")
        
        # Process text (unlimited - LLM decides)
        result = service.process_text(
            text=sample_text,
            min_importance=0.5
        )
        
        print("\n✓ Processing successful!\n")
        
        # Check response structure
        if 'concepts' not in result:
            print("✗ Missing 'concepts' in response")
            return False
        print("✓ Response contains 'concepts'")
        
        if 'metadata' not in result:
            print("✗ Missing 'metadata' in response")
            return False
        print("✓ Response contains 'metadata'")
        
        # Check metadata (no max_concepts anymore - unlimited extraction)
        metadata = result['metadata']
        required_metadata = ['model', 'concepts_found', 'input_length', 'chunk_count']
        for field in required_metadata:
            if field not in metadata:
                print(f"✗ Missing metadata field: {field}")
                return False
        print("✓ All metadata fields present")
        
        # Display summary
        print(f"\n  Metadata:")
        print(f"    - Model used: {metadata['model']}")
        print(f"    - Concepts found: {metadata['concepts_found']}")
        print(f"    - Input length: {metadata['input_length']} chars")
        
        return True
        
    except Exception as e:
        print(f"✗ Process text failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all text processing tests."""
    print("\n" + "=" * 60)
    print("TEXT PROCESSING SERVICE TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    validation_ok = test_validation()
    extraction_ok = test_concept_extraction()
    process_ok = test_process_text()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Input Validation:     {'✓ PASS' if validation_ok else '✗ FAIL'}")
    print(f"  Concept Extraction:   {'✓ PASS' if extraction_ok else '✗ FAIL'}")
    print(f"  Full Text Processing: {'✓ PASS' if process_ok else '✗ FAIL'}")
    
    all_passed = all([validation_ok, extraction_ok, process_ok])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Task 3 is complete. Ready for Task 4!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

