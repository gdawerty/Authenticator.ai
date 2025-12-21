import os

class Config:
    # Flask configuration
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 8000
    
    # CORS configuration - Allow common development ports
    CORS_RESOURCES = {
        r"/api/*": {
            "origins": [
                "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
                "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
                "http://localhost:8000", "http://localhost:8080", "http://localhost:8081",
                "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
                "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
                "http://127.0.0.1:8000", "http://127.0.0.1:8080", "http://127.0.0.1:8081"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"]
        },
        r"/*": {
            "origins": [
                "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
                "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
                "http://localhost:8000", "http://localhost:8080", "http://localhost:8081",
                "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
                "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
                "http://127.0.0.1:8000", "http://127.0.0.1:8080", "http://127.0.0.1:8081"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"]
        }
    }
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API configuration
    API_TITLE = "Authenticator.ai API"
    API_VERSION = "1.0"
    API_PREFIX = "/api"
    API_DOC = "/docs"
    
    # Groq Cloud Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
