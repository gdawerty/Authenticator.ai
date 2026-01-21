from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Get the backend_new directory (parent of app directory)
BACKEND_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application configuration"""

    # Database
    DATABASE_URL: str = "postgresql://authenticator:SecurePassword123!@postgres:5432/authenticator_db"

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
