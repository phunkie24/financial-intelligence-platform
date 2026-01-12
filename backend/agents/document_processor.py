"""
Document Processor Agent - OCR and document extraction specialist.

This agent handles all document processing tasks including:
- Text extraction from PDFs and images
- Table and chart detection
- OCR with PaddleOCR
- Document preprocessing and cleaning

CAMEL-AI Integration:
- Extends CAMEL's ChatAgent for intelligent document analysis
- Uses tools for PaddleOCR, PDF parsing, table extraction
- Communicates with Knowledge Manager for indexing
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.types import RoleType, ModelType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    RoleType = type('RoleType', (), {'ASSISTANT': 'assistant'})
    ModelType = type('ModelType', (), {'GPT_4': 'gpt-4'})

from .base_agent import FinancialAgent


logger = logging.getLogger(__name__)


class DocumentProcessorAgent(FinancialAgent):
    """
    Document Processor Agent - Handles OCR and document extraction.

    Capabilities:
    - PDF text extraction
    - Image OCR with PaddleOCR
    - Table detection and extraction
    - Text cleaning and normalization
    - Multi-page document handling
    """

    SYSTEM_MESSAGE = """
You are a Document Processing specialist with expertise in:
- Optical Character Recognition (OCR) using PaddleOCR
- PDF parsing and text extraction
- Table and chart detection
- Financial document layout analysis
- Text preprocessing and cleaning

Your role in the multi-agent system:
1. Extract text from uploaded documents (PDF, images)
2. Detect and parse tables with financial data
3. Clean and normalize extracted text
4. Provide structured output for downstream agents
5. Report extraction confidence and quality metrics

Always provide:
- Extracted text with page numbers
- Detected tables in structured format
- Confidence scores for OCR results
- Any extraction warnings or issues
"""

    def __init__(self):
        """Initialize Document Processor Agent."""
        super().__init__(
            role_name="Document Processor",
            role_type=RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )

        # Initialize PaddleOCR lazily
        self.ocr_engine = None
        self.pdf_parser = None

        logger.info("📄 Document Processor Agent initialized")

    def _init_ocr_engine(self):
        """Initialize PaddleOCR engine (lazy loading)."""
        if self.ocr_engine is not None:
            return

        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                show_log=False
            )
            logger.info("✅ PaddleOCR engine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PaddleOCR: {e}")
            self.ocr_engine = None

    def _init_pdf_parser(self):
        """Initialize PDF parsing tools (lazy loading)."""
        if self.pdf_parser is not None:
            return

        try:
            import pdfplumber
            self.pdf_parser = pdfplumber
            logger.info("✅ PDF parser initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PDF parser: {e}")
            self.pdf_parser = None

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Process document and extract content.

        Args:
            input_data: File path to document or dictionary with file_path

        Returns:
            Extraction results with text, tables, and metadata
        """
        # Extract file path
        if isinstance(input_data, dict):
            file_path = input_data.get('file_path', input_data.get('input', ''))
        else:
            file_path = str(input_data)

        if not file_path or not os.path.exists(file_path):
            return {
                'status': 'FAILED',
                'error': f'File not found: {file_path}',
                'extracted_text': '',
                'tables': [],
                'metadata': {}
            }

        logger.info(f"📄 Processing document: {file_path}")

        # Determine file type
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            result = await self._process_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            result = await self._process_image(file_path)
        else:
            result = {
                'status': 'FAILED',
                'error': f'Unsupported file type: {file_ext}',
                'extracted_text': '',
                'tables': [],
                'metadata': {}
            }

        return result

    async def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text and tables from PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Extraction results
        """
        self._init_pdf_parser()

        if self.pdf_parser is None:
            return {
                'status': 'FAILED',
                'error': 'PDF parser not available',
                'extracted_text': '',
                'tables': [],
                'metadata': {}
            }

        try:
            pages_text = []
            tables = []
            page_count = 0

            with self.pdf_parser.open(file_path) as pdf:
                page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append({
                            'page': page_num,
                            'text': page_text.strip()
                        })

                    # Extract tables
                    page_tables = page.extract_tables()
                    for table_idx, table in enumerate(page_tables):
                        if table:
                            tables.append({
                                'page': page_num,
                                'table_index': table_idx,
                                'data': table,
                                'rows': len(table),
                                'columns': len(table[0]) if table else 0
                            })

            # Combine all text
            full_text = "\n\n".join([
                f"[Page {p['page']}]\n{p['text']}"
                for p in pages_text
            ])

            # Calculate confidence (basic heuristic)
            confidence = min(100, len(full_text) / 100 * 10)  # Simple estimate

            logger.info(f"✅ PDF processed: {page_count} pages, {len(tables)} tables, {len(full_text)} chars")

            return {
                'status': 'SUCCESS',
                'extracted_text': full_text,
                'pages': pages_text,
                'tables': tables,
                'metadata': {
                    'file_path': file_path,
                    'page_count': page_count,
                    'table_count': len(tables),
                    'character_count': len(full_text),
                    'confidence': confidence,
                    'extraction_method': 'pdfplumber',
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"❌ PDF processing failed: {e}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'extracted_text': '',
                'tables': [],
                'metadata': {'file_path': file_path}
            }

    async def _process_image(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from image using PaddleOCR.

        Args:
            file_path: Path to image file

        Returns:
            OCR results
        """
        self._init_ocr_engine()

        if self.ocr_engine is None:
            return {
                'status': 'FAILED',
                'error': 'OCR engine not available',
                'extracted_text': '',
                'tables': [],
                'metadata': {}
            }

        try:
            # Run OCR
            result = self.ocr_engine.ocr(file_path, cls=True)

            # Extract text and confidence
            extracted_lines = []
            total_confidence = 0
            line_count = 0

            for page_result in result:
                if page_result is None:
                    continue

                for line in page_result:
                    if len(line) >= 2:
                        text = line[1][0]
                        confidence = line[1][1]

                        extracted_lines.append(text)
                        total_confidence += confidence
                        line_count += 1

            full_text = "\n".join(extracted_lines)
            avg_confidence = (total_confidence / line_count * 100) if line_count > 0 else 0

            logger.info(f"✅ OCR processed: {line_count} lines, {len(full_text)} chars, {avg_confidence:.1f}% confidence")

            return {
                'status': 'SUCCESS',
                'extracted_text': full_text,
                'pages': [{'page': 1, 'text': full_text}],
                'tables': [],  # Table detection would require additional processing
                'metadata': {
                    'file_path': file_path,
                    'line_count': line_count,
                    'character_count': len(full_text),
                    'confidence': avg_confidence,
                    'extraction_method': 'paddleocr',
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"❌ OCR processing failed: {e}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'extracted_text': '',
                'tables': [],
                'metadata': {'file_path': file_path}
            }

    def extract_tables_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract table-like structures from plain text.

        Args:
            text: Extracted text

        Returns:
            List of detected tables
        """
        # Simple heuristic: look for lines with multiple tab/space-separated values
        tables = []
        lines = text.split('\n')

        current_table = []
        for line in lines:
            # Check if line looks like table row (multiple cells)
            cells = [c.strip() for c in line.split('\t') if c.strip()]
            if len(cells) >= 2:
                current_table.append(cells)
            else:
                if len(current_table) >= 2:
                    # End of table
                    tables.append({
                        'data': current_table,
                        'rows': len(current_table),
                        'columns': len(current_table[0])
                    })
                current_table = []

        # Add last table if exists
        if len(current_table) >= 2:
            tables.append({
                'data': current_table,
                'rows': len(current_table),
                'columns': len(current_table[0])
            })

        return tables

    async def validate_extraction(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extraction quality and generate report.

        Args:
            extraction_result: Result from process()

        Returns:
            Validation report
        """
        text = extraction_result.get('extracted_text', '')
        metadata = extraction_result.get('metadata', {})

        # Quality checks
        checks = {
            'has_content': len(text) > 0,
            'sufficient_length': len(text) > 100,
            'high_confidence': metadata.get('confidence', 0) > 70,
            'tables_detected': len(extraction_result.get('tables', [])) > 0
        }

        quality_score = sum(checks.values()) / len(checks) * 100

        validation = {
            'quality_score': quality_score,
            'checks': checks,
            'warnings': [],
            'recommendations': []
        }

        # Add warnings
        if not checks['has_content']:
            validation['warnings'].append('No content extracted from document')
        if not checks['high_confidence']:
            validation['warnings'].append(f"Low OCR confidence: {metadata.get('confidence', 0):.1f}%")
        if not checks['tables_detected']:
            validation['recommendations'].append('Consider manual table verification')

        return validation
