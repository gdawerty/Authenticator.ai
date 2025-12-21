# Authenticator.ai Unified Application - V1 Launch

## Overview

`app_unified.py` is the unified Flask application for Authenticator.ai V1 that handles both document and image classification using:
- **BERT Model**: For document classification (PDF, DOCX) with 138 subcategories across 5 main categories
- **ViT Model**: For image classification using Vision Transformer
- **Parsing Service**: For text extraction from documents using OCR

## Key Features

### ✅ Unified Endpoints
- **Text Classification**: `/api/classify/text` - BERT-based text classification
- **Image Classification**: `/api/classify/image` - ViT-based image classification
- **Unified Analysis**: `/api/analyze/unified` - Handles all file types (PDF, DOCX, images)
- **Health Check**: `/api/health` - Check model and service status

### ✅ File Type Support
- **PDFs**: Text extraction + BERT classification
- **DOCX/DOC**: Text extraction + BERT classification
- **Images**: ViT classification + optional OCR text extraction

### ✅ Model Information
- **BERT Model**: 138 subcategories trained on diverse document types
  - Education (21 subcategories)
  - Finance (23 subcategories)
  - Medical (24 subcategories)
  - Other (51 subcategories)
  - Supply Chain (20 subcategories)

- **ViT Model**: Vision Transformer for image classification

## Running the Application

### Prerequisites
```bash
cd /Users/prathamsaurabh/Authenticator.ai/backend
pip install -r requirements.txt
```

### Start the Server
```bash
python3 app_unified.py
```

The application will start on `http://localhost:5000`

### API Documentation
- Swagger UI: `http://localhost:5000/api/docs`
- ReDoc: `http://localhost:5000/api/redoc`

## API Endpoints

### 1. Unified Analysis (Recommended)
**POST** `/api/analyze/unified`

Handles all file types with automatic routing:

```bash
curl -X POST "http://localhost:5000/api/analyze/unified" \
  -F "file=@document.pdf" \
  -F "analysis_type=comprehensive"
```

**Response:**
```json
{
  "success": true,
  "file_id": "document_20250115_100000_abc12345",
  "filename": "document.pdf",
  "file_type": "pdf",
  "raw_text": "Extracted text content...",
  "classification": {
    "prediction": "Education_Transcripts",
    "confidence": 0.92,
    "method": "BERT",
    "model": "bert-base-uncased (138 subcategories)"
  },
  "authenticity_score": 0.92,
  "text_extracted": true,
  "text_length": 5234,
  "timestamp": "2025-01-15T10:00:00.000000"
}
```

### 2. Text Classification
**POST** `/api/classify/text`

For direct text classification using BERT:

```bash
curl -X POST "http://localhost:5000/api/classify/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text content here..."}'
```

### 3. Image Classification
**POST** `/api/classify/image`

For image classification using ViT:

```bash
curl -X POST "http://localhost:5000/api/classify/image" \
  -F "file=@image.jpg"
```

### 4. Health Check
**GET** `/api/health`

```bash
curl "http://localhost:5000/api/health"
```

**Response:**
```json
{
  "status": "online",
  "bert_model": "healthy",
  "vit_model": "healthy",
  "parsing_service": "healthy",
  "timestamp": "2025-01-15T10:00:00.000000"
}
```

## Frontend Integration

The frontend (port 5173) should send requests to `http://localhost:8001/api/analyze` or use the unified endpoint on port 5000.

### Key Points for Frontend
1. **Document Upload**: Set `content_type='document'` and upload PDF/DOCX
   - The response will include `raw_text` with extracted content
   - Classification will use BERT model

2. **Image Upload**: Set `content_type='image'` and upload image file
   - Classification will use ViT model
   - Optional text extraction via OCR

3. **Check for `raw_text`**: Always check if `analysisResult?.raw_text` exists in DemoModal
   - If present, display the extracted content
   - If not, show appropriate loading/error state

## BERT Model Details

### Model Path
- Location: `/Users/prathamsaurabh/Authenticator.ai/BERT/models/best_model.pt`
- Label Map: `/Users/prathamsaurabh/Authenticator.ai/BERT/models/label_map.json`
- Checkpoint Size: ~438MB

### Label Map Structure
```json
{
  "label_map": {
    "0": "Education_academic_journals",
    "1": "Education_attendance_logs",
    ...
    "138": "Supply_Chain_warehouse_reports"
  }
}
```

### Training Configuration
- Base Model: `bert-base-uncased`
- Max Sequence Length: 512
- Number of Categories: 139 (0-138)
- Device: CPU or CUDA (auto-detected)

## ViT Model Details

### Model Path
- Location: `/Users/prathamsaurabh/Authenticator.ai/ViT/vit_model_artifacts/`
- Config: `config.json`
- Model: `model.safetensors`
- Label Map: `id_to_label.json`

## Troubleshooting

### Issue: "BERT model not loaded"
**Solution**: Check BERT model files exist at:
```bash
ls -la /Users/prathamsaurabh/Authenticator.ai/BERT/models/
```

Expected files:
- `best_model.pt` (438MB)
- `label_map.json`
- `training_history.json`

### Issue: "ViT model not loaded"
**Solution**: Check ViT model files exist at:
```bash
ls -la /Users/prathamsaurabh/Authenticator.ai/ViT/vit_model_artifacts/
```

### Issue: Document shows placeholder "88"
**Solution**: 
1. Ensure backend is returning `raw_text` in response
2. Check frontend DemoModal.tsx is checking for `analysisResult?.raw_text`
3. Verify PDF/DOCX is being parsed correctly:
   ```bash
   curl -X POST "http://localhost:5000/api/analyze/unified" \
     -F "file=@document.pdf" | jq '.raw_text'
   ```

### Issue: CORS errors
**Solution**: app_unified.py has CORS enabled globally. If issues persist:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## Performance

- **Document Processing**: ~2-3 seconds per document (extraction + classification)
- **Image Processing**: ~1-2 seconds per image
- **Model Loading**: ~3-5 seconds on first request (cached thereafter)
- **Max File Size**: 16MB

## Security

- File uploads limited to 16MB
- Files saved with unique IDs to prevent conflicts
- Uploaded files stored in `backend/uploads/` directory
- Input validation on all endpoints

## Logging

View logs to debug issues:
```bash
# Tail logs (if running in terminal)
tail -f app.log

# Or check console output when running app_unified.py
```

## Next Steps for V1 Launch

- [ ] Test all file types (PDF, DOCX, images)
- [ ] Verify `raw_text` displays correctly in frontend
- [ ] Test with large files (10MB+)
- [ ] Verify BERT model handles all 138 subcategories
- [ ] Test concurrent requests
- [ ] Monitor memory usage
- [ ] Deploy to production

## Support

For issues or questions, check:
1. Health endpoint: `GET /api/health`
2. API documentation: `GET /api/docs`
3. Console logs when running `app_unified.py`

---

**Version**: 1.0  
**Last Updated**: January 15, 2025  
**Status**: Ready for V1 Launch ✅

