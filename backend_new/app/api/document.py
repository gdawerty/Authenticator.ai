from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.document import Document, DocumentSpan
from app.models.db_models import DocumentModel, DocumentSpanModel

router = APIRouter()


@router.get("/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a document by ID with all its spans
    """
    # TODO: Implement database retrieval
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/documents", response_model=List[Document])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all documents
    """
    # TODO: Implement database listing
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/documents/{document_id}/spans")
async def get_document_spans(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all spans for a specific document

    Returns the extracted text spans (paragraphs, headings, tables) from the document.
    """
    # Check if document exists
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    # Fetch spans
    spans = db.query(DocumentSpanModel).filter(
        DocumentSpanModel.document_id == document_id
    ).order_by(DocumentSpanModel.page, DocumentSpanModel.id).all()

    # Convert to response format
    return {
        "document_id": str(document_id),
        "span_count": len(spans),
        "spans": [
            {
                "id": str(span.id),
                "span_type": span.span_type,
                "text": span.text,
                "page": span.page,
                "bbox": span.bbox
            }
            for span in spans
        ]
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a document and all its spans
    """
    # TODO: Implement deletion
    raise HTTPException(status_code=501, detail="Not implemented yet")
