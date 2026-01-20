# Authenticator.AI - Document Intelligence Platform

A deterministic document processing pipeline with AI-powered context analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ (for backend)
- Node.js 18+ (for frontend)
- Groq API Key (free at https://console.groq.com)

---

## 📦 Backend Setup (backend_new)

### 1. Navigate to Backend Directory
```bash
cd backend_new
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Edit `backend_new/.env` and add your Groq API key:
```bash
# Groq API
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=mixtral-8x7b-32768
```

### 4. Run the Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

Backend will be available at:
- **API**: http://localhost:8002
- **Docs**: http://localhost:8002/docs
- **Health**: http://localhost:8002/health

---

## 🎨 Frontend Setup (frontend_new)

### 1. Navigate to Frontend Directory
```bash
cd frontend_new
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Run the Development Server
```bash
npm run dev
```

Frontend will be available at: **http://localhost:5175**

---

## 🔧 Features

### Document Processing Pipeline
```
Upload → Normalize → Parse → Context Analysis → Evidence Layer
```

1. **Upload**: PDF, DOCX, DOC, PNG, JPG, JPEG (max 50MB)
2. **Normalize**: Convert to canonical format (PDF→DOCX, IMG→PNG)
3. **Parse**: Extract text spans, tables, headings
4. **Context Analysis**: AI-powered narratives and entity extraction
5. **Evidence Layer**: (Coming soon)

### Context Analyzer
- **Page Narratives**: Executive-style summaries for each page
- **Entity Extraction**: Actors, dates, financial values
- **Neutral Analysis**: Descriptive, no judgment or risk scoring
- **Groq-Powered**: Fast inference with Mixtral-8x7B

---

## 📚 API Endpoints

### Document Upload
```bash
POST /api/v1/upload/upload
```
Upload and process a document through the pipeline.

**Example:**
```bash
curl -X POST "http://localhost:8002/api/v1/upload/upload" \
  -F "file=@document.pdf"
```

### Context Analysis
```bash
POST /api/v1/documents/{document_id}/analyze-context
```
Generate AI-powered context analysis for an uploaded document.

**Example:**
```bash
curl -X POST "http://localhost:8002/api/v1/documents/123e4567-e89b-12d3-a456-426614174000/analyze-context"
```

### Document Metadata
```bash
GET /api/v1/convert/{document_id}
```
Get document metadata (filename, type, created_at).

### PDF Retrieval
```bash
GET /api/v1/pdf/{document_id}
```
Retrieve the original PDF file for viewing.

---

## 📖 Documentation

- **Context Analyzer**: See [backend_new/CONTEXT_ANALYZER_README.md](backend_new/CONTEXT_ANALYZER_README.md)
- **Quick Start**: See [backend_new/QUICK_START.md](backend_new/QUICK_START.md)
- **Groq Integration**: See [docs/GROQ_INTEGRATION_GUIDE.md](docs/GROQ_INTEGRATION_GUIDE.md)

---

## 🗄️ Database

The backend uses SQLite by default:
- **Location**: `backend_new/authenticator.db`
- **Tables**: `documents`, `document_spans`, `evidence`

**View documents:**
```bash
sqlite3 backend_new/authenticator.db "SELECT id, original_filename, type FROM documents;"
```

---

## 🧪 Testing

### Test Context Analyzer
```bash
cd backend_new
python test_context_analyzer.py
```

### Test with Sample Document
```bash
# Upload a document
curl -X POST "http://localhost:8002/api/v1/upload/upload" \
  -F "file=@sample.pdf"

# Note the document ID from response
# Then analyze it
curl -X POST "http://localhost:8002/api/v1/documents/{document_id}/analyze-context"
```

---

## 🛠️ Development

### Kill Processes on Specific Ports
```bash
# Kill backend
lsof -ti:8002 | xargs kill -9

# Kill frontend
lsof -ti:5175 | xargs kill -9

# Kill multiple ports at once
for port in 5175 8002; do lsof -ti:$port | xargs kill -9 2>/dev/null; done
```

### View Backend Logs
```bash
# Backend runs in the terminal - logs appear in real-time
# Look for:
# - "Application startup complete" - backend is ready
# - API request logs - shows incoming requests
# - Error messages - debug issues
```

---

## 🏗️ Architecture

### Backend (backend_new)
- **Framework**: FastAPI + Uvicorn
- **Database**: SQLAlchemy + SQLite
- **AI**: Groq API (Mixtral-8x7B)
- **Document Processing**: pdf2docx, python-docx, Pillow

### Frontend (frontend_new)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI**: Tailwind CSS + Framer Motion
- **PDF Viewer**: react-pdf

---

## 📁 Project Structure

```
Authenticator.ai/
├── backend_new/           # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── db/           # Database
│   │   ├── models/       # Data models
│   │   ├── pipeline/     # Processing pipeline
│   │   └── main.py       # FastAPI app
│   ├── .env              # Environment variables
│   ├── requirements.txt  # Python dependencies
│   └── authenticator.db  # SQLite database
│
├── frontend_new/         # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   └── App.tsx       # Main app
│   ├── package.json      # Node dependencies
│   └── vite.config.ts    # Vite configuration
│
├── docs/                 # Documentation
└── README.md            # This file
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite:///./authenticator.db

# Storage
STORAGE_PATH=./storage
UPLOAD_PATH=./uploads

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Authenticator.AI Pipeline

# CORS
CORS_ORIGINS=["http://localhost:5174", "http://localhost:3000"]

# File Processing
MAX_FILE_SIZE_MB=50

# Groq API
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=mixtral-8x7b-32768
```

---

## 🐛 Troubleshooting

### Backend Won't Start
- Check if port 8002 is already in use: `lsof -ti:8002`
- Verify Python version: `python --version` (needs 3.13+)
- Check if all dependencies are installed: `pip install -r requirements.txt`

### Frontend Won't Start
- Check if port 5175 is already in use: `lsof -ti:5175`
- Verify Node.js version: `node --version` (needs 18+)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### Context Analyzer Fails
- Verify Groq API key is set in `.env`
- Restart backend after changing `.env`
- Check if document has been parsed: Document must be uploaded first

### Upload Fails
- Check file size (max 50MB)
- Verify file type (PDF, DOCX, DOC, PNG, JPG, JPEG)
- Check backend logs for errors

---

## 📊 Current Status

✅ Document upload and storage
✅ PDF/DOCX normalization
✅ Text extraction and parsing
✅ Context analyzer with AI narratives
✅ Entity extraction (actors, dates, financial values)
✅ Frontend document viewer
⏳ Evidence layer (in progress)
⏳ Risk scoring (planned)
⏳ Frontend context display (planned)

---

## 🤝 Contributing

This is a development project. To contribute:

1. Create a new branch from `clean-docker-setup`
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## 📝 License

[Add your license here]

---

## 🔗 Links

- **Groq Console**: https://console.groq.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

**Ready to analyze documents?** Start the backend, add your Groq API key, and upload your first document!
