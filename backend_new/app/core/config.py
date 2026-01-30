from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Get the backend_new directory (parent of app directory)
BACKEND_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application configuration"""

    # Database
    DATABASE_URL: str = "sqlite:///./authenticator.db"
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Storage - use relative paths from backend_new directory
    STORAGE_PATH: str = str(BACKEND_ROOT / "storage")
    UPLOAD_PATH: str = str(BACKEND_ROOT / "uploads")

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Authenticator.AI Pipeline"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:3000"]

    # File Processing
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}

    # Groq API
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_URI: str = "http://localhost:5175/auth/callback"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
