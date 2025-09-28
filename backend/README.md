# Authenticator.ai Backend

A Flask-based REST API for document authentication and analysis using AI.

## 🚀 Quick Start

1. Set up a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

The server will start at `http://127.0.0.1:8000`

## 🔑 Key Features

- 📁 File Upload & Storage
- 🔍 Content Type Detection
- 🧠 AI-powered Domain Classification (Place Holder)
- ⚡ Smart Routing Logic
- 🔐 Document Authentication
- 📊 Authenticity Scoring (Place Holder)
- 🌐 Frontend Integration

## 📚 API Documentation

### Main Routes

#### GET /
- Description: Landing page with API information
- Response: HTML page with API overview

#### GET /health
- Description: Health check endpoint
- Response: JSON with service status and features
```json
{
    "status": "healthy",
    "message": "API is running",
    "service": "Authenticator.ai Backend",
    "version": "1.0",
    "features": {
        "upload": "active",
        "content_detection": "active",
        "domain_classification": "active",
        "authenticity_scoring": "active",
        "smart_routing": "active"
    }
}
```

### Authentication Routes

#### POST /login
- Description: User authentication endpoint
- Request Body:
```json
{
    "username": "string",
    "password": "string"
}
```
- Response: JWT token for authenticated requests

### API Routes

#### POST /api/upload
- Description: Upload document for analysis
- Content-Type: multipart/form-data
- Request:
  - File: document file (PDF, DOC, DOCX, etc.)
- Response: Upload status and file information

#### POST /api/analyze
- Description: Analyze uploaded document
- Request Body:
```json
{
    "file_id": "string",
    "analysis_type": "string"
}
```
- Response: Analysis results and authenticity score

#### GET /api/docs
- Description: Swagger UI for API documentation
- Response: Interactive API documentation interface

## 📂 Project Structure

```
backend/
├── app.py              # Main application entry point
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── models/            
│   ├── __init__.py
│   └── user_model.py   # User data model
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py  # Authentication endpoints
│   └── main_routes.py  # Main application endpoints
└── services/
    ├── __init__.py
    ├── data_service.py # Data processing service
    └── user_service.py # User management service
```

## ⚙️ Environment Variables

- `FLASK_ENV`: Development/Production environment
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `UPLOAD_FOLDER`: Path for file uploads

## 🔒 Security Features

- JWT Authentication
- Secure File Storage
- Input Validation
- CORS Protection
- Rate Limiting

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Style
Following PEP 8 guidelines. Use `flake8` for linting:
```bash
flake8 .
```

## 📦 Dependencies

See `requirements.txt` for complete list of dependencies.

Core packages:
- Flask
- Flask-RESTful
- Flask-JWT-Extended
- Flask-CORS
- PyJWT
- Werkzeug
- python-dotenv
- PyYAML
- requests
- pandas
- numpy
- scikit-learn

## 📝 License

MIT License - see LICENSE file for details.
