# Services

This directory contains business logic services for the mindmap system.

## Services

### `text_processing.py` - Text Processing Service

Extracts concepts and relationships from raw text using OpenAI GPT-4.

**Key Features:**
- Input validation (100-50,000 characters)
- Concept extraction with GPT-4
- Relationship extraction between concepts
- Structured JSON output
- Configurable parameters (max concepts, min importance, min strength)

**Usage:**

```python
from api.services.text_processing import TextProcessingService

# Initialize service
service = TextProcessingService()

# Extract concepts
concepts = service.extract_concepts(
    text="Your text here...",
    max_concepts=10,
    min_importance=0.6
)

# Or use the full processing method (extracts concepts + relationships)
result = service.process_text(
    text="Your text here...",
    max_concepts=10,
    min_importance=0.5,
    min_strength=0.5,
    extract_rels=True
)

# Result contains:
# {
#   "concepts": [
#     {
#       "name": "Concept Name",
#       "description": "Brief description",
#       "importance": 0.95,
#       "source_text": "Relevant excerpt"
#     }
#   ],
#   "relationships": [
#     {
#       "source": "Concept A",
#       "target": "Concept B",
#       "type": "is-a",
#       "strength": 0.9,
#       "description": "Explanation of relationship"
#     }
#   ],
#   "metadata": {
#     "model": "gpt-4o-mini",
#     "concepts_found": 5,
#     "relationships_found": 3,
#     ...
#   }
# }

# Or extract relationships separately
relationships = service.extract_relationships(
    text="Your text...",
    concepts=concepts_list,
    min_strength=0.5
)
```

**Validation Rules:**
- Minimum length: 100 characters
- Maximum length: 50,000 characters
- Text cannot be empty

**Environment Variables:**
- `OPENAI_API_KEY` - Required
- `OPENAI_MODEL` - Optional (default: gpt-4o-mini)

## Testing

Run tests for text processing:

```bash
python api/tests/test_text_processing.py
```

This tests:
- ✓ Input validation
- ✓ Concept extraction
- ✓ Response format
- ✓ Full processing workflow

## Future Services

Coming in next phases:
- `graph_service.py` - Graph operations and traversal
- `llm_service.py` - Relationship explanations and Q&A
- `tts_service.py` - Text-to-speech synthesis

