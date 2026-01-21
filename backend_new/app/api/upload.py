from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from uuid import uuid4

from app.db.session import get_db
from app.core.storage import storage_manager
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.document import Document
from app.models.db_models import DocumentModel, DocumentSpanModel, UserModel
from app.pipeline.normalize import normalizer
from app.pipeline.parse import parser

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Upload and process a document through the normalization and parsing pipeline

    Steps:
    1. Save uploaded file
    2. Normalize to canonical format (PDF→DOCX, IMG→PNG)
    3. Parse into DocumentSpans
    4. Store in database
    5. Return Document object
    """

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Supported: {settings.ALLOWED_EXTENSIONS}"
        )

    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )

    temp_path = None
    try:
        # Step 1: Save uploaded file temporarily
        temp_path = storage_manager.get_upload_path(f"temp_{uuid4()}{file_ext}")
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 2: Save original file permanently (for PDFs we need to keep both)
        original_path = storage_manager.get_upload_path(f"{uuid4()}{file_ext}")
        shutil.copy2(temp_path, original_path)

        # Step 3: Normalize
        canonical_path, doc_type = normalizer.normalize(temp_path)

        # Step 4: Parse into spans
        spans = parser.parse(canonical_path) if doc_type in ['pdf', 'docx'] else []

        # Step 5: Store document in database
        db_document = DocumentModel(
            type=doc_type,
            canonical_path=str(canonical_path),
            original_filename=file.filename,
            user_id=current_user.id,
            doc_metadata={
                "size_bytes": file_size,
                "original_extension": file_ext,
                "original_path": str(original_path)  # Store original PDF path
            }
        )
        db.add(db_document)
        db.flush()  # Get the document ID

        # Step 6: Store spans in database
        for span in spans:
            db_span = DocumentSpanModel(
                id=span.id,
                document_id=db_document.id,
                span_type=span.span_type,
                text=span.text,
                page=span.page,
                bbox=span.bbox
            )
            db.add(db_span)

        db.commit()
        db.refresh(db_document)

        # Step 7: Create response Document object
        document = Document(
            id=db_document.id,
            type=db_document.type,
            canonical_path=db_document.canonical_path,
            original_filename=db_document.original_filename,
            metadata=db_document.doc_metadata,
            structure=spans,
            created_at=db_document.created_at
        )

        # Clean up temp file if different from canonical
        if temp_path != canonical_path and temp_path.exists():
            temp_path.unlink()

        # Return as dict with explicit serialization
        return document.model_dump(mode='json')

    except Exception as e:
        # Clean up on error
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
