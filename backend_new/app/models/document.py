from uuid import UUID, uuid4
from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentSpan(BaseModel):
    """Atomic unit of truth - represents a single structural element in a document"""
    id: UUID = Field(default_factory=uuid4)
    span_type: Literal["title", "paragraph", "table", "image", "heading"]
    text: str
    page: Optional[int] = None
    bbox: Optional[dict] = None  # Bounding box coordinates

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "span_type": "paragraph",
                "text": "This is a sample paragraph.",
                "page": 1,
                "bbox": {"x": 100, "y": 200, "width": 400, "height": 50}
            }
        }


class Document(BaseModel):
    """Canonical document object - everything revolves around this"""
    id: UUID = Field(default_factory=uuid4)
    type: Literal["pdf", "docx", "image"]
    canonical_path: str  # Path to normalized file
    original_filename: str
    company_id: Optional[UUID] = None
    metadata: dict = Field(default_factory=dict)
    structure: list[DocumentSpan] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "pdf",
                "canonical_path": "/storage/documents/doc-123.docx",
                "original_filename": "contract.pdf",
                "metadata": {"pages": 5, "size_bytes": 102400},
                "structure": []
            }
        },
        "json_encoders": {
            UUID: str
        }
    }
