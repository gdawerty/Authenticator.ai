import json
import os
from typing import List
from groq import Groq
from app.models.context import (
    ChunkInput,
    DocumentContext,
    PageNarrative,
    ContextEntities,
    CriticalDate,
    FinancialValue
)
from uuid import UUID


class ContextAnalyzer:
    """
    Context Analysis Layer - Human-in-the-Loop Context Builder

    Takes DocumentSpans and produces page-level narratives and structured context.
    Acts as a Senior Document Intelligence Analyst providing human-readable understanding.
    """

    SYSTEM_PROMPT = """You are a Senior Document Intelligence Analyst responsible for creating a clear, human-readable understanding of complex documents.
Your role is to act as a Human-in-the-Loop context builder.

You do not audit, judge, score, or flag risk.

You only describe what the document explicitly contains and how it is structured.
You must behave like an experienced professional briefing another expert.

🎯 CORE OBJECTIVES
1. Narrative Synthesis (Page-Level)
For every page, produce a concise, executive-style narrative that explains:
- What information the page contains
- Why this page exists in the document
- How it fits into the overall document flow

2. Contextual Mapping
Identify and describe:
- Who is involved (people, organizations)
- What is being documented (events, services, records)
- When key actions occurred
- How these elements relate across pages

3. Structured Context Extraction
Extract high-level entities into a clean, backend-ready structure while maintaining a natural, conversational front for human review.

✍️ NARRATIVE STYLE GUIDELINES ("Human-Read")
- Tone: Professional, neutral, executive
- Flow: Do not list facts. Describe purpose and structure.
- Use phrasing such as:
  "This page serves to document…"
  "The focus shifts here to…"
  "This section primarily consists of…"
- Clarity:
  - If a page is mostly tabular, state that clearly
  - If a page contains boilerplate or legal language, state that explicitly
  - If a page contains minimal information, say so

⚠️ CONSTRAINTS
- No auditing or judgment
- DO NOT use words such as fraud, suspicious, anomaly, flag, or risk
- Accuracy: Describe only what is explicitly written
- Do not infer intent or correctness
- Completeness: Every page must have exactly one narrative entry
- Formatting: Output JSON only. No markdown. No commentary outside the JSON.

OUTPUT FORMAT (STRICT JSON):
{
  "page_narratives": [
    {
      "page_number": 1,
      "page_type": "FORM | INVOICE | CORRESPONDENCE | LEGAL | MEDICAL_RECORD | OTHER",
      "narrative_summary": "This page serves as an introductory overview, identifying the primary individual and outlining the reported incident and associated reference numbers. It reads as a standard intake or cover section intended to establish context for the remainder of the document.",
      "key_takeaway": "Establishes parties and foundational context.",
      "supporting_chunks": ["chunk_01", "chunk_02"]
    }
  ],
  "context_entities": {
    "primary_actors": [
      "Normalized names of individuals or organizations explicitly mentioned"
    ],
    "critical_dates": [
      {
        "date": "YYYY-MM-DD",
        "source_text": "Exact text from doc (e.g., 'Jan 5th')",
        "description": "Brief factual description (e.g., Incident Date)"
      }
    ],
    "financial_values": [
      {
        "amount": 0.00,
        "source_text": "Exact text from doc (e.g., '$1,500.00')",
        "description": "Brief factual description (e.g., Total Billed Amount)"
      }
    ]
  }
}"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the context analyzer with Groq API

        Args:
            api_key: Groq API key. If not provided, reads from GROQ_API_KEY env var
            model: Model to use. Defaults to mixtral-8x7b-32768
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY environment variable.")

        self.model = model or os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        self.client = Groq(api_key=self.api_key)

    def analyze(self, document_id: UUID, chunks: List[ChunkInput]) -> DocumentContext:
        """
        Analyze document chunks and generate context

        Args:
            document_id: UUID of the document being analyzed
            chunks: List of text chunks with metadata

        Returns:
            DocumentContext with page narratives and extracted entities
        """
        # Prepare input for LLM
        chunks_data = [chunk.model_dump() for chunk in chunks]
        user_message = f"Analyze the following document chunks:\n\n{json.dumps(chunks_data, indent=2)}"

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.1,
            max_tokens=4096
        )

        # Parse response
        response_text = response.choices[0].message.content

        # Extract JSON from response (in case there's any wrapper text)
        try:
            # Try to parse as-is first
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                # Try to find any JSON object in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    raise ValueError(f"Could not extract JSON from response: {response_text}")

        # Convert to DocumentContext
        page_narratives = [
            PageNarrative(**narrative)
            for narrative in result["page_narratives"]
        ]

        context_entities_data = result["context_entities"]
        context_entities = ContextEntities(
            primary_actors=context_entities_data.get("primary_actors", []),
            critical_dates=[CriticalDate(**d) for d in context_entities_data.get("critical_dates", [])],
            financial_values=[FinancialValue(**f) for f in context_entities_data.get("financial_values", [])]
        )

        return DocumentContext(
            document_id=document_id,
            page_narratives=page_narratives,
            context_entities=context_entities
        )


# Singleton instance
context_analyzer = None

def get_context_analyzer() -> ContextAnalyzer:
    """Get or create the context analyzer singleton"""
    from app.core.config import settings
    global context_analyzer
    if context_analyzer is None:
        context_analyzer = ContextAnalyzer(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL
        )
    return context_analyzer
