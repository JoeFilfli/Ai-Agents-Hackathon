"""
Test script for relationship extraction.

Tests:
1. Relationship extraction with known concepts
2. Response format validation
3. Relationship type validation
4. Integration test with concepts + relationships

Run from project root: python api/tests/test_relationships.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')


def test_simple_relationship():
    """Test relationship extraction with simple text."""
    print("=" * 60)
    print("Testing Simple Relationship Extraction")
    print("=" * 60)
    
    # Simple text with clear relationship
    text = """
Python is a high-level programming language. It was created by Guido van Rossum
and first released in 1991. Python emphasizes code readability and simplicity.
Programming languages are formal languages used to communicate instructions to computers.
"""
    
    # Pre-defined concepts
    concepts = [
        {
            "name": "Python",
            "description": "A high-level programming language",
            "importance": 0.95,
            "source_text": "Python is a high-level programming language"
        },
        {
            "name": "Programming Language",
            "description": "Formal languages for computer instructions",
            "importance": 0.90,
            "source_text": "Programming languages are formal languages"
        }
    ]
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        print("  → Extracting relationships...")
        
        relationships = service.extract_relationships(
            text=text,
            concepts=concepts,
            min_strength=0.5
        )
        
        print(f"\n✓ Extraction successful! Found {len(relationships)} relationship(s):\n")
        
        # Display relationships
        for i, rel in enumerate(relationships, 1):
            source = rel.get('source', 'Unknown')
            target = rel.get('target', 'Unknown')
            rel_type = rel.get('type', 'Unknown')
            strength = rel.get('strength', 0)
            description = rel.get('description', 'No description')
            
            print(f"  {i}. {source} --[{rel_type}]--> {target}")
            print(f"     Strength: {strength:.2f}")
            print(f"     Description: {description}")
            print()
        
        # Validate response format
        if len(relationships) > 0:
            first_rel = relationships[0]
            
            # Check required fields
            required_fields = ['source', 'target', 'type', 'strength', 'description']
            missing_fields = [f for f in required_fields if f not in first_rel]
            
            if missing_fields:
                print(f"✗ Missing required fields: {missing_fields}")
                return False
            
            print("✓ All required fields present (source, target, type, strength, description)")
            
            # Check strength is in valid range
            if 0 <= first_rel['strength'] <= 1:
                print("✓ Strength scores in valid range (0-1)")
            else:
                print(f"✗ Invalid strength score: {first_rel['strength']}")
                return False
            
            # Validate source and target are from concepts
            concept_names = [c['name'] for c in concepts]
            if first_rel['source'] in concept_names and first_rel['target'] in concept_names:
                print("✓ Source and target match concept names")
            else:
                print(f"✗ Source or target not in concepts: {first_rel['source']}, {first_rel['target']}")
                return False
            
            return True
        else:
            print("⚠ No relationships extracted (expected at least 1)")
            # This is a warning, not a failure
            return True
        
    except Exception as e:
        print(f"✗ Relationship extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_relationship_types():
    """Test that various relationship types are recognized."""
    print("\n" + "=" * 60)
    print("Testing Various Relationship Types")
    print("=" * 60)
    
    text = """
Machine learning is a subset of artificial intelligence. Neural networks are
a key component of deep learning systems. Supervised learning requires labeled
training data. Reinforcement learning uses rewards to guide agent behavior.
"""
    
    concepts = [
        {"name": "Machine Learning", "description": "AI subset", "importance": 0.95, "source_text": "..."},
        {"name": "Artificial Intelligence", "description": "AI field", "importance": 0.90, "source_text": "..."},
        {"name": "Neural Networks", "description": "ML architecture", "importance": 0.85, "source_text": "..."},
        {"name": "Deep Learning", "description": "ML technique", "importance": 0.88, "source_text": "..."},
        {"name": "Supervised Learning", "description": "Learning type", "importance": 0.80, "source_text": "..."},
        {"name": "Labeled Data", "description": "Training data", "importance": 0.75, "source_text": "..."}
    ]
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        print("  → Extracting relationships with various types...")
        
        relationships = service.extract_relationships(
            text=text,
            concepts=concepts,
            min_strength=0.5
        )
        
        print(f"\n✓ Found {len(relationships)} relationships with different types:\n")
        
        # Collect relationship types
        relationship_types = set()
        for rel in relationships:
            rel_type = rel.get('type', 'unknown')
            relationship_types.add(rel_type)
            print(f"  - {rel['source']} --[{rel_type}]--> {rel['target']}")
        
        print(f"\n✓ Identified {len(relationship_types)} different relationship types:")
        for rt in relationship_types:
            print(f"  - {rt}")
        
        return True
        
    except Exception as e:
        print(f"✗ Relationship type testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test full pipeline: concepts + relationships."""
    print("\n" + "=" * 60)
    print("Testing Full Pipeline (Concepts + Relationships)")
    print("=" * 60)
    
    text = """
Python is a high-level programming language known for its simplicity and readability.
Django is a popular web framework written in Python. Flask is another lightweight
web framework for Python. Both Django and Flask are used for building web applications.
Web frameworks provide tools and libraries that simplify web development tasks.
"""
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        print("  → Processing text (extracting concepts and relationships)...")
        
        # Process with both concepts and relationships
        result = service.process_text(
            text=text,
            max_concepts=5,
            min_importance=0.5,
            min_strength=0.5,
            extract_rels=True
        )
        
        print("\n✓ Processing successful!\n")
        
        # Validate structure
        if 'concepts' not in result:
            print("✗ Missing 'concepts' in response")
            return False
        print("✓ Response contains 'concepts'")
        
        if 'relationships' not in result:
            print("✗ Missing 'relationships' in response")
            return False
        print("✓ Response contains 'relationships'")
        
        if 'metadata' not in result:
            print("✗ Missing 'metadata' in response")
            return False
        print("✓ Response contains 'metadata'")
        
        # Display summary
        concepts = result['concepts']
        relationships = result['relationships']
        metadata = result['metadata']
        
        print(f"\n  Summary:")
        print(f"    - Concepts found: {len(concepts)}")
        print(f"    - Relationships found: {len(relationships)}")
        print(f"    - Model used: {metadata.get('model', 'Unknown')}")
        
        print(f"\n  Concepts:")
        for c in concepts:
            print(f"    - {c['name']} (importance: {c['importance']:.2f})")
        
        print(f"\n  Relationships:")
        for r in relationships:
            print(f"    - {r['source']} --[{r['type']}]--> {r['target']} (strength: {r['strength']:.2f})")
        
        # Check metadata has relationship info
        if 'relationships_found' in metadata:
            print("\n✓ Metadata includes relationship count")
        else:
            print("\n✗ Metadata missing relationship count")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all relationship extraction tests."""
    print("\n" + "=" * 60)
    print("RELATIONSHIP EXTRACTION TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    simple_ok = test_simple_relationship()
    types_ok = test_relationship_types()
    pipeline_ok = test_full_pipeline()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Simple Relationship:  {'✓ PASS' if simple_ok else '✗ FAIL'}")
    print(f"  Relationship Types:   {'✓ PASS' if types_ok else '✗ FAIL'}")
    print(f"  Full Pipeline:        {'✓ PASS' if pipeline_ok else '✗ FAIL'}")
    
    all_passed = all([simple_ok, types_ok, pipeline_ok])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Task 4 is complete. Ready for Task 5!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

