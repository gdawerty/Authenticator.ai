# Authenticator.AI - Project Structure

## Overview
This document describes the cleaned and organized project structure.

## Active Directories

### 📁 backend_new/
**Purpose**: FastAPI backend server (SQLite database)
- Main application code in `app/`
- Database models using SQLAlchemy
- PDF to DOCX conversion pipeline
- Document upload and storage endpoints
- **Run**: `cd backend_new && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002`
- **Initialize DB**: `cd backend_new && python init_db.py`

### 📁 frontend_new/
**Purpose**: React + TypeScript + Vite frontend
- Document viewer with PDF rendering (react-pdf)
- Upload interface with drag-and-drop
- Zoom controls (50% - 200%)
- Page navigation for multi-page PDFs
- **Run**: `cd frontend_new && npm run dev`
- **URL**: http://localhost:5175

### 📁 data/
**Purpose**: Training data and datasets
- Model training data
- Evaluation datasets

## Organizational Directories

### 📁 archive/
**Purpose**: Old/deprecated code and configurations
- `backend_old/` - Previous Flask backend
- `frontend_old/` - Previous frontend version
- `BERT/`, `ViT/`, `authentia-ai/`, `src/` - Old model code
- Old Docker configurations

### 📁 docs/
**Purpose**: Project documentation
- Setup guides (GROQ, Docker, Backend)
- Implementation checklists
- Architecture documentation
- Sprint planning documents

### 📁 scripts/
**Purpose**: Utility scripts and tests
- Deployment scripts
- Test scripts for GROQ integration
- Docker setup scripts
- Backend test scripts

## Key Files

### Root Level
- **README.md** - Main project documentation
- **.gitignore** - Git ignore rules (updated for new structure)
- **.gitattributes** - Git attributes
- **PROJECT_STRUCTURE.md** - This file

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (local development)
- **ORM**: SQLAlchemy
- **PDF Processing**: pdf2docx, python-docx
- **Port**: 8002

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **PDF Rendering**: react-pdf (with PDF.js)
- **Port**: 5175

## Getting Started

1. **Start Backend**:
   ```bash
   cd backend_new
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
   ```

2. **Start Frontend**:
   ```bash
   cd frontend_new
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:5175
   - Backend API: http://localhost:8002
   - API Docs: http://localhost:8002/docs

## Database

- **Type**: SQLite
- **Location**: `backend_new/authenticator.db`
- **Initialize**: `cd backend_new && python init_db.py`
- **Reset**: Delete `authenticator.db` and run init script again

## Recent Changes

- ✅ Organized all documentation into `docs/`
- ✅ Moved all scripts to `scripts/`
- ✅ Archived old backend and frontend
- ✅ Cleaned up root directory
- ✅ Updated .gitignore for new structure
- ✅ Switched to SQLite for easier local development
- ✅ Implemented professional PDF viewer with zoom and navigation controls
