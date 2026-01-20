# Context Analyzer - Quick Start Guide

## ✅ Status: Implementation Complete!

The Context Analyzer is now fully integrated into your backend and ready to use.

## 🚀 What You Need to Do

### 1. Get Your Groq API Key (Free!)

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to "API Keys"
4. Create a new API key (starts with `gsk_`)
5. Copy the key

### 2. Add Your API Key to .env

Open `backend_new/.env` and replace the placeholder:

```bash
# Groq API
GROQ_API_KEY=gsk_your_actual_key_here  # Replace this!
GROQ_MODEL=mixtral-8x7b-32768
```

### 3. Restart Your Backend

The backend should auto-reload if it's running with `--reload` flag. If not:

```bash
cd /Users/prathamsaurabh/Authenticator.ai/backend_new
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## 🧪 Test It Out

### Option 1: Test with Sample Data

```bash
cd /Users/prathamsaurabh/Authenticator.ai/backend_new
python test_context_analyzer.py
```

This will analyze sample medical record chunks and show you the output.

### Option 2: Test with API

1. **Upload a document first:**
```bash
curl -X POST "http://localhost:8001/api/v1/upload/upload" \
  -F "file=@/path/to/your/document.pdf"
```

This will return a document ID like `"id": "123e4567-e89b-12d3-a456-426614174000"`

2. **Analyze its context:**
```bash
curl -X POST "http://localhost:8001/api/v1/documents/123e4567-e89b-12d3-a456-426614174000/analyze-context"
```

### Option 3: Test with Raw Chunks

```bash
curl -X POST "http://localhost:8001/api/v1/analyze-context-raw" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "00000000-0000-0000-0000-000000000000",
    "chunks": [
      {
        "chunk_id": "test_01",
        "page_number": 1,
        "text": "Invoice #12345\nDate: January 15, 2024\nBill To: Acme Corp\nTotal: $1,500.00"
      }
    ]
  }'
```

## 📊 What You'll Get Back

```json
{
  "document_id": "...",
  "page_narratives": [
    {
      "page_number": 1,
      "page_type": "INVOICE",
      "narrative_summary": "This page serves as a billing document...",
      "key_takeaway": "Invoice for services rendered",
      "supporting_chunks": ["test_01"]
    }
  ],
  "context_entities": {
    "primary_actors": ["Acme Corp"],
    "critical_dates": [
      {
        "date": "2024-01-15",
        "source_text": "January 15, 2024",
        "description": "Invoice Date"
      }
    ],
    "financial_values": [
      {
        "amount": 1500.0,
        "source_text": "$1,500.00",
        "description": "Total Amount"
      }
    ]
  }
}
```

## 🔍 Access API Documentation

Visit: http://localhost:8001/docs

You'll see all the endpoints including:
- `POST /api/v1/documents/{document_id}/analyze-context`
- `POST /api/v1/analyze-context-raw`

## 📁 Files Created

- `app/models/context.py` - Data models
- `app/pipeline/context.py` - Analyzer implementation
- `app/api/context.py` - API endpoints
- `test_context_analyzer.py` - Test script
- `CONTEXT_ANALYZER_README.md` - Full documentation

## ❓ Troubleshooting

**Error: "Groq API key required"**
- Make sure you've added your API key to `.env`
- Restart the backend after adding the key

**Error: "Document not found"**
- Upload a document first using `/api/v1/upload/upload`
- Use the correct document ID from the upload response

**Error: "No document spans found"**
- The document may not have been parsed correctly
- Try uploading a PDF or DOCX file (images aren't parsed into spans yet)

## 🎯 Next Steps

Once this is working, you can:

1. **Build the Evidence Layer** - Use context entities to identify evidence signals
2. **Create Frontend Integration** - Display narratives in the UI
3. **Add Batch Processing** - Analyze multiple documents at once
4. **Enhance Parsing** - Add page number detection for better narratives

## 📚 Full Documentation

See [CONTEXT_ANALYZER_README.md](CONTEXT_ANALYZER_README.md) for complete details.

---

**Ready to test?** Just add your Groq API key and run `python test_context_analyzer.py`!
