from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration"""

    # Database
    DATABASE_URL: str = "postgresql://authenticator:SecurePassword123!@postgres:5432/authenticator_db"

    # Storage
    STORAGE_PATH: str = "/workspace/backend_new/storage"
    UPLOAD_PATH: str = "/workspace/backend_new/uploads"

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
    GROQ_MODEL: str = "mixtral-8x7b-32768"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
