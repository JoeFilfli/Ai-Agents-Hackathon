# Bug Fix: JSON Parsing Error

## Problem
Frontend was getting a JSON parsing error:
```
Error processing text: SyntaxError: Unexpected token 'I', "Internal S"... is not valid JSON
```

Backend showed 200 OK, suggesting the response was malformed JSON.

## Root Causes Identified

1. **Frontend sending deprecated parameter**: `max_concepts` was removed from the API but frontend was still sending it
2. **Unsafe error messages**: Backend error handling included raw LLM responses in error messages, which could break JSON serialization
3. **No validation**: No validation of LLM response structure before processing
4. **Poor error handling**: Frontend couldn't distinguish between JSON and non-JSON errors

## Fixes Applied

### 1. Frontend Updates (`app/page.tsx`)

**BEFORE:**
```typescript
body: JSON.stringify({
  text: inputText,
  max_concepts: 10,  // ❌ Removed parameter
  min_importance: 0.5,
  min_strength: 0.5,
  // ...
})
```

**AFTER:**
```typescript
body: JSON.stringify({
  text: inputText,
  min_importance: 0.0,  // ✅ 0.0 = LLM decides (unlimited)
  min_strength: 0.0,    // ✅ 0.0 = keep all edges
  extract_relationships: true,
  generate_embeddings: true,
})
```

**Error Handling Improved:**
- Read response text once (avoid double-read bug)
- Show first 100 chars of response if JSON parsing fails
- Log full error details to console for debugging

### 2. Backend Error Handling (`api/services/text_processing.py`)

**Added Safe Error Messages:**
```python
except json.JSONDecodeError as e:
    # Safely truncate response without breaking JSON strings
    safe_preview = raw[:500].replace('"', "'").replace('\n', ' ')
    error_msg = f"Failed to parse LLM JSON response: {str(e)}. Preview: {safe_preview}"
    raise Exception(error_msg)
```

**Why this matters**: Raw LLM responses can contain characters that break JSON when included in error detail objects.

### 3. Response Validation

**Concepts Validation:**
```python
# Validate concepts is a list
if not isinstance(concepts, list):
    raise Exception(f"Expected 'concepts' to be a list, got {type(concepts)}")

# Filter out invalid concepts and ensure required fields
valid_concepts = []
for c in concepts:
    if not isinstance(c, dict) or not c.get("name"):
        continue
    # Set defaults for missing fields
    c.setdefault("description", "")
    c.setdefault("importance", 0.5)
    c.setdefault("level", 1)
    c.setdefault("parent", None)
    valid_concepts.append(c)
```

**Relationships Validation:**
```python
# Ensure rels is a list
if not isinstance(rels, list):
    print(f"Warning: relationships is not a list, got {type(rels)}")
    rels = []

# Validate each relationship is a dict
for r in rels:
    if not isinstance(r, dict):
        continue
    # ... process valid relationships only
```

### 4. TypeScript Types Updated (`app/types/graph.ts`)

**BEFORE:**
```typescript
export interface TextProcessRequest {
  text: string;
  options?: {
    maxNodes?: number;  // ❌ Wrong structure
    minConfidence?: number;
  };
}
```

**AFTER:**
```typescript
export interface TextProcessRequest {
  text: string;
  min_importance?: number;      // ✅ Matches backend
  min_strength?: number;
  extract_relationships?: boolean;
  generate_embeddings?: boolean;
}
```

### 5. Documentation Updated

- ✅ `app/components/README.md` - Updated example code
- ✅ API endpoint documentation - Removed `max_concepts`
- ✅ Test files - Updated to use new parameters

## Testing

### Quick Test
1. Start backend: `cd api && uvicorn index:app --reload`
2. Start frontend: `npm run dev`
3. Paste text > 100 characters
4. Click "Generate Graph"
5. Should now work without JSON errors

### Verify Error Handling
Test with invalid input to ensure errors are properly formatted:
```bash
curl -X POST http://localhost:3000/api/py/text/process \
  -H "Content-Type: application/json" \
  -d '{"text": "too short"}'
```

Should return proper JSON error (not plain text).

## What Changed From Original Implementation

| Feature | Before | After |
|---------|--------|-------|
| Max concepts | Hard limit (10-50) | Unlimited (LLM decides) |
| Min importance | Required | Optional (default 0.0) |
| Min strength | Required | Optional (default 0.0) |
| Error messages | Unsafe (raw LLM) | Safe (sanitized) |
| Validation | None | Full validation |
| Frontend types | Mismatched | Matches backend |

## Files Modified

### Backend
- `api/services/text_processing.py` - Safe error handling + validation
- `api/index.py` - Already updated in previous commit
- `api/tests/*.py` - Already updated in previous commit

### Frontend
- `app/page.tsx` - Removed `max_concepts`, improved error handling
- `app/types/graph.ts` - Updated interface to match backend
- `app/components/README.md` - Updated example code

## Prevention

To prevent similar issues in the future:

1. **Always validate LLM responses** before using them
2. **Sanitize error messages** that include user/LLM content
3. **Keep frontend/backend types in sync** (consider generating types from backend)
4. **Test with real LLM responses** that might have unexpected structures
5. **Read response body only once** in fetch handlers

## Next Steps

If the error still occurs:

1. Check browser console for the full error message
2. Check backend logs for LLM response preview
3. Look at Network tab to see actual response body
4. Try with shorter text first (minimize LLM response size)
5. Verify OpenAI API key is valid and has credits

## Success Criteria

✅ Frontend sends correct parameters (no `max_concepts`)  
✅ Backend returns valid JSON (even on errors)  
✅ Error messages are safe and informative  
✅ LLM responses are validated before use  
✅ No more "Unexpected token" JSON errors  

