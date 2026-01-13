from pathlib import Path
from typing import List
from app.models.document import DocumentSpan
from uuid import uuid4


class Parser:
    """
    Parsing Layer - Extract structured spans from normalized documents

    Using python-docx for DOCX parsing
    Assigns stable span IDs to each element
    """

    def parse(self, docx_path: Path) -> List[DocumentSpan]:
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
