import os

class Config:
    # Flask configuration
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 8000
    
    # CORS configuration
    CORS_RESOURCES = {
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"]
        },
        r"/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "http://127.0.0.1:8080"],
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
