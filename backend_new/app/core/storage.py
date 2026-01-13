import os
from pathlib import Path
from uuid import UUID
from app.core.config import settings


class StorageManager:
    """Manages file storage for canonical documents"""

    def __init__(self):
        self.storage_path = Path(settings.STORAGE_PATH)
        self.upload_path = Path(settings.UPLOAD_PATH)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create storage directories if they don't exist"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.upload_path.mkdir(parents=True, exist_ok=True)

    def get_document_path(self, document_id: UUID, extension: str) -> Path:
        """Get the canonical storage path for a document"""
        return self.storage_path / f"{document_id}{extension}"

    def get_upload_path(self, filename: str) -> Path:
        """Get temporary upload path"""
        return self.upload_path / filename

    def save_file(self, source_path: Path, destination_path: Path) -> Path:
        """Move file from source to destination"""
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(destination_path)
        return destination_path

    def delete_file(self, file_path: Path):
        """Delete a file"""
        if file_path.exists():
            file_path.unlink()


storage_manager = StorageManager()
