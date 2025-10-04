# File Upload Feature - Setup Guide

## Overview

Your Interactive Mindmap app now supports uploading **PDF files** and **images** to extract text automatically! This allows you to analyze documents and images without manually copying text.

## Features Added

✅ **PDF Upload** - Upload PDF documents and extract all text  
✅ **Image Upload (OCR)** - Upload images with text and extract using OCR  
✅ **Drag & Drop** - Easy file selection with visual feedback  
✅ **File Validation** - Automatic type and size validation  
✅ **Error Handling** - Clear error messages for troubleshooting  

## Supported File Types

- **PDFs**: `.pdf`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.tiff`

**File Size Limit**: 10MB maximum

## Installation Steps

### 1. Install Python Dependencies

First, install the required Python packages:

```bash
# Activate your virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

This installs:
- `pypdf==5.1.0` - For PDF text extraction
- `pillow==11.0.0` - For image processing
- `pytesseract==0.3.13` - For OCR (text extraction from images)
- `python-multipart==0.0.9` - For file upload handling in FastAPI

### 2. Install Tesseract OCR (Required for Images)

Tesseract OCR is needed to extract text from images. Install it on your system:

#### Windows:
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (recommended path: `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to your PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click Edit
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK

#### Mac:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 3. Verify Installation

Test that Tesseract is installed correctly:

```bash
tesseract --version
```

You should see version information if installed correctly.

### 4. Restart Backend

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

### 2. Upload a File

1. Navigate to http://localhost:3000
2. Click the **"Upload PDF or Image"** button
3. Select your PDF or image file
4. The text will be extracted automatically and appear in the text area
5. Click **"Generate Knowledge Graph"** to process

### 3. Or Paste Text

You can still paste text manually as before. The file upload is an additional option.

## API Endpoints

### File Extraction Endpoint

```
POST /api/py/file/extract
Content-Type: multipart/form-data

Request:
- file: (binary file upload)

Response:
{
  "text": "Extracted text content...",
  "filename": "document.pdf",
  "file_type": "pdf" | "image",
  "char_count": 1234
}
```

## Troubleshooting

### "Tesseract OCR is not installed"

**Problem**: You're trying to upload an image but Tesseract isn't installed.

**Solution**: Follow Step 2 above to install Tesseract OCR on your system.

### "Failed to extract text from PDF"

**Possible causes**:
- PDF is encrypted or password-protected
- PDF contains only images (scanned document)
- PDF is corrupted

**Solutions**:
- Remove password protection from PDF
- For scanned PDFs, save images and upload them separately
- Try a different PDF

### "No text could be extracted from image"

**Possible causes**:
- Image quality is too low
- Text is too small or blurry
- Image doesn't contain text

**Solutions**:
- Use higher resolution images
- Ensure text is clearly visible
- Try enhancing image contrast/brightness first

### "File too large"

**Problem**: File exceeds 10MB limit.

**Solution**: 
- Compress your PDF (many online tools available)
- Reduce image resolution
- Split large documents into smaller parts

## Architecture

### Backend Components

**`api/services/file_extraction.py`**
- `FileExtractionService` - Main service class
- `extract_text_from_pdf()` - PDF processing
- `extract_text_from_image()` - Image OCR processing
- `extract_text_from_file()` - Auto-detection and routing

**`api/index.py`**
- `POST /api/py/file/extract` - File upload endpoint
- Validation and error handling

### Frontend Components

**`app/page.tsx`**
- File upload UI with drag & drop
- File extraction state management
- Integration with text processing flow

## Technical Details

### PDF Extraction
Uses `pypdf` library to read PDF files and extract text from each page. Works with:
- Text-based PDFs
- PDFs with selectable text
- Multi-page documents

### Image OCR
Uses `pytesseract` (wrapper for Tesseract OCR) to perform optical character recognition on images. Works with:
- Screenshots
- Photos of documents
- Scanned images
- JPG, PNG, WebP, GIF, etc.

### Security Features
- File type validation (MIME type and extension)
- File size limit (10MB)
- Secure file handling (no files saved to disk)
- Error sanitization

## Next Steps

Once text is extracted from your file:
1. The text appears in the text area
2. You can edit it if needed
3. Click "Generate Knowledge Graph"
4. The system processes the text as usual

Enjoy analyzing PDFs and images! 📄🖼️

