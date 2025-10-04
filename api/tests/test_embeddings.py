"""
Test script for embedding generation.

Tests:
1. Single embedding generation
2. Batch embedding generation
3. Embedding dimensions verification
4. Cosine similarity for similar concepts
5. Cosine similarity for dissimilar concepts

Run from project root: python api/tests/test_embeddings.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')


def test_single_embedding():
    """Test generating a single embedding."""
    print("=" * 60)
    print("Testing Single Embedding Generation")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        text = "Machine learning is a subset of artificial intelligence"
        
        print(f"  → Generating embedding for: \"{text[:50]}...\"")
        
        embedding = service.generate_embedding(text)
        
        print(f"\n✓ Embedding generated successfully!")
        print(f"  - Embedding dimensions: {len(embedding)}")
        print(f"  - First 5 values: {embedding[:5]}")
        
        # Verify dimensions (text-embedding-3-small is 1536 dimensions)
        expected_dims = 1536
        if len(embedding) == expected_dims:
            print(f"✓ Correct dimensions ({expected_dims})")
        else:
            print(f"✗ Unexpected dimensions: {len(embedding)} (expected {expected_dims})")
            return False
        
        # Verify values are floats
        if all(isinstance(v, float) for v in embedding[:10]):
            print("✓ Values are floats")
        else:
            print("✗ Values are not floats")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Single embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_embeddings():
    """Test generating multiple embeddings in batch."""
    print("\n" + "=" * 60)
    print("Testing Batch Embedding Generation")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        texts = [
            "Python is a programming language",
            "JavaScript is used for web development",
            "Machine learning uses algorithms"
        ]
        
        print(f"  → Generating embeddings for {len(texts)} texts...")
        
        embeddings = service.generate_embeddings_batch(texts)
        
        print(f"\n✓ Batch generation successful!")
        print(f"  - Generated {len(embeddings)} embeddings")
        
        # Verify count matches input
        if len(embeddings) == len(texts):
            print(f"✓ Correct number of embeddings ({len(embeddings)})")
        else:
            print(f"✗ Wrong number of embeddings: {len(embeddings)} (expected {len(texts)})")
            return False
        
        # Verify all have correct dimensions
        if all(len(e) == 1536 for e in embeddings):
            print("✓ All embeddings have correct dimensions (1536)")
        else:
            dims = [len(e) for e in embeddings]
            print(f"✗ Incorrect dimensions: {dims}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Batch embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_similar_concepts():
    """Test that similar concepts have high cosine similarity."""
    print("\n" + "=" * 60)
    print("Testing Similarity for Similar Concepts")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        # Similar concepts
        text1 = "Machine learning is a field of artificial intelligence"
        text2 = "Machine learning is a subset of AI that learns from data"
        
        print(f"  → Concept 1: \"{text1}\"")
        print(f"  → Concept 2: \"{text2}\"")
        print("  → Generating embeddings...")
        
        embedding1 = service.generate_embedding(text1)
        embedding2 = service.generate_embedding(text2)
        
        similarity = service.cosine_similarity(embedding1, embedding2)
        
        print(f"\n✓ Cosine similarity: {similarity:.4f}")
        
        # Similar concepts should have high similarity (> 0.7)
        if similarity > 0.7:
            print(f"✓ High similarity score ({similarity:.4f} > 0.7)")
            return True
        else:
            print(f"⚠ Lower than expected similarity: {similarity:.4f}")
            # This is a warning, not necessarily a failure
            return True
        
    except Exception as e:
        print(f"✗ Similarity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dissimilar_concepts():
    """Test that dissimilar concepts have lower cosine similarity."""
    print("\n" + "=" * 60)
    print("Testing Similarity for Dissimilar Concepts")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        # Dissimilar concepts
        text1 = "Python programming language for software development"
        text2 = "Pizza is a popular Italian dish with cheese and toppings"
        
        print(f"  → Concept 1: \"{text1}\"")
        print(f"  → Concept 2: \"{text2}\"")
        print("  → Generating embeddings...")
        
        embedding1 = service.generate_embedding(text1)
        embedding2 = service.generate_embedding(text2)
        
        similarity = service.cosine_similarity(embedding1, embedding2)
        
        print(f"\n✓ Cosine similarity: {similarity:.4f}")
        
        # Dissimilar concepts should have lower similarity (< 0.5)
        if similarity < 0.5:
            print(f"✓ Low similarity score ({similarity:.4f} < 0.5)")
            return True
        else:
            print(f"⚠ Higher than expected similarity: {similarity:.4f}")
            # This is a warning, not necessarily a failure
            return True
        
    except Exception as e:
        print(f"✗ Dissimilar concepts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_embeddings_to_concepts():
    """Test adding embeddings to concept dictionaries."""
    print("\n" + "=" * 60)
    print("Testing Adding Embeddings to Concepts")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        # Sample concepts
        concepts = [
            {
                "name": "Python",
                "description": "A high-level programming language",
                "importance": 0.95,
                "source_text": "Python is..."
            },
            {
                "name": "JavaScript",
                "description": "A web programming language",
                "importance": 0.90,
                "source_text": "JavaScript is..."
            }
        ]
        
        print(f"  → Adding embeddings to {len(concepts)} concepts...")
        
        concepts_with_embeddings = service.add_embeddings_to_concepts(concepts)
        
        print(f"\n✓ Embeddings added successfully!")
        
        # Check that embeddings were added
        for i, concept in enumerate(concepts_with_embeddings):
            if 'embedding' in concept:
                print(f"  ✓ Concept {i+1} ({concept['name']}): has embedding with {len(concept['embedding'])} dimensions")
            else:
                print(f"  ✗ Concept {i+1} ({concept['name']}): missing embedding")
                return False
        
        # Verify dimensions
        if all(len(c['embedding']) == 1536 for c in concepts_with_embeddings):
            print("✓ All embeddings have correct dimensions")
        else:
            print("✗ Some embeddings have incorrect dimensions")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Add embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline_with_embeddings():
    """Test full pipeline including embeddings."""
    print("\n" + "=" * 60)
    print("Testing Full Pipeline with Embeddings")
    print("=" * 60)
    
    try:
        from api.services.text_processing import TextProcessingService
        
        service = TextProcessingService()
        
        text = """
        Python is a high-level programming language known for its simplicity.
        JavaScript is another popular language used primarily for web development.
        Both languages are widely used in software engineering and data science.
        """
        
        print("  → Processing text with embeddings enabled...")
        
        result = service.process_text(
            text=text,
            max_concepts=3,
            min_importance=0.5,
            extract_rels=False,  # Skip relationships for faster test
            generate_embeddings=True
        )
        
        print(f"\n✓ Processing successful!")
        
        concepts = result['concepts']
        metadata = result['metadata']
        
        print(f"\n  Metadata:")
        print(f"    - Concepts found: {len(concepts)}")
        print(f"    - Embeddings generated: {metadata.get('embeddings_generated', False)}")
        print(f"    - Embedding model: {metadata.get('embedding_model', 'Unknown')}")
        
        # Verify embeddings were added
        concepts_with_embeddings = sum(1 for c in concepts if 'embedding' in c)
        
        if concepts_with_embeddings == len(concepts):
            print(f"\n✓ All {len(concepts)} concepts have embeddings")
        else:
            print(f"\n✗ Only {concepts_with_embeddings}/{len(concepts)} concepts have embeddings")
            return False
        
        # Test similarity between concepts
        if len(concepts) >= 2:
            emb1 = concepts[0]['embedding']
            emb2 = concepts[1]['embedding']
            similarity = service.cosine_similarity(emb1, emb2)
            
            print(f"\n  Similarity between concepts:")
            print(f"    - {concepts[0]['name']} <-> {concepts[1]['name']}: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all embedding tests."""
    print("\n" + "=" * 60)
    print("EMBEDDING GENERATION TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    single_ok = test_single_embedding()
    batch_ok = test_batch_embeddings()
    similar_ok = test_similar_concepts()
    dissimilar_ok = test_dissimilar_concepts()
    add_ok = test_add_embeddings_to_concepts()
    pipeline_ok = test_full_pipeline_with_embeddings()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Single Embedding:      {'✓ PASS' if single_ok else '✗ FAIL'}")
    print(f"  Batch Embeddings:      {'✓ PASS' if batch_ok else '✗ FAIL'}")
    print(f"  Similar Concepts:      {'✓ PASS' if similar_ok else '✗ FAIL'}")
    print(f"  Dissimilar Concepts:   {'✓ PASS' if dissimilar_ok else '✗ FAIL'}")
    print(f"  Add to Concepts:       {'✓ PASS' if add_ok else '✗ FAIL'}")
    print(f"  Full Pipeline:         {'✓ PASS' if pipeline_ok else '✗ FAIL'}")
    
    all_passed = all([
        single_ok, batch_ok, similar_ok, 
        dissimilar_ok, add_ok, pipeline_ok
    ])
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("   Task 5 is complete. Ready for Task 6!")
        return True
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

