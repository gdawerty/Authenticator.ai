from pathlib import Path
from typing import Tuple
import shutil
from PIL import Image


class Normalizer:
    """
    Normalization Layer - Deterministic only, no intelligence

    Rules:
    - Everything → DOCX
    - Images → PNG
    - PDFs → DOCX (layout preserved)
    """

    def normalize(self, file_path: Path) -> Tuple[Path, str]:
        """
        Normalize a file to canonical format

        Returns:
            Tuple of (canonical_path, document_type)
        """
        extension = file_path.suffix.lower()

        if extension == '.pdf':
            return self._normalize_pdf(file_path), 'pdf'
        elif extension in ['.doc', '.docx']:
            return self._normalize_docx(file_path), 'docx'
        elif extension in ['.png', '.jpg', '.jpeg']:
            return self._normalize_image(file_path), 'image'
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def _normalize_pdf(self, pdf_path: Path) -> Path:
        """Convert PDF to DOCX (layout preserved)"""
        try:
            from pdf2docx import Converter

            docx_path = pdf_path.with_suffix('.docx')
            cv = Converter(str(pdf_path))
            cv.convert(str(docx_path))
            cv.close()

            return docx_path
        except ImportError:
            # Fallback: if pdf2docx not available, keep as PDF for now
            # In production, this should fail or use another library
            return pdf_path

    def _normalize_docx(self, docx_path: Path) -> Path:
        """DOCX is already canonical, just return it"""
        return docx_path

    def _normalize_image(self, image_path: Path) -> Path:
        """Convert image to PNG"""
        png_path = image_path.with_suffix('.png')

        if image_path.suffix.lower() == '.png':
            return image_path

        img = Image.open(image_path)
        img.save(png_path, 'PNG')

        return png_path


normalizer = Normalizer()
