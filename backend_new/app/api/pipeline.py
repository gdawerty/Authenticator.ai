"""
Pipeline API - Exposes the Authentia Core document processing pipeline
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.db_models import DocumentModel, UserModel
from app.pipeline.authentia_core import AuthentiaAgent, FileType


router = APIRouter()


# Response models
class FileMetadataResponse(BaseModel):
    filename: str
    file_type: str
    file_size: int
    mime_type: str
    extension_matches_content: bool
    author: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    page_count: Optional[int] = None
    integrity_warnings: list[str] = []


class OCRResultResponse(BaseModel):
    text: str
    page_number: int
    confidence: Optional[float] = None


class ProcessedDocumentResponse(BaseModel):
    metadata: FileMetadataResponse
    ocr_results: list[OCRResultResponse]
    markdown_content: str
    processing_time: float


@router.get("/{document_id}/inspect", response_model=FileMetadataResponse)
async def inspect_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Inspect a document's file integrity and metadata.

    Returns:
    - File type validation (magic bytes vs extension)
    - Metadata extraction (author, dates, producer)
    - Integrity warnings
    """
    # Get document from database
    document = db.query(DocumentModel).filter(
        DocumentModel.id == str(document_id),
        DocumentModel.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get original file path
    original_path = document.doc_metadata.get("original_path")
    if not original_path:
        raise HTTPException(status_code=400, detail="Original file path not found")

    try:
        agent = AuthentiaAgent()
        metadata = agent.inspect_only(original_path)

        return FileMetadataResponse(
            filename=metadata.filename,
            file_type=metadata.file_type.value,
            file_size=metadata.file_size,
            mime_type=metadata.mime_type,
            extension_matches_content=metadata.extension_matches_content,
            author=metadata.author,
            creator=metadata.creator,
            producer=metadata.producer,
            creation_date=metadata.creation_date,
            modification_date=metadata.modification_date,
            title=metadata.title,
            subject=metadata.subject,
            page_count=metadata.page_count,
            integrity_warnings=metadata.integrity_warnings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspection failed: {str(e)}")


@router.get("/{document_id}/ocr", response_model=list[OCRResultResponse])
async def ocr_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Run OCR on a document.

    Returns extracted text per page with confidence scores.
    """
    # Get document from database
    document = db.query(DocumentModel).filter(
        DocumentModel.id == str(document_id),
        DocumentModel.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get original file path
    original_path = document.doc_metadata.get("original_path")
    if not original_path:
        raise HTTPException(status_code=400, detail="Original file path not found")

    try:
        agent = AuthentiaAgent()
        metadata = agent.inspect_only(original_path)
        ocr_results = agent.ocr_engine.extract_text(original_path, metadata.file_type)

        return [
            OCRResultResponse(
                text=r.text,
                page_number=r.page_number,
                confidence=r.confidence
            )
            for r in ocr_results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


@router.post("/{document_id}/process", response_model=ProcessedDocumentResponse)
async def process_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Run the full Authentia processing pipeline on a document.

    Steps:
    1. File inspection (magic bytes, metadata)
    2. OCR extraction
    3. Markdown normalization

    Returns complete processed document with metadata, OCR, and markdown.
    """
    # Get document from database
    document = db.query(DocumentModel).filter(
        DocumentModel.id == str(document_id),
        DocumentModel.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get original file path
    original_path = document.doc_metadata.get("original_path")
    if not original_path:
        raise HTTPException(status_code=400, detail="Original file path not found")

    try:
        agent = AuthentiaAgent()
        result = agent.process(original_path, save_markdown=False)

        return ProcessedDocumentResponse(
            metadata=FileMetadataResponse(
                filename=result.metadata.filename,
                file_type=result.metadata.file_type.value,
                file_size=result.metadata.file_size,
                mime_type=result.metadata.mime_type,
                extension_matches_content=result.metadata.extension_matches_content,
                author=result.metadata.author,
                creator=result.metadata.creator,
                producer=result.metadata.producer,
                creation_date=result.metadata.creation_date,
                modification_date=result.metadata.modification_date,
                title=result.metadata.title,
                subject=result.metadata.subject,
                page_count=result.metadata.page_count,
                integrity_warnings=result.metadata.integrity_warnings
            ),
            ocr_results=[
                OCRResultResponse(
                    text=r.text,
                    page_number=r.page_number,
                    confidence=r.confidence
                )
                for r in result.ocr_results
            ],
            markdown_content=result.markdown_content,
            processing_time=result.processing_time
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
