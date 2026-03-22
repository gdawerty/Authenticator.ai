from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4
import shutil
import zipfile
import tempfile
import os

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.storage import storage_manager
from app.core.config import settings
from app.models.db_models import (
    ContractModel, ContractFolderModel, DocumentModel,
    DocumentSpanModel, UserModel
)
from app.pipeline.normalize import normalizer
from app.pipeline.parse import parser

router = APIRouter()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}


# ─── Schemas ────────────────────────────────────────────────────────────────

class ContractCreate(BaseModel):
    name: str


class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None


class DocumentSummary(BaseModel):
    id: str
    original_filename: str
    type: str
    created_at: str
    folder_id: Optional[str]

    class Config:
        from_attributes = True


class FolderNode(BaseModel):
    id: str
    name: str
    parent_id: Optional[str]
    children: List['FolderNode'] = []
    documents: List[DocumentSummary] = []

    class Config:
        from_attributes = True

FolderNode.model_rebuild()


class ContractSummary(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    document_count: int = 0

    class Config:
        from_attributes = True


class ContractDetail(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    folders: List[FolderNode] = []
    root_documents: List[DocumentSummary] = []

    class Config:
        from_attributes = True


# ─── Helpers ────────────────────────────────────────────────────────────────

def _process_file(
    file_path: Path,
    filename: str,
    file_size: int,
    contract_id,
    folder_id,
    user_id,
    db: Session
) -> Optional[DocumentModel]:
    """Process a single file through the normalize/parse pipeline and store in DB."""
    file_ext = Path(filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        return None

    try:
        original_path = storage_manager.get_upload_path(f"{uuid4()}{file_ext}")
        shutil.copy2(file_path, original_path)

        canonical_path, doc_type = normalizer.normalize(file_path)

        if doc_type == 'pdf':
            spans = parser.parse(original_path)
        elif doc_type == 'docx':
            spans = parser.parse(canonical_path)
        elif doc_type == 'image':
            spans = parser.parse(original_path)
        else:
            spans = []

        db_document = DocumentModel(
            type=doc_type,
            canonical_path=str(canonical_path),
            original_filename=filename,
            user_id=user_id,
            contract_id=contract_id,
            folder_id=folder_id,
            doc_metadata={
                "size_bytes": file_size,
                "original_extension": file_ext,
                "original_path": str(original_path)
            }
        )
        db.add(db_document)
        db.flush()

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

        return db_document

    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return None


def _build_folder_tree(folders: list, documents: list, parent_id=None) -> list:
    """Recursively build folder tree."""
    nodes = []
    for folder in folders:
        folder_parent = str(folder.parent_id) if folder.parent_id else None
        compare_parent = str(parent_id) if parent_id else None
        if folder_parent == compare_parent:
            folder_docs = [
                DocumentSummary(
                    id=str(d.id),
                    original_filename=d.original_filename,
                    type=d.type,
                    created_at=d.created_at.isoformat(),
                    folder_id=str(d.folder_id) if d.folder_id else None
                )
                for d in documents
                if d.folder_id and str(d.folder_id) == str(folder.id)
            ]
            node = FolderNode(
                id=str(folder.id),
                name=folder.name,
                parent_id=str(folder.parent_id) if folder.parent_id else None,
                children=_build_folder_tree(folders, documents, folder.id),
                documents=folder_docs
            )
            nodes.append(node)
    return nodes


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("", response_model=ContractSummary, status_code=201)
async def create_contract(
    data: ContractCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new empty contract."""
    contract = ContractModel(
        user_id=current_user.id,
        name=data.name,
        status="pending"
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return ContractSummary(
        id=str(contract.id),
        name=contract.name,
        status=contract.status,
        created_at=contract.created_at.isoformat(),
        document_count=0
    )


@router.get("", response_model=List[ContractSummary])
async def list_contracts(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all contracts for the current user."""
    contracts = db.query(ContractModel).filter(
        ContractModel.user_id == current_user.id
    ).order_by(desc(ContractModel.created_at)).all()

    result = []
    for c in contracts:
        doc_count = db.query(DocumentModel).filter(
            DocumentModel.contract_id == c.id
        ).count()
        result.append(ContractSummary(
            id=str(c.id),
            name=c.name,
            status=c.status,
            created_at=c.created_at.isoformat(),
            document_count=doc_count
        ))
    return result


@router.get("/{contract_id}", response_model=ContractDetail)
async def get_contract(
    contract_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a contract with its full folder/file tree."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    folders = db.query(ContractFolderModel).filter(
        ContractFolderModel.contract_id == contract_id
    ).all()

    documents = db.query(DocumentModel).filter(
        DocumentModel.contract_id == contract_id
    ).all()

    root_docs = [
        DocumentSummary(
            id=str(d.id),
            original_filename=d.original_filename,
            type=d.type,
            created_at=d.created_at.isoformat(),
            folder_id=None
        )
        for d in documents if d.folder_id is None
    ]

    return ContractDetail(
        id=str(contract.id),
        name=contract.name,
        status=contract.status,
        created_at=contract.created_at.isoformat(),
        folders=_build_folder_tree(folders, documents),
        root_documents=root_docs
    )


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contract and all its contents."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    db.delete(contract)
    db.commit()


@router.post("/{contract_id}/folders", response_model=FolderNode, status_code=201)
async def create_folder(
    contract_id: str,
    data: FolderCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a subfolder inside a contract."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    parent_id = None
    if data.parent_id:
        parent = db.query(ContractFolderModel).filter(
            ContractFolderModel.id == data.parent_id,
            ContractFolderModel.contract_id == contract_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        parent_id = parent.id

    folder = ContractFolderModel(
        contract_id=contract_id,
        parent_id=parent_id,
        name=data.name
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)

    return FolderNode(
        id=str(folder.id),
        name=folder.name,
        parent_id=str(folder.parent_id) if folder.parent_id else None,
        children=[],
        documents=[]
    )


@router.post("/{contract_id}/upload")
async def upload_file(
    contract_id: str,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a single file into a contract (optionally into a specific folder)."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not supported")

    # Validate folder_id if provided
    resolved_folder_id = None
    if folder_id:
        folder = db.query(ContractFolderModel).filter(
            ContractFolderModel.id == folder_id,
            ContractFolderModel.contract_id == contract_id
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        resolved_folder_id = folder.id

    # Save temp file
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit")

    temp_path = storage_manager.get_upload_path(f"temp_{uuid4()}{file_ext}")
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    try:
        doc = _process_file(
            temp_path, file.filename, file_size,
            contract.id, resolved_folder_id, current_user.id, db
        )
        if not doc:
            raise HTTPException(status_code=500, detail="Failed to process file")
        db.commit()
        db.refresh(doc)
        return DocumentSummary(
            id=str(doc.id),
            original_filename=doc.original_filename,
            type=doc.type,
            created_at=doc.created_at.isoformat(),
            folder_id=str(doc.folder_id) if doc.folder_id else None
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.post("/{contract_id}/upload-zip")
async def upload_zip(
    contract_id: str,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a ZIP file and extract it into the contract, maintaining folder structure."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")

    # Validate parent folder
    parent_folder_id = None
    if folder_id:
        parent_folder = db.query(ContractFolderModel).filter(
            ContractFolderModel.id == folder_id,
            ContractFolderModel.contract_id == contract_id
        ).first()
        if not parent_folder:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        parent_folder_id = parent_folder.id

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save and extract ZIP
        zip_path = Path(tmp_dir) / "upload.zip"
        with zip_path.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid or corrupt ZIP file")

        zip_path.unlink()

        # Walk directory tree and create folder/file structure
        # folder_path_map: relative path string -> ContractFolderModel.id
        folder_path_map: dict = {}
        processed_docs = []
        skipped = []

        for root, dirs, files in os.walk(tmp_dir):
            # Skip __MACOSX and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]

            rel_root = os.path.relpath(root, tmp_dir)

            # Create folder model for non-root directories
            if rel_root != '.':
                parent_rel = os.path.dirname(rel_root)
                if parent_rel == '.':
                    par_id = parent_folder_id
                else:
                    par_id = folder_path_map.get(parent_rel)

                folder_model = ContractFolderModel(
                    contract_id=contract.id,
                    parent_id=par_id,
                    name=os.path.basename(rel_root)
                )
                db.add(folder_model)
                db.flush()
                folder_path_map[rel_root] = folder_model.id
                current_folder_id = folder_model.id
            else:
                current_folder_id = parent_folder_id

            for filename in files:
                if filename.startswith('.') or filename.startswith('__'):
                    continue
                file_path = Path(root) / filename
                file_size = file_path.stat().st_size
                doc = _process_file(
                    file_path, filename, file_size,
                    contract.id, current_folder_id, current_user.id, db
                )
                if doc:
                    processed_docs.append(doc)
                else:
                    skipped.append(filename)

        db.commit()

    return {
        "processed": len(processed_docs),
        "skipped": skipped,
        "documents": [
            DocumentSummary(
                id=str(d.id),
                original_filename=d.original_filename,
                type=d.type,
                created_at=d.created_at.isoformat(),
                folder_id=str(d.folder_id) if d.folder_id else None
            )
            for d in processed_docs
        ]
    }
