# Databricks notebook source
"""
PaddleOCR Wrapper for Financial Document Extraction
Handles PDFs, images, tables, and charts
"""

from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class PaddleOCRWrapper:
    def __init__(self, use_gpu=False, lang='en'):
        """Initialize PaddleOCR"""
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                use_gpu=use_gpu,
                show_log=False
            )
            logger.info("✅ PaddleOCR initialized")
        except Exception as e:
            logger.error(f"❌ PaddleOCR initialization failed: {e}")
            raise
    
    def extract_from_file(self, file_path: str) -> Dict:
        """
        Extract text from PDF or image file
        Returns: {text, tables, confidence, layout}
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self._extract_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            raise
    
    def _extract_from_pdf(self, pdf_path: str) -> Dict:
        """Extract from PDF (converts pages to images)"""
        doc = fitz.open(pdf_path)
        all_text = []
        all_tables = []
        confidences = []
        
        logger.info(f"📄 Processing PDF: {doc.page_count} pages")
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img)
            
            # OCR on page
            result = self.ocr.ocr(img_np, cls=True)
            
            if result and result[0]:
                # Extract text
                page_text = []
                page_confidence = []
                
                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    page_text.append(text)
                    page_confidence.append(confidence)
                
                all_text.extend(page_text)
                confidences.extend(page_confidence)
                
                # Detect tables
                tables = self._detect_tables(img_np, result[0])
                all_tables.extend(tables)
            
            logger.info(f"  Page {page_num + 1}/{doc.page_count} processed")
        
        doc.close()
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            'text': '\n'.join(all_text),
            'tables': all_tables,
            'confidence': float(avg_confidence),
            'pages': doc.page_count,
            'layout': 'multi_page'
        }
    
    def _extract_from_image(self, img_path: str) -> Dict:
        """Extract from single image"""
        img = cv2.imread(img_path)
        
        if img is None:
            raise ValueError(f"Failed to load image: {img_path}")
        
        result = self.ocr.ocr(img, cls=True)
        
        if not result or not result[0]:
            return {
                'text': '',
                'tables': [],
                'confidence': 0.0,
                'pages': 1,
                'layout': 'single_image'
            }
        
        # Extract text and confidence
        text_lines = []
        confidences = []
        
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            text_lines.append(text)
            confidences.append(confidence)
        
        # Detect tables
        tables = self._detect_tables(img, result[0])
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            'text': '\n'.join(text_lines),
            'tables': tables,
            'confidence': float(avg_confidence),
            'pages': 1,
            'layout': 'single_image'
        }
    
    def _detect_tables(self, img: np.ndarray, ocr_result: List) -> List[Dict]:
        """
        Detect tables in image using OCR box positions
        Simple heuristic: aligned boxes = table
        """
        tables = []
        
        if not ocr_result:
            return tables
        
        # Group boxes by vertical position (rows)
        rows = {}
        for line in ocr_result:
            box = line[0]
            y_center = (box[0][1] + box[2][1]) / 2
            
            # Find nearest row
            found_row = False
            for row_y in rows.keys():
                if abs(y_center - row_y) < 20:  # Same row if within 20px
                    rows[row_y].append(line)
                    found_row = True
                    break
            
            if not found_row:
                rows[y_center] = [line]
        
        # Check if rows form a table (multiple rows with same column count)
        sorted_rows = sorted(rows.items(), key=lambda x: x[0])
        
        if len(sorted_rows) >= 3:  # At least 3 rows
            # Check column alignment
            col_counts = [len(row[1]) for row in sorted_rows]
            
            if len(set(col_counts)) <= 2:  # Consistent column count
                # Extract table data
                table_data = []
                for _, row_boxes in sorted_rows:
                    row_data = [box[1][0] for box in sorted(row_boxes, key=lambda x: x[0][0][0])]
                    table_data.append(row_data)
                
                tables.append({
                    'data': table_data,
                    'rows': len(table_data),
                    'cols': len(table_data[0]) if table_data else 0
                })
        
        return tables
    
    def extract_tables_advanced(self, file_path: str) -> List[Dict]:
        """
        Advanced table extraction using camelot (for PDFs)
        """
        try:
            import camelot
            
            tables = camelot.read_pdf(file_path, pages='all', flavor='lattice')
            
            extracted_tables = []
            for table in tables:
                extracted_tables.append({
                    'data': table.df.values.tolist(),
                    'rows': len(table.df),
                    'cols': len(table.df.columns),
                    'accuracy': table.accuracy
                })
            
            return extracted_tables
            
        except Exception as e:
            logger.warning(f"Advanced table extraction failed: {e}")
            return []
    
    def visualize_ocr(self, img_path: str, output_path: str = None):
        """Visualize OCR results with bounding boxes"""
        img = cv2.imread(img_path)
        result = self.ocr.ocr(img, cls=True)
        
        if not result or not result[0]:
            return None
        
        # Draw boxes
        boxes = [line[0] for line in result[0]]
        texts = [line[1][0] for line in result[0]]
        scores = [line[1][1] for line in result[0]]
        
        # Convert to PIL for drawing
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Draw
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img_pil)
        
        for box, text, score in zip(boxes, texts, scores):
            box = [(int(p[0]), int(p[1])) for p in box]
            draw.polygon(box, outline='red', width=2)
            draw.text(box[0], f"{text[:20]} ({score:.2f})", fill='blue')
        
        if output_path:
            img_pil.save(output_path)
        
        return img_pil