from pathlib import Path
from typing import List
from app.models.document import DocumentSpan
from uuid import uuid4


class Parser:
    """
    Parsing Layer - Extract structured spans from normalized documents

    Uses:
    - python-docx for DOCX parsing (digital documents)
    - Tesseract OCR for scanned/image-based documents (via authentia_core)

    Assigns stable span IDs to each element
    """

    def parse(self, file_path: Path) -> List[DocumentSpan]:
        """
        Parse file into DocumentSpans

        Handles both DOCX and PDF files.
        For PDFs, tries DOCX extraction first, falls back to OCR for scanned docs.

        Returns:
            List of DocumentSpan objects
        """
        extension = file_path.suffix.lower()

        if extension == '.docx':
            return self._parse_docx(file_path)
        elif extension == '.pdf':
            # For PDFs, we need to check if it's scanned or digital
            # First try the converted DOCX if it exists
            docx_path = file_path.with_suffix('.docx')
            if docx_path.exists():
                spans = self._parse_docx(docx_path)
                # If we got meaningful content, return it
                if spans and sum(len(s.text) for s in spans) > 50:
                    return spans

            # Fall back to OCR for scanned documents
            return self._parse_with_ocr(file_path)
        else:
            # Try OCR for images
            if extension in ['.png', '.jpg', '.jpeg']:
                return self._parse_with_ocr(file_path)
            return []

    def _parse_docx(self, docx_path: Path) -> List[DocumentSpan]:
        """
        Parse DOCX file into DocumentSpans

        Returns:
            List of DocumentSpan objects
        """
        try:
            from docx import Document

            doc = Document(str(docx_path))
            spans = []

            # Extract paragraphs
            for para in doc.paragraphs:
                if not para.text.strip():
                    continue

                span_type = self._determine_span_type(para)
                spans.append(DocumentSpan(
                    id=uuid4(),
                    span_type=span_type,
                    text=para.text.strip(),
                    page=None,  # python-docx doesn't provide page numbers easily
                    bbox=None
                ))

            # Extract tables
            for table_idx, table in enumerate(doc.tables):
                table_text = self._extract_table_text(table)
                if table_text.strip():
                    spans.append(DocumentSpan(
                        id=uuid4(),
                        span_type="table",
                        text=table_text,
                        page=None,
                        bbox=None
                    ))

            return spans

        except ImportError:
            raise ImportError("python-docx is required. Install with: pip install python-docx")

    def _parse_with_ocr(self, file_path: Path) -> List[DocumentSpan]:
        """
        Parse file using OCR (for scanned documents and images)

        Uses the authentia_core OCR engine.

        Returns:
            List of DocumentSpan objects
        """
        try:
            from app.pipeline.authentia_core import AuthentiaAgent

            agent = AuthentiaAgent()

            # Get metadata and OCR results
            metadata = agent.inspect_only(str(file_path))
            ocr_results = agent.ocr_engine.extract_text(str(file_path), metadata.file_type)

            spans = []

            for ocr_result in ocr_results:
                # Split OCR text into paragraphs
                paragraphs = [p.strip() for p in ocr_result.text.split('\n\n') if p.strip()]

                for para_text in paragraphs:
                    # Skip very short fragments
                    if len(para_text) < 10:
                        continue

                    # Detect span type based on text characteristics
                    span_type = self._detect_span_type_from_text(para_text)

                    spans.append(DocumentSpan(
                        id=uuid4(),
                        span_type=span_type,
                        text=para_text,
                        page=ocr_result.page_number,
                        bbox=None
                    ))

            return spans

        except Exception as e:
            print(f"OCR parsing error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _detect_span_type_from_text(self, text: str) -> str:
        """Detect span type from text characteristics"""
        # Check for title/heading patterns
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else text

        # Short, all caps = likely heading
        if first_line.isupper() and len(first_line) < 60:
            return "heading"

        # Very short with no punctuation = likely heading
        if len(first_line) < 40 and not first_line.endswith(('.', ',', ';', ':')):
            return "heading"

        # Contains table-like patterns (multiple | or tabs)
        if text.count('|') > 3 or text.count('\t') > 3:
            return "table"

        return "paragraph"

    def _determine_span_type(self, paragraph) -> str:
        """Determine if paragraph is title, heading, or regular paragraph"""
        if paragraph.style.name.startswith('Heading'):
            return "heading"
        elif paragraph.style.name == 'Title':
            return "title"
        else:
            return "paragraph"

    def _extract_table_text(self, table) -> str:
        """Extract text from table"""
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append(" | ".join(cells))
        return "\n".join(rows)


parser = Parser()
