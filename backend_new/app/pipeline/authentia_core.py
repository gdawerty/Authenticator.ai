"""
Authentia Core - Document Processing Pipeline
==============================================
Modular document processing with file validation, OCR, and markdown normalization.

Components:
- FileInspector: Validates file integrity and extracts metadata
- OCREngine: Tesseract-based OCR with image preprocessing
- MarkdownNormalizer: Converts raw OCR output to structured markdown
"""

import os
import re
import mimetypes
import tempfile
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

# Image processing
from PIL import Image, ImageFilter, ImageOps

# PDF handling
from pdf2image import convert_from_path
import fitz  # PyMuPDF for PDF metadata

# OCR
import pytesseract

# DOCX handling
from docx import Document as DocxDocument


class FileType(Enum):
    """Supported file types"""
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    DOCX = "docx"
    DOC = "doc"
    UNKNOWN = "unknown"


@dataclass
class FileMetadata:
    """Document metadata container"""
    filename: str
    file_type: FileType
    file_size: int
    mime_type: str
    extension_matches_content: bool

    # PDF/DOCX specific metadata
    author: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    page_count: Optional[int] = None

    # Integrity flags
    integrity_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "filename": self.filename,
            "file_type": self.file_type.value,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "extension_matches_content": self.extension_matches_content,
            "author": self.author,
            "creator": self.creator,
            "producer": self.producer,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "modification_date": self.modification_date.isoformat() if self.modification_date else None,
            "title": self.title,
            "subject": self.subject,
            "page_count": self.page_count,
            "integrity_warnings": self.integrity_warnings
        }


@dataclass
class OCRResult:
    """OCR extraction result"""
    text: str
    page_number: int
    confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "page_number": self.page_number,
            "confidence": self.confidence
        }


@dataclass
class ProcessedDocument:
    """Complete processed document"""
    metadata: FileMetadata
    ocr_results: List[OCRResult]
    markdown_content: str
    processing_time: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "ocr_results": [r.to_dict() for r in self.ocr_results],
            "markdown_content": self.markdown_content,
            "processing_time": self.processing_time
        }


class FileInspector:
    """
    Validates file integrity and extracts metadata.
    First line of defense against file type spoofing.
    """

    # Magic byte signatures for file type detection
    MAGIC_SIGNATURES = {
        b'%PDF': FileType.PDF,
        b'\x89PNG': FileType.PNG,
        b'\xff\xd8\xff': FileType.JPG,  # Also covers JPEG
        b'PK\x03\x04': FileType.DOCX,   # ZIP-based (DOCX, XLSX, etc.)
    }

    # Expected MIME types per file type
    EXPECTED_MIMES = {
        FileType.PDF: ['application/pdf'],
        FileType.PNG: ['image/png'],
        FileType.JPG: ['image/jpeg'],
        FileType.JPEG: ['image/jpeg'],
        FileType.DOCX: ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        FileType.DOC: ['application/msword'],
    }

    def __init__(self):
        mimetypes.init()

    def inspect(self, file_path: str) -> FileMetadata:
        """
        Inspect a file and extract metadata with integrity checks.

        Args:
            file_path: Path to the file to inspect

        Returns:
            FileMetadata with all extracted information
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Basic file info
        filename = path.name
        file_size = path.stat().st_size
        extension = path.suffix.lower().lstrip('.')

        # Detect actual file type from magic bytes
        actual_type = self._detect_file_type(file_path)

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        # Check if extension matches content
        declared_type = self._extension_to_type(extension)
        extension_matches = self._types_match(declared_type, actual_type)

        # Create metadata object
        metadata = FileMetadata(
            filename=filename,
            file_type=actual_type,
            file_size=file_size,
            mime_type=mime_type,
            extension_matches_content=extension_matches
        )

        # Add integrity warning if mismatch
        if not extension_matches:
            metadata.integrity_warnings.append(
                f"Extension mismatch: file has .{extension} but content is {actual_type.value}"
            )

        # Extract type-specific metadata
        if actual_type == FileType.PDF:
            self._extract_pdf_metadata(file_path, metadata)
        elif actual_type == FileType.DOCX:
            self._extract_docx_metadata(file_path, metadata)
        elif actual_type in [FileType.PNG, FileType.JPG, FileType.JPEG]:
            self._extract_image_metadata(file_path, metadata)

        return metadata

    def _detect_file_type(self, file_path: str) -> FileType:
        """Detect file type from magic bytes"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)

            for signature, file_type in self.MAGIC_SIGNATURES.items():
                if header.startswith(signature):
                    # Special handling for ZIP-based formats
                    if file_type == FileType.DOCX:
                        # Verify it's actually a DOCX by checking internal structure
                        if self._is_valid_docx(file_path):
                            return FileType.DOCX
                    else:
                        return file_type

            return FileType.UNKNOWN

        except Exception:
            return FileType.UNKNOWN

    def _is_valid_docx(self, file_path: str) -> bool:
        """Verify ZIP file is actually a DOCX"""
        try:
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as z:
                # DOCX files must contain these
                required = ['[Content_Types].xml', 'word/document.xml']
                names = z.namelist()
                return all(any(req in name for name in names) for req in required)
        except Exception:
            return False

    def _extension_to_type(self, extension: str) -> FileType:
        """Convert file extension to FileType"""
        ext_map = {
            'pdf': FileType.PDF,
            'png': FileType.PNG,
            'jpg': FileType.JPG,
            'jpeg': FileType.JPEG,
            'docx': FileType.DOCX,
            'doc': FileType.DOC,
        }
        return ext_map.get(extension.lower(), FileType.UNKNOWN)

    def _types_match(self, declared: FileType, actual: FileType) -> bool:
        """Check if declared and actual types are compatible"""
        # JPG and JPEG are the same
        if {declared, actual} == {FileType.JPG, FileType.JPEG}:
            return True
        return declared == actual

    def _extract_pdf_metadata(self, file_path: str, metadata: FileMetadata) -> None:
        """Extract metadata from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            pdf_metadata = doc.metadata

            metadata.page_count = len(doc)
            metadata.author = pdf_metadata.get('author')
            metadata.creator = pdf_metadata.get('creator')
            metadata.producer = pdf_metadata.get('producer')
            metadata.title = pdf_metadata.get('title')
            metadata.subject = pdf_metadata.get('subject')

            # Parse dates
            if pdf_metadata.get('creationDate'):
                metadata.creation_date = self._parse_pdf_date(pdf_metadata['creationDate'])
            if pdf_metadata.get('modDate'):
                metadata.modification_date = self._parse_pdf_date(pdf_metadata['modDate'])

            # Check for anomalies
            if metadata.producer and 'Fake' in metadata.producer:
                metadata.integrity_warnings.append("Suspicious producer string detected")

            doc.close()

        except Exception as e:
            metadata.integrity_warnings.append(f"PDF metadata extraction failed: {str(e)}")

    def _extract_docx_metadata(self, file_path: str, metadata: FileMetadata) -> None:
        """Extract metadata from DOCX"""
        try:
            doc = DocxDocument(file_path)
            core_props = doc.core_properties

            metadata.author = core_props.author
            metadata.title = core_props.title
            metadata.subject = core_props.subject
            metadata.creation_date = core_props.created
            metadata.modification_date = core_props.modified

            # Count pages (approximate from paragraphs)
            metadata.page_count = max(1, len(doc.paragraphs) // 30)

        except Exception as e:
            metadata.integrity_warnings.append(f"DOCX metadata extraction failed: {str(e)}")

    def _extract_image_metadata(self, file_path: str, metadata: FileMetadata) -> None:
        """Extract metadata from image files"""
        try:
            with Image.open(file_path) as img:
                metadata.page_count = 1

                # Check for EXIF data
                exif = img.getexif()
                if exif:
                    # Software used to create
                    if 305 in exif:  # Software tag
                        metadata.creator = exif[305]
                    # DateTimeOriginal
                    if 36867 in exif:
                        try:
                            metadata.creation_date = datetime.strptime(
                                exif[36867], '%Y:%m:%d %H:%M:%S'
                            )
                        except ValueError:
                            pass

        except Exception as e:
            metadata.integrity_warnings.append(f"Image metadata extraction failed: {str(e)}")

    def _parse_pdf_date(self, date_str: str) -> Optional[datetime]:
        """Parse PDF date format (D:YYYYMMDDHHmmSS)"""
        if not date_str:
            return None
        try:
            # Remove D: prefix if present
            if date_str.startswith('D:'):
                date_str = date_str[2:]
            # Parse the date (might have timezone)
            date_str = date_str[:14]  # Take just YYYYMMDDHHmmSS
            return datetime.strptime(date_str, '%Y%m%d%H%M%S')
        except (ValueError, IndexError):
            return None


class OCREngine:
    """
    Tesseract-based OCR with image preprocessing.
    Handles PDFs, images, and provides preprocessing for better accuracy.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None, dpi: int = 300):
        """
        Initialize OCR engine.

        Args:
            tesseract_cmd: Path to tesseract executable (auto-detect if None)
            dpi: DPI for PDF to image conversion
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.dpi = dpi

    def extract_text(self, file_path: str, file_type: FileType) -> List[OCRResult]:
        """
        Extract text from a document using OCR.

        Args:
            file_path: Path to the document
            file_type: Type of the file

        Returns:
            List of OCRResult objects, one per page
        """
        if file_type == FileType.PDF:
            return self._process_pdf(file_path)
        elif file_type in [FileType.PNG, FileType.JPG, FileType.JPEG]:
            return self._process_image(file_path)
        elif file_type == FileType.DOCX:
            return self._process_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _process_pdf(self, file_path: str) -> List[OCRResult]:
        """Convert PDF pages to images and OCR each"""
        results = []

        # Convert PDF to images
        images = convert_from_path(file_path, dpi=self.dpi)

        for page_num, image in enumerate(images, start=1):
            # Preprocess and OCR
            processed = self._preprocess_image(image)
            text = pytesseract.image_to_string(processed)

            # Get confidence data
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if c != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            results.append(OCRResult(
                text=text.strip(),
                page_number=page_num,
                confidence=round(avg_confidence, 2)
            ))

        return results

    def _process_image(self, file_path: str) -> List[OCRResult]:
        """OCR a single image file"""
        with Image.open(file_path) as img:
            processed = self._preprocess_image(img)
            text = pytesseract.image_to_string(processed)

            # Get confidence
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if c != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return [OCRResult(
                text=text.strip(),
                page_number=1,
                confidence=round(avg_confidence, 2)
            )]

    def _process_docx(self, file_path: str) -> List[OCRResult]:
        """Extract text from DOCX (no OCR needed, direct extraction)"""
        doc = DocxDocument(file_path)

        # Combine all paragraphs
        full_text = '\n'.join(para.text for para in doc.paragraphs if para.text.strip())

        return [OCRResult(
            text=full_text,
            page_number=1,
            confidence=100.0  # Direct extraction, no OCR uncertainty
        )]

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.

        Steps:
        1. Convert to grayscale
        2. Apply adaptive thresholding
        3. Remove noise
        4. Enhance contrast
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # Enhance contrast
        image = ImageOps.autocontrast(image, cutoff=2)

        # Apply slight sharpening
        image = image.filter(ImageFilter.SHARPEN)

        # Binarization (thresholding) for scanned documents
        # Use a threshold that works well for most documents
        threshold = 140
        image = image.point(lambda x: 255 if x > threshold else 0, mode='1')

        # Convert back to grayscale for Tesseract
        image = image.convert('L')

        return image


class MarkdownNormalizer:
    """
    Converts raw OCR text to structured Markdown.
    Uses heuristics to identify headers, lists, and structure.
    """

    def __init__(self):
        # Patterns for structure detection
        self.header_patterns = [
            # ALL CAPS short lines (likely headers)
            (r'^([A-Z][A-Z\s]{2,50})$', 2),
            # Lines ending with colon (likely section headers)
            (r'^([A-Za-z][A-Za-z\s]{2,40}:)\s*$', 3),
            # Numbered sections like "1. Introduction"
            (r'^(\d+\.\s+[A-Z][a-z]+.*)$', 2),
        ]

        self.list_patterns = [
            # Bullet points
            r'^[\•\-\*\◦]\s+(.+)$',
            # Numbered lists
            r'^(\d+[\.\)]\s+.+)$',
            # Letter lists
            r'^([a-z][\.\)]\s+.+)$',
        ]

    def normalize(self, ocr_results: List[OCRResult], metadata: FileMetadata) -> str:
        """
        Convert OCR results to structured Markdown.

        Args:
            ocr_results: List of OCR results from each page
            metadata: Document metadata for header

        Returns:
            Formatted Markdown string
        """
        lines = []

        # Document header
        lines.append(f"# {metadata.filename}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Document Information")
        lines.append("")
        lines.append(f"- **File Type:** {metadata.file_type.value.upper()}")
        lines.append(f"- **Pages:** {metadata.page_count or 'Unknown'}")
        if metadata.author:
            lines.append(f"- **Author:** {metadata.author}")
        if metadata.creation_date:
            lines.append(f"- **Created:** {metadata.creation_date.strftime('%Y-%m-%d')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Process each page
        for result in ocr_results:
            if len(ocr_results) > 1:
                lines.append(f"## Page {result.page_number}")
                lines.append("")

            # Process the text content
            page_lines = self._process_text(result.text)
            lines.extend(page_lines)
            lines.append("")

        return '\n'.join(lines)

    def _process_text(self, text: str) -> List[str]:
        """Process raw text and apply markdown formatting"""
        output = []
        raw_lines = text.split('\n')

        in_list = False

        for line in raw_lines:
            line = line.strip()

            if not line:
                if in_list:
                    in_list = False
                output.append("")
                continue

            # Check for headers
            is_header, header_level, header_text = self._detect_header(line)
            if is_header:
                if in_list:
                    output.append("")
                    in_list = False
                output.append(f"{'#' * header_level} {header_text}")
                continue

            # Check for list items
            is_list, list_text = self._detect_list_item(line)
            if is_list:
                in_list = True
                output.append(f"- {list_text}")
                continue

            # Regular paragraph
            if in_list:
                output.append("")
                in_list = False

            # Clean up the line
            cleaned = self._clean_line(line)
            if cleaned:
                output.append(cleaned)

        return output

    def _detect_header(self, line: str) -> Tuple[bool, int, str]:
        """Detect if a line is a header"""
        for pattern, level in self.header_patterns:
            match = re.match(pattern, line)
            if match:
                # Don't mark very long lines as headers
                if len(line) > 60:
                    continue
                return True, level, match.group(1).strip().title()

        # ALL CAPS detection (separate logic)
        if line.isupper() and 3 <= len(line) <= 50 and ' ' in line:
            return True, 2, line.title()

        return False, 0, ""

    def _detect_list_item(self, line: str) -> Tuple[bool, str]:
        """Detect if a line is a list item"""
        for pattern in self.list_patterns:
            match = re.match(pattern, line)
            if match:
                # Clean the text
                text = match.group(1) if match.lastindex else line
                # Remove leading bullet/number
                text = re.sub(r'^[\•\-\*\◦\d+\.a-z\)]+\s*', '', text)
                return True, text.strip()

        return False, ""

    def _clean_line(self, line: str) -> str:
        """Clean up a line of text"""
        # Remove multiple spaces
        line = re.sub(r'\s+', ' ', line)

        # Remove common OCR artifacts
        line = re.sub(r'[|]', '', line)

        # Fix common OCR mistakes
        replacements = [
            (r'\bI\b(?=[a-z])', 'l'),  # I before lowercase often should be l
            (r'(?<=[a-z])I\b', 'l'),    # lowercase followed by I
            (r'\b0(?=[a-z])', 'O'),     # 0 before letter should be O
        ]

        for pattern, replacement in replacements:
            line = re.sub(pattern, replacement, line)

        return line.strip()


class AuthentiaAgent:
    """
    Main orchestrator for the document processing pipeline.
    Coordinates FileInspector, OCREngine, and MarkdownNormalizer.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the Authentia agent.

        Args:
            output_dir: Directory for output files (temp dir if None)
        """
        self.inspector = FileInspector()
        self.ocr_engine = OCREngine()
        self.normalizer = MarkdownNormalizer()
        self.output_dir = output_dir or tempfile.gettempdir()

    def process(self, file_path: str, save_markdown: bool = True) -> ProcessedDocument:
        """
        Process a document through the full pipeline.

        Args:
            file_path: Path to the document
            save_markdown: Whether to save markdown to file

        Returns:
            ProcessedDocument with all results
        """
        import time
        start_time = time.time()

        # Step 1: Inspect file and extract metadata
        metadata = self.inspector.inspect(file_path)

        if metadata.file_type == FileType.UNKNOWN:
            raise ValueError(f"Unsupported or unrecognized file type: {file_path}")

        # Step 2: OCR extraction
        ocr_results = self.ocr_engine.extract_text(file_path, metadata.file_type)

        # Step 3: Normalize to Markdown
        markdown_content = self.normalizer.normalize(ocr_results, metadata)

        processing_time = time.time() - start_time

        # Optionally save markdown
        if save_markdown:
            md_filename = Path(file_path).stem + '_extracted.md'
            md_path = Path(self.output_dir) / md_filename
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

        return ProcessedDocument(
            metadata=metadata,
            ocr_results=ocr_results,
            markdown_content=markdown_content,
            processing_time=round(processing_time, 2)
        )

    def inspect_only(self, file_path: str) -> FileMetadata:
        """Run only the file inspection step"""
        return self.inspector.inspect(file_path)

    def ocr_only(self, file_path: str) -> List[OCRResult]:
        """Run only OCR extraction"""
        metadata = self.inspector.inspect(file_path)
        return self.ocr_engine.extract_text(file_path, metadata.file_type)


# Convenience function for quick processing
def process_document(file_path: str, output_dir: Optional[str] = None) -> ProcessedDocument:
    """
    Quick function to process a document.

    Args:
        file_path: Path to the document
        output_dir: Optional output directory for markdown

    Returns:
        ProcessedDocument with all results
    """
    agent = AuthentiaAgent(output_dir=output_dir)
    return agent.process(file_path)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python authentia_core.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    print(f"\n{'='*60}")
    print("AUTHENTIA CORE - Document Processing Pipeline")
    print(f"{'='*60}\n")

    try:
        result = process_document(file_path)

        print("📄 METADATA")
        print("-" * 40)
        meta = result.metadata
        print(f"  Filename: {meta.filename}")
        print(f"  Type: {meta.file_type.value}")
        print(f"  Size: {meta.file_size:,} bytes")
        print(f"  Extension Valid: {'✓' if meta.extension_matches_content else '✗'}")
        if meta.author:
            print(f"  Author: {meta.author}")
        if meta.page_count:
            print(f"  Pages: {meta.page_count}")
        if meta.integrity_warnings:
            print(f"\n  ⚠️  Warnings:")
            for w in meta.integrity_warnings:
                print(f"      - {w}")

        print(f"\n📝 OCR RESULTS")
        print("-" * 40)
        for ocr in result.ocr_results:
            preview = ocr.text[:200].replace('\n', ' ')
            print(f"  Page {ocr.page_number} (conf: {ocr.confidence}%): {preview}...")

        print(f"\n⏱️  Processing Time: {result.processing_time}s")
        print(f"\n{'='*60}\n")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
