from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import docx
import subprocess
import tempfile
from typing import Dict, Any
from uuid import UUID

from app.db.session import get_db
from app.models.db_models import DocumentModel

router = APIRouter()


def docx_to_html(docx_path: Path) -> str:
    """
    Convert DOCX to semantic HTML preserving formatting
    """
    try:
        doc = docx.Document(str(docx_path))
        html_parts = []

        html_parts.append('<div class="resume-document">')

        for para in doc.paragraphs:
            # Skip empty paragraphs
            if not para.text.strip():
                html_parts.append('<p class="empty-para">&nbsp;</p>')
                continue

            # Determine paragraph style and alignment
            style = para.style.name.lower() if para.style else ''
            alignment = ''
            if para.alignment:
                if str(para.alignment) == 'WD_ALIGN_PARAGRAPH.CENTER (1)':
                    alignment = ' style="text-align: center;"'
                elif str(para.alignment) == 'WD_ALIGN_PARAGRAPH.RIGHT (2)':
                    alignment = ' style="text-align: right;"'

            # Handle headings and titles
            if 'heading 1' in style or 'title' in style:
                html_parts.append(f'<h1{alignment}>{para.text}</h1>')
            elif 'heading 2' in style:
                html_parts.append(f'<h2{alignment}>{para.text}</h2>')
            elif 'heading 3' in style:
                html_parts.append(f'<h3{alignment}>{para.text}</h3>')
            else:
                # Regular paragraph - preserve formatting in runs
                para_html = f'<p{alignment}>'

                for run in para.runs:
                    text = run.text
                    if not text:
                        continue

                    # Build nested formatting
                    if run.bold and run.italic and run.underline:
                        text = f'<strong><em><u>{text}</u></em></strong>'
                    elif run.bold and run.italic:
                        text = f'<strong><em>{text}</em></strong>'
                    elif run.bold and run.underline:
                        text = f'<strong><u>{text}</u></strong>'
                    elif run.italic and run.underline:
                        text = f'<em><u>{text}</u></em>'
                    elif run.bold:
                        text = f'<strong>{text}</strong>'
                    elif run.italic:
                        text = f'<em>{text}</em>'
                    elif run.underline:
                        text = f'<u>{text}</u>'

                    para_html += text

                para_html += '</p>'
                html_parts.append(para_html)

        # Handle tables
        for table in doc.tables:
            html_parts.append('<table class="doc-table">')
            for i, row in enumerate(table.rows):
                html_parts.append('<tr>')
                for cell in row.cells:
                    # Check if cell has bold text (likely a header)
                    is_header = any(run.bold for para in cell.paragraphs for run in para.runs)
                    tag = 'th' if is_header or i == 0 else 'td'
                    html_parts.append(f'<{tag}>{cell.text}</{tag}>')
                html_parts.append('</tr>')
            html_parts.append('</table>')

        html_parts.append('</div>')

        return '\n'.join(html_parts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.get("/convert/{document_id}")
async def convert_document_to_html(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Convert a stored document to HTML format

    Returns:
        {
            "html": "<div>...</div>",
            "metadata": {...}
        }
    """

    # Fetch document from database
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    canonical_path = Path(db_document.canonical_path)

    if not canonical_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    # Convert based on file extension (canonical path is already normalized)
    # PDFs are converted to DOCX by the normalizer, so check the actual file type
    file_extension = canonical_path.suffix.lower()

    if file_extension == '.docx':
        html_content = docx_to_html(canonical_path)
    elif file_extension == '.pdf':
        # Shouldn't happen since normalizer converts PDF to DOCX
        html_content = '<div class="document-content"><p>PDF file was not properly converted to DOCX</p></div>'
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        # For images, show the image
        html_content = f'<div class="document-content"><img src="data:image/png;base64,TODO" alt="Document image" style="max-width: 100%;" /></div>'
    else:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_extension}' cannot be converted to HTML"
        )

    return {
        "html": html_content,
        "metadata": {
            "filename": db_document.original_filename,
            "type": db_document.type,
            "created_at": db_document.created_at.isoformat()
        }
    }


@router.get("/download/{document_id}")
async def download_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download the converted DOCX file directly

    This returns the actual DOCX file so the frontend can use mammoth.js
    to render it with full formatting preservation
    """

    # Fetch document from database
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    canonical_path = Path(db_document.canonical_path)

    if not canonical_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    # Return the DOCX file directly
    return FileResponse(
        path=str(canonical_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{db_document.original_filename}.docx" if not db_document.original_filename.endswith('.docx') else db_document.original_filename
    )


@router.get("/pdf/{document_id}")
async def download_original_pdf(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download the original PDF file for client-side rendering with react-pdf

    This returns the actual uploaded PDF file (not the converted DOCX)
    so the frontend can render it as a live, interactive document
    """

    # Fetch document from database
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get original path from metadata
    original_path_str = db_document.doc_metadata.get("original_path")

    if not original_path_str:
        raise HTTPException(status_code=404, detail="Original file path not found in metadata")

    original_path = Path(original_path_str)

    if not original_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found on disk")

    # Return the original PDF file
    return FileResponse(
        path=str(original_path),
        media_type="application/pdf",
        filename=db_document.original_filename
    )


@router.get("/docx-to-pdf/{document_id}")
async def convert_docx_to_pdf(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Convert a DOCX document to PDF using pandoc and return the PDF."""
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    canonical_path = Path(db_document.canonical_path)
    if not canonical_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    if canonical_path.suffix.lower() != '.docx':
        raise HTTPException(status_code=400, detail="Document is not a DOCX file")

    # Write PDF to a temp file (persisted until next request — simple cache by doc id)
    pdf_path = canonical_path.with_suffix('.pdf')
    if not pdf_path.exists():
        result = subprocess.run(
            ['pandoc', str(canonical_path), '-o', str(pdf_path), '--pdf-engine=xelatex'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"PDF conversion failed: {result.stderr}")

    stem = Path(db_document.original_filename).stem
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{stem}.pdf"
    )
