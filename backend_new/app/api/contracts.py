from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse, StreamingResponse
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
import asyncio
import mimetypes
import io

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


class PinUpdate(BaseModel):
    pinned: bool


class ContractSummary(BaseModel):
    id: str
    name: str
    status: str
    pinned: bool = False
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

def _heavy_process(file_path: Path, filename: str, file_size: int):
    """CPU-heavy normalize+parse — runs in a thread pool executor."""
    file_ext = Path(filename).suffix.lower()
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

    return original_path, canonical_path, doc_type, spans


async def _store_file_raw(
    file_path: Path,
    filename: str,
    file_size: int,
    contract_id,
    folder_id,
    user_id,
    db: Session
) -> Optional[DocumentModel]:
    """Just copy the file and record it — no pipeline, instant."""
    file_ext = Path(filename).suffix.lower()
    loop = asyncio.get_event_loop()

    def _copy():
        dest = storage_manager.get_upload_path(f"{uuid4()}{file_ext}")
        shutil.copy2(file_path, dest)
        return dest

    try:
        stored_path = await loop.run_in_executor(None, _copy)
    except Exception as e:
        print(f"Error storing file {filename}: {e}")
        return None

    doc_type = file_ext.lstrip('.') or 'raw'
    db_document = DocumentModel(
        type=doc_type,
        canonical_path=str(stored_path),
        original_filename=filename,
        user_id=user_id,
        contract_id=contract_id,
        folder_id=folder_id,
        doc_metadata={
            "size_bytes": file_size,
            "original_extension": file_ext,
            "original_path": str(stored_path)
        }
    )
    db.add(db_document)
    db.flush()
    return db_document


async def _process_file_async(
    file_path: Path,
    filename: str,
    file_size: int,
    contract_id,
    folder_id,
    user_id,
    db: Session
) -> Optional[DocumentModel]:
    """Run full normalize+parse pipeline — used for single-file uploads only."""
    file_ext = Path(filename).suffix.lower()
    loop = asyncio.get_event_loop()

    if file_ext in SUPPORTED_EXTENSIONS:
        try:
            original_path, canonical_path, doc_type, spans = await asyncio.wait_for(
                loop.run_in_executor(None, _heavy_process, file_path, filename, file_size),
                timeout=120.0
            )
        except asyncio.TimeoutError:
            print(f"Timeout processing file {filename} (>2 min) — falling back to raw store")
            return await _store_file_raw(file_path, filename, file_size, contract_id, folder_id, user_id, db)
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            return await _store_file_raw(file_path, filename, file_size, contract_id, folder_id, user_id, db)
    else:
        return await _store_file_raw(file_path, filename, file_size, contract_id, folder_id, user_id, db)

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
        pinned=bool(contract.pinned),
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
            pinned=bool(c.pinned),
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


@router.patch("/{contract_id}/pin", response_model=ContractSummary)
async def pin_contract(
    contract_id: str,
    data: PinUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pin or unpin a contract."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    contract.pinned = 1 if data.pinned else 0
    db.commit()
    db.refresh(contract)
    doc_count = db.query(DocumentModel).filter(DocumentModel.contract_id == contract.id).count()
    return ContractSummary(
        id=str(contract.id),
        name=contract.name,
        status=contract.status,
        pinned=bool(contract.pinned),
        created_at=contract.created_at.isoformat(),
        document_count=doc_count
    )


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

    # Enforce unique names within the same parent space
    duplicate = db.query(ContractFolderModel).filter(
        ContractFolderModel.contract_id == contract_id,
        ContractFolderModel.parent_id == parent_id,
        ContractFolderModel.name == data.name
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"A folder named '{data.name}' already exists here"
        )

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
    file_ext = Path(file.filename).suffix.lower()
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit")

    temp_path = storage_manager.get_upload_path(f"temp_{uuid4()}{file_ext}")
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    try:
        doc = await _store_file_raw(
            temp_path, file.filename, file_size,
            contract.id, resolved_folder_id, current_user.id, db
        )
        if not doc:
            raise HTTPException(status_code=500, detail="Failed to store file")
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

        folder_path_map: dict = {}
        processed_docs = []
        skipped = []
        timed_out = False

        async def _process_all():
            for root, dirs, files in os.walk(tmp_dir):
                dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
                rel_root = os.path.relpath(root, tmp_dir)

                if rel_root != '.':
                    parent_rel = os.path.dirname(rel_root)
                    par_id = parent_folder_id if parent_rel == '.' else folder_path_map.get(parent_rel)
                    folder_name = os.path.basename(rel_root)
                    folder_model = db.query(ContractFolderModel).filter(
                        ContractFolderModel.contract_id == contract.id,
                        ContractFolderModel.parent_id == par_id,
                        ContractFolderModel.name == folder_name
                    ).first()
                    if not folder_model:
                        folder_model = ContractFolderModel(
                            contract_id=contract.id, parent_id=par_id, name=folder_name
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
                    if filename.lower().endswith('.zip'):
                        continue
                    file_path = Path(root) / filename
                    file_size = file_path.stat().st_size
                    # Skip if an identical filename already exists at this location
                    existing = db.query(DocumentModel).filter(
                        DocumentModel.contract_id == contract.id,
                        DocumentModel.folder_id == current_folder_id,
                        DocumentModel.original_filename == filename,
                    ).first()
                    if existing:
                        skipped.append(filename)
                        continue
                    doc = await _store_file_raw(
                        file_path, filename, file_size,
                        contract.id, current_folder_id, current_user.id, db
                    )
                    if doc:
                        processed_docs.append(doc)
                    else:
                        skipped.append(filename)

        try:
            await asyncio.wait_for(_process_all(), timeout=120.0)
        except asyncio.TimeoutError:
            timed_out = True
            print(f"ZIP upload timed out after 2 minutes — committing {len(processed_docs)} processed files")

        db.commit()

    return {
        "processed": len(processed_docs),
        "skipped": skipped,
        "timed_out": timed_out,
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


@router.get("/{contract_id}/documents/{document_id}/raw")
async def get_document_raw(
    contract_id: str,
    document_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Serve raw file bytes for any document in a contract."""
    doc = db.query(DocumentModel).filter(
        DocumentModel.id == document_id,
        DocumentModel.contract_id == contract_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Try canonical path first, fall back to original_path in metadata
    file_path = Path(doc.canonical_path)
    if not file_path.exists():
        orig = (doc.doc_metadata or {}).get("original_path")
        if orig:
            file_path = Path(orig)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_type, _ = mimetypes.guess_type(doc.original_filename)
    return FileResponse(
        path=str(file_path),
        media_type=media_type or "application/octet-stream",
        filename=doc.original_filename
    )


class DocumentMove(BaseModel):
    folder_id: Optional[str] = None


@router.patch("/{contract_id}/documents/{document_id}/folder", response_model=DocumentSummary)
async def move_document(
    contract_id: str,
    document_id: str,
    data: DocumentMove,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move a document to a different folder (or root) within the same contract."""
    contract = db.query(ContractModel).filter(
        ContractModel.id == contract_id,
        ContractModel.user_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=403, detail="Not authorized")

    doc = db.query(DocumentModel).filter(
        DocumentModel.id == document_id,
        DocumentModel.contract_id == contract_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if data.folder_id:
        folder = db.query(ContractFolderModel).filter(
            ContractFolderModel.id == data.folder_id,
            ContractFolderModel.contract_id == contract_id
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Target folder not found")
        doc.folder_id = folder.id
    else:
        doc.folder_id = None

    db.commit()
    db.refresh(doc)
    return DocumentSummary(
        id=str(doc.id),
        original_filename=doc.original_filename,
        type=doc.type,
        created_at=doc.created_at.isoformat(),
        folder_id=str(doc.folder_id) if doc.folder_id else None
    )


@router.get("/{contract_id}/download-zip")
async def download_contract_zip(
    contract_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download all contract files as a ZIP, preserving folder structure."""
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

    # Build folder id → path map
    folder_map: dict = {}  # id -> Path-like string

    def _build_paths(parent_id=None, prefix=""):
        for f in folders:
            fid = str(f.id)
            fp = str(f.parent_id) if f.parent_id else None
            if fp == (str(parent_id) if parent_id else None):
                path = f"{prefix}{f.name}/" if prefix else f"{f.name}/"
                folder_map[fid] = path
                _build_paths(f.id, path)

    _build_paths()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for doc in documents:
            file_path = Path(doc.canonical_path)
            if not file_path.exists():
                orig = (doc.doc_metadata or {}).get("original_path")
                if orig:
                    file_path = Path(orig)
            if not file_path.exists():
                continue

            folder_prefix = ""
            if doc.folder_id:
                folder_prefix = folder_map.get(str(doc.folder_id), "")

            arcname = f"{folder_prefix}{doc.original_filename}"
            zf.write(file_path, arcname=arcname)

    buf.seek(0)
    safe_name = contract.name.replace(" ", "_").replace("/", "-")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.zip"'}
    )
