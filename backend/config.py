import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    # Accept common truthy values
    DEBUG = str(os.getenv("DEBUG", "true")).lower() in {"1", "true", "yes", "on"}

    # File uploads
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(os.path.dirname(__file__), "tmp_uploads")
    )
    ALLOWED_EXTENSIONS = set(
        os.getenv("ALLOWED_EXTENSIONS", "txt,pdf,doc,docx,jpg,jpeg,png,gif").split(",")
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
