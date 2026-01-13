from uuid import UUID, uuid4
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Evidence(BaseModel):
    """Evidence record for a document span - enables explainability"""
    id: UUID = Field(default_factory=uuid4)
    span_id: UUID
    signal_type: str  # e.g., "ai_generated", "clone_match", "metadata_anomaly"
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    raw_data: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "456e7890-e89b-12d3-a456-426614174000",
                "signal_type": "ai_generated",
                "confidence": 0.87,
                "explanation": "Text shows high perplexity typical of GPT-3.5 generation",
                "raw_data": {"perplexity": 12.3, "burstiness": 0.45}
            }
        }
