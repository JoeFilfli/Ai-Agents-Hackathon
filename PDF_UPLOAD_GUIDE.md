# PDF Upload Feature - Setup Guide

## Overview

Your Interactive Mindmap app now supports uploading **PDF files** to extract text automatically! This allows you to analyze documents without manually copying text.

## Features

✅ **PDF Upload** - Upload PDF documents and extract all text  
✅ **File Validation** - Automatic type and size validation  
✅ **No Minimum Length** - Extracted text has no character minimum  
✅ **Error Handling** - Clear error messages for troubleshooting  

## Supported File Types

- **PDFs**: `.pdf` only

**File Size Limit**: 10MB maximum

## Installation Steps

### 1. Install Python Dependencies

Install the required Python packages:

```bash
# Activate your virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

This installs:
- `pypdf==5.1.0` - For PDF text extraction
- `python-multipart==0.0.9` - For file upload handling in FastAPI

### 2. Restart Backend

Restart your FastAPI backend to load the new dependencies:

```bash
python start_backend.py
```

## How to Use

### 1. Start the Application

```bash
# Terminal 1 - Backend
python start_backend.py

# Terminal 2 - Frontend
npm run dev
```

### 2. Upload a PDF File

1. Navigate to http://localhost:3000
2. Click the **"Upload PDF"** button
3. Select your PDF file
4. The text will be extracted automatically and appear in the text area
5. Click **"Generate Knowledge Graph"** to process

### 3. Or Paste Text Manually

You can still paste text manually as before. The file upload is an additional option.

## API Endpoints

### File Extraction Endpoint

```
POST /api/py/file/extract
Content-Type: multipart/form-data

Request:
- file: (binary PDF file upload)

Response:
{
  "text": "Extracted text content...",
  "filename": "document.pdf",
  "file_type": "pdf",
  "char_count": 1234
}
```

## Troubleshooting

### "Failed to extract text from PDF"

**Possible causes**:
- PDF is encrypted or password-protected
- PDF contains only images (scanned document)
- PDF is corrupted

**Solutions**:
- Remove password protection from PDF
- For scanned PDFs (images), use OCR software to convert to text first
- Try a different PDF file

### "Unsupported file type"

**Problem**: You're trying to upload a non-PDF file.

**Solution**: Only PDF files (`.pdf`) are supported. Convert your document to PDF first.

### "File too large"

**Problem**: File exceeds 10MB limit.

**Solution**: 
- Compress your PDF (many online tools available)
- Split large documents into smaller parts

## Technical Details

### PDF Extraction

Uses `pypdf` library to read PDF files and extract text from each page. Works with:
- Text-based PDFs
- PDFs with selectable text
- Multi-page documents

**Note**: Does NOT work with:
- Scanned PDFs (images only)
- Encrypted/protected PDFs
- PDFs with only images

### Security Features

- File type validation (MIME type and extension)
- File size limit (10MB)
- Secure file handling (no files saved to disk)
- Error sanitization

## Character Requirements

### Manual Text Entry
- **Minimum**: 100 characters required
- **Maximum**: 50,000 characters

### PDF Upload
- **Minimum**: No minimum! Any amount of extracted text is valid
- **Maximum**: 50,000 characters

This makes it easy to process PDF documents with varying amounts of text content.

## Next Steps

Once text is extracted from your PDF:
1. The text appears in the text area
2. You can edit it if needed
3. Click "Generate Knowledge Graph"
4. The system processes the text as usual

Enjoy analyzing PDFs! 📄✨

