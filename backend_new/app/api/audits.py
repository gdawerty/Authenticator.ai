from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel
from uuid import UUID

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.db_models import AuditModel, UserModel, DocumentModel

router = APIRouter()


class AuditCreate(BaseModel):
    """Audit creation schema"""
    name: str
    document_id: str  # UUID as string
    status: str = "clean"  # clean, warning, flagged


class AuditResponse(BaseModel):
    """Audit response schema"""
    id: str
    name: str
    document_id: str | None
    status: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit_data: AuditCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new audit for the current user"""
    # Validate document_id if provided
    document_id = None
    if audit_data.document_id:
        try:
            document_uuid_str = str(UUID(audit_data.document_id))
            # Verify the document belongs to the current user
            document = db.query(DocumentModel).filter(
                DocumentModel.id == document_uuid_str,
                DocumentModel.user_id == current_user.id
            ).first()
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found or access denied"
                )
            document_id = document_uuid_str
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID format"
            )

    # Create audit
    db_audit = AuditModel(
        user_id=current_user.id,
        name=audit_data.name,
        document_id=document_id,
        status=audit_data.status
    )
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)

    return AuditResponse(
        id=str(db_audit.id),
        name=db_audit.name,
        document_id=str(db_audit.document_id) if db_audit.document_id else None,
        status=db_audit.status,
        created_at=db_audit.created_at.isoformat()
    )


@router.get("", response_model=List[AuditResponse])
async def get_audits(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all audits for the current user"""
    audits = db.query(AuditModel).filter(
        AuditModel.user_id == current_user.id
    ).order_by(desc(AuditModel.created_at)).offset(skip).limit(limit).all()

    return [
        AuditResponse(
            id=str(audit.id),
            name=audit.name,
            document_id=str(audit.document_id) if audit.document_id else None,
            status=audit.status,
            created_at=audit.created_at.isoformat()
        )
        for audit in audits
    ]
