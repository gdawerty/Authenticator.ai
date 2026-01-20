from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.db_models import DocumentModel, DocumentSpanModel
from app.models.context import ChunkInput, DocumentContext
from app.pipeline.context import get_context_analyzer

router = APIRouter()


@router.post("/documents/{document_id}/analyze-context", response_model=DocumentContext)
async def analyze_document_context(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Analyze document context and generate page narratives

    Takes a document's parsed spans and generates:
    - Page-level narrative summaries
    - Extracted context entities (actors, dates, financial values)

    Args:
        document_id: UUID of the document to analyze

    Returns:
        DocumentContext with narratives and entities
    """
    # Fetch document from database
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    # Fetch spans
    spans = db.query(DocumentSpanModel).filter(
        DocumentSpanModel.document_id == document_id
    ).order_by(DocumentSpanModel.page, DocumentSpanModel.id).all()

    if not spans:
        raise HTTPException(
            status_code=400,
            detail="No document spans found. Document may not have been parsed yet."
        )

    # Convert spans to chunks for context analysis
    chunks = [
        ChunkInput(
            chunk_id=str(span.id),
            page_number=span.page or 1,  # Default to page 1 if page number not available
            text=span.text
        )
        for span in spans
    ]

    # Analyze context
    try:
        analyzer = get_context_analyzer()
        context = analyzer.analyze(document_id=document_id, chunks=chunks)
        return context
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Context analysis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during context analysis: {str(e)}")


@router.post("/analyze-context-raw", response_model=DocumentContext)
async def analyze_context_raw(
    document_id: UUID,
    chunks: List[ChunkInput]
):
    """
    Analyze context from raw chunks (without database lookup)

    Useful for testing or analyzing documents that aren't in the database yet.

    Args:
        document_id: UUID to associate with the analysis
        chunks: List of text chunks with metadata

    Returns:
        DocumentContext with narratives and entities
    """
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")

    try:
        analyzer = get_context_analyzer()
        context = analyzer.analyze(document_id=document_id, chunks=chunks)
        return context
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Context analysis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during context analysis: {str(e)}")
