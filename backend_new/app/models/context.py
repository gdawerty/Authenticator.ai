from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from uuid import UUID


class CriticalDate(BaseModel):
    """Represents a critical date found in the document"""
    date: str  # YYYY-MM-DD format
    source_text: str  # Exact text from document
    description: str  # Brief factual description


class FinancialValue(BaseModel):
    """Represents a financial value found in the document"""
    amount: float
    source_text: str  # Exact text from document
    description: str  # Brief factual description


class ContextEntities(BaseModel):
    """Structured entities extracted from the document"""
    primary_actors: List[str] = Field(default_factory=list, description="Normalized names of individuals or organizations")
    critical_dates: List[CriticalDate] = Field(default_factory=list)
    financial_values: List[FinancialValue] = Field(default_factory=list)


class PageNarrative(BaseModel):
    """Narrative summary for a single page"""
    page_number: int
    page_type: Literal["FORM", "INVOICE", "CORRESPONDENCE", "LEGAL", "MEDICAL_RECORD", "OTHER"]
    narrative_summary: str = Field(description="Executive-style narrative explaining the page")
    key_takeaway: str = Field(description="Brief summary of the page's purpose")
    supporting_chunks: List[str] = Field(default_factory=list, description="List of chunk IDs that support this narrative")


class DocumentContext(BaseModel):
    """Complete context analysis for a document"""
    document_id: UUID
    page_narratives: List[PageNarrative] = Field(default_factory=list)
    context_entities: ContextEntities = Field(default_factory=ContextEntities)


class ChunkInput(BaseModel):
    """Input format for text chunks"""
    chunk_id: str
    page_number: int
    text: str
