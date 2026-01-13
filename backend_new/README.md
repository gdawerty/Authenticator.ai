# Authenticator.AI Backend - Week 1 Spine

A deterministic document processing pipeline built with FastAPI.

## Architecture

Think of this as a **compiler pipeline**, not an AI system:

```
Upload → Normalize → Parse → Structure → Context → Evidence → Decision
```

## Structure

```
backend_new/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API endpoints
│   │   ├── upload.py        # File upload & processing
│   │   └── document.py      # Document CRUD
│   ├── core/                # Core configuration
│   │   ├── config.py        # App settings
│   │   └── storage.py       # File storage manager
│   ├── pipeline/            # Processing pipeline
│   │   ├── normalize.py     # PDF/Image → DOCX/PNG
│   │   ├── parse.py         # DOCX → DocumentSpans
│   │   ├── context.py       # (TODO)
│   │   ├── evidence.py      # (TODO)
│   │   └── predict.py       # (TODO)
│   ├── models/              # Data models
│   │   ├── document.py      # Canonical Document & DocumentSpan
│   │   └── evidence.py      # Evidence model
│   ├── db/                  # Database
│   │   ├── session.py       # SQLAlchemy setup
│   │   └── schema.sql       # PostgreSQL schema
│   └── utils/               # Utilities
└── requirements.txt
```

## Key Concepts

### 1. Canonical Document Object

Everything revolves around this:

```python
class Document:
    id: UUID
    type: "pdf" | "docx" | "image"
    canonical_path: str
    metadata: dict
    structure: list[DocumentSpan]
```

### 2. DocumentSpan (Atomic Unit)

```python
class DocumentSpan:
    id: UUID
    span_type: "title" | "paragraph" | "table" | "image"
    text: str
    page: int | None
    bbox: dict | None
```

Every highlight maps to a DocumentSpan.

### 3. Pipeline Stages

#### Normalization (Deterministic)
- PDF → DOCX (layout preserved)
- Image → PNG
- DOCX → DOCX (passthrough)

#### Parsing (Deterministic)
- Extract paragraphs, headings, tables
- Assign stable span IDs
- Store in PostgreSQL immediately

## Database Schema

```sql
documents (
  id UUID PK,
  type VARCHAR,
  canonical_path TEXT,
  original_filename TEXT,
  company_id UUID,
  metadata JSONB
)

document_spans (
  id UUID PK,
  document_id UUID FK,
  span_type VARCHAR,
  text TEXT,
  page INT,
  bbox JSONB
)

evidence (
  id UUID PK,
  span_id UUID FK,
  signal_type VARCHAR,
  confidence FLOAT,
  explanation TEXT,
  raw_data JSONB
)
```

## Installation

```bash
cd backend_new
pip install -r requirements.txt
```

## Running

```bash
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## API Endpoints

- `POST /api/v1/upload/upload` - Upload and process document
- `GET /api/v1/documents/{id}` - Get document by ID
- `GET /api/v1/documents` - List all documents
- `GET /api/v1/documents/{id}/spans` - Get document spans
- `DELETE /api/v1/documents/{id}` - Delete document

## Week 1 Goals (NO ML)

- [x] Service layout
- [x] Canonical Document object
- [x] Normalization layer
- [x] Parsing layer
- [x] PostgreSQL schema
- [ ] Database integration
- [ ] Upload endpoint testing

## Next Steps

1. Implement database storage in upload endpoint
2. Implement document retrieval endpoints
3. Add context layer (Week 2)
4. Add evidence layer (Week 2)
5. Add ML prediction layer (Week 3)
