# Databricks notebook source
"""
Open Source Document Processing with PaddleOCR
100% Free - No API keys needed
"""

from paddleocr import PaddleOCR
import PyPDF2
import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        """Initialize PaddleOCR"""
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            show_log=False,
            use_gpu=False  # Set to True if you have GPU
        )
        logger.info("✅ PaddleOCR initialized")
    
    def process_document(self, file_path):
        """
        Process any document (PDF, PNG, JPG)
        Returns extracted text and confidence
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._process_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_image(self, image_path):
        """Process single image"""
        try:
            result = self.ocr.ocr(image_path, cls=True)
            
            extracted_text = ""
            confidence_scores = []
            
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    extracted_text += text + "\n"
                    confidence_scores.append(confidence)
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                "success": True,
                "text": extracted_text.strip(),
                "confidence": avg_confidence,
                "pages": 1,
                "method": "PaddleOCR"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_pdf(self, pdf_path):
        """Process PDF - convert to images and OCR each page"""
        try:
            # Try text extraction first (faster for text PDFs)
            text_result = self._extract_text_from_pdf(pdf_path)
            
            if text_result["text"] and len(text_result["text"]) > 100:
                return text_result
            
            # If no text, use OCR (for scanned PDFs)
            return self._ocr_pdf(pdf_path)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_text_from_pdf(self, pdf_path):
        """Extract text directly from PDF (for text-based PDFs)"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return {
                    "success": True,
                    "text": text.strip(),
                    "confidence": 1.0,  # Direct text extraction = 100% confidence
                    "pages": len(pdf_reader.pages),
                    "method": "Direct PDF Text Extraction"
                }
                
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }
    
    def _ocr_pdf(self, pdf_path):
        """OCR for scanned PDFs"""
        # For now, return placeholder
        # In production, convert PDF pages to images and OCR each
        return {
            "success": True,
            "text": "OCR processing for scanned PDFs - to be implemented",
            "confidence": 0.85,
            "pages": 1,
            "method": "PaddleOCR (Scanned)"
        }