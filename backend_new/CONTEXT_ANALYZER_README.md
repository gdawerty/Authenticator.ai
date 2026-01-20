# Context Analyzer - Document Intelligence Layer

## Overview

The Context Analyzer is a powerful document intelligence layer that acts as a **Human-in-the-Loop context builder**. It transforms parsed document spans into human-readable narratives and structured context entities using AI.

## Key Features

✅ **Page-Level Narratives** - Executive-style summaries for each page explaining what it contains and why it exists
✅ **Context Entity Extraction** - Automatically identifies actors, dates, and financial values
✅ **Neutral & Descriptive** - No auditing or judgment, only factual description
✅ **Groq-Powered** - Uses Mixtral-8x7B for fast, accurate analysis
✅ **Backend-Ready** - Clean JSON output for easy integration

## Architecture

```
Document Upload → Normalize → Parse → Context Analyzer → Evidence Layer
                                              ↓
                                    Page Narratives
                                    Context Entities
```

## Setup

### 1. Install Dependencies

```bash
cd backend_new
pip install -r requirements.txt
```

### 2. Configure Groq API

Add your Groq API key to [.env](backend_new/.env):

```bash
# Groq API
GROQ_API_KEY=gsk_your_actual_groq_key_here
GROQ_MODEL=mixtral-8x7b-32768
```

Get a free Groq API key at: https://console.groq.com

### 3. Start the Backend

```bash
cd backend_new
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## API Endpoints

### 1. Analyze Document Context (From Database)

**Endpoint:** `POST /api/v1/documents/{document_id}/analyze-context`

Analyzes a document that's already been uploaded and parsed.

**Example:**
```bash
curl -X POST "http://localhost:8001/api/v1/documents/123e4567-e89b-12d3-a456-426614174000/analyze-context"
```

**Response:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "page_narratives": [
    {
      "page_number": 1,
      "page_type": "MEDICAL_RECORD",
      "narrative_summary": "This page serves as an introductory overview, identifying the primary individual and outlining the reported incident and associated reference numbers...",
      "key_takeaway": "Establishes parties and foundational context.",
      "supporting_chunks": ["chunk_01", "chunk_02"]
    }
  ],
  "context_entities": {
    "primary_actors": ["John Smith", "ABC Medical Center"],
    "critical_dates": [
      {
        "date": "2024-03-20",
        "source_text": "March 20, 2024",
        "description": "Date of Visit"
      }
    ],
    "financial_values": [
      {
        "amount": 250.00,
        "source_text": "$250.00",
        "description": "Total Charges"
      }
    ]
  }
}
```

### 2. Analyze Raw Chunks (Testing)

**Endpoint:** `POST /api/v1/analyze-context-raw`

Analyzes chunks directly without needing a document in the database.

**Example:**
```bash
curl -X POST "http://localhost:8001/api/v1/analyze-context-raw" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "chunks": [
      {
        "chunk_id": "chunk_01",
        "page_number": 1,
        "text": "Patient: John Smith\nDate of Visit: March 20, 2024"
      }
    ]
  }'
```

## Output Format

### Page Narratives

Each page gets a narrative that includes:
- **page_number**: Page number in the document
- **page_type**: Category (FORM, INVOICE, CORRESPONDENCE, LEGAL, MEDICAL_RECORD, OTHER)
- **narrative_summary**: Executive-style description of the page
- **key_takeaway**: Brief summary of the page's purpose
- **supporting_chunks**: List of chunk IDs that support this narrative

### Context Entities

Structured extraction of key entities:

**Primary Actors**: Names of people and organizations
**Critical Dates**: Important dates with source text and description
**Financial Values**: Monetary amounts with source text and description

## Narrative Style

The analyzer produces professional, neutral narratives that:
- Describe what the document contains, not what it means
- Use executive phrasing like "This page serves to document..."
- Clearly state page structure (tabular, legal boilerplate, etc.)
- Avoid judgment words like "fraud", "suspicious", "anomaly"

## Integration Example

```python
from app.pipeline.context import get_context_analyzer
from app.models.context import ChunkInput
from uuid import uuid4

# Prepare chunks
chunks = [
    ChunkInput(
        chunk_id="chunk_01",
        page_number=1,
        text="Patient: John Smith..."
    )
]

# Analyze
analyzer = get_context_analyzer()
context = analyzer.analyze(
    document_id=uuid4(),
    chunks=chunks
)

# Access results
for narrative in context.page_narratives:
    print(f"Page {narrative.page_number}: {narrative.key_takeaway}")

for actor in context.context_entities.primary_actors:
    print(f"Actor: {actor}")
```

## Testing

Run the test script:

```bash
cd backend_new
python test_context_analyzer.py
```

This will analyze sample medical record chunks and display the results.

## File Structure

```
backend_new/
├── app/
│   ├── models/
│   │   └── context.py          # Data models for context analysis
│   ├── pipeline/
│   │   └── context.py          # Context analyzer implementation
│   └── api/
│       └── context.py          # API endpoints
├── test_context_analyzer.py    # Test script
└── CONTEXT_ANALYZER_README.md  # This file
```

## Models Used

- **Default**: `mixtral-8x7b-32768` (Groq)
- Alternative: `mistral-7b` (faster but less accurate)

Set via `GROQ_MODEL` environment variable.

## Error Handling

The analyzer handles:
- Missing API keys (returns 500 with clear error message)
- Malformed JSON responses (attempts to extract JSON from markdown)
- Empty or invalid chunks (returns 400 with validation error)
- Database lookup failures (returns 404 if document not found)

## Next Steps

This context analyzer is the foundation for the evidence layer. The next steps are:

1. **Evidence Layer**: Use context entities to identify specific evidence signals
2. **Risk Scoring**: Combine evidence to generate risk scores
3. **Frontend Integration**: Display narratives and entities in the UI
4. **Batch Processing**: Process multiple documents in parallel

## Support

For issues or questions:
- Check the `.env` file for correct GROQ_API_KEY
- Ensure the backend is running on port 8001
- Review logs for detailed error messages
- Test with `test_context_analyzer.py` first
