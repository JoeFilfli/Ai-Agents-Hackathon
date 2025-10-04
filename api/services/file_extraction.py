"""
File Extraction Service

This service handles extracting text from various file types:
- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png, .webp, .gif) using OCR

The extracted text can then be processed by the TextProcessingService.
"""

import io
from pathlib import Path
from typing import Optional
from pypdf import PdfReader
from PIL import Image
import pytesseract


class FileExtractionService:
    """
    Service for extracting text from uploaded files.
    
    Supports:
    - PDF files (using pypdf)
    - Images (using pytesseract OCR)
    """
    
    # Supported file extensions
    SUPPORTED_PDF_EXTENSIONS = {'.pdf'}
    SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}
    
    def __init__(self):
        """Initialize the file extraction service."""
        pass
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_content: Raw bytes of the PDF file
            
        Returns:
            Extracted text from all pages
            
        Raises:
            ValueError: If PDF cannot be read or is empty
        """
        try:
            # Create PDF reader from bytes
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            # Check if PDF has pages
            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF file is empty (no pages found)")
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
            
            # Combine all pages
            full_text = "\n\n".join(text_parts)
            
            # Validate extracted text
            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF. The PDF may contain only images or be encrypted.")
            
            return full_text
            
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_image(self, file_content: bytes, filename: str = "image") -> str:
        """
        Extract text from an image using OCR (Optical Character Recognition).
        
        Args:
            file_content: Raw bytes of the image file
            filename: Original filename (for error messages)
            
        Returns:
            Extracted text from the image
            
        Raises:
            ValueError: If image cannot be read or OCR fails
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if needed (some formats like PNG with alpha channel)
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Perform OCR
            # pytesseract must be installed on the system
            # For Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
            # For Linux: sudo apt-get install tesseract-ocr
            # For Mac: brew install tesseract
            text = pytesseract.image_to_string(image, lang='eng')
            
            # Validate extracted text
            if not text.strip():
                raise ValueError(
                    "No text could be extracted from image. "
                    "The image may not contain readable text or the quality may be too low."
                )
            
            return text.strip()
            
        except pytesseract.TesseractNotFoundError:
            raise ValueError(
                "Tesseract OCR is not installed on the system. "
                "Please install Tesseract OCR to process images. "
                "Visit: https://github.com/tesseract-ocr/tesseract"
            )
        except Exception as e:
            raise ValueError(f"Failed to extract text from image '{filename}': {str(e)}")
    
    def extract_text_from_file(
        self, 
        file_content: bytes, 
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Extract text from a file (auto-detects type).
        
        Args:
            file_content: Raw bytes of the file
            filename: Original filename (used to determine file type)
            content_type: Optional MIME type (e.g., 'application/pdf')
            
        Returns:
            Extracted text from the file
            
        Raises:
            ValueError: If file type is unsupported or extraction fails
        """
        # Get file extension
        file_ext = Path(filename).suffix.lower()
        
        # Route to appropriate extractor
        if file_ext in self.SUPPORTED_PDF_EXTENSIONS or content_type == 'application/pdf':
            return self.extract_text_from_pdf(file_content)
        
        elif file_ext in self.SUPPORTED_IMAGE_EXTENSIONS or (
            content_type and content_type.startswith('image/')
        ):
            return self.extract_text_from_image(file_content, filename)
        
        else:
            # Unsupported file type
            supported_types = ', '.join(
                list(self.SUPPORTED_PDF_EXTENSIONS) + 
                list(self.SUPPORTED_IMAGE_EXTENSIONS)
            )
            raise ValueError(
                f"Unsupported file type '{file_ext}'. "
                f"Supported types: {supported_types}"
            )
    
    def is_supported_file(self, filename: str) -> bool:
        """
        Check if a file type is supported.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file type is supported, False otherwise
        """
        file_ext = Path(filename).suffix.lower()
        return (
            file_ext in self.SUPPORTED_PDF_EXTENSIONS or 
            file_ext in self.SUPPORTED_IMAGE_EXTENSIONS
        )

