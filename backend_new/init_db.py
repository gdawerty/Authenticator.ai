"""Initialize database tables"""
from app.db.session import engine, Base
from app.models.db_models import (
    DocumentModel, DocumentSpanModel, UserModel, AuditModel,
    ContractModel, ContractFolderModel
)
from sqlalchemy import text

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # SQLite migrations: add new columns to existing tables if not present
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE documents ADD COLUMN contract_id CHAR(36)",
            "ALTER TABLE documents ADD COLUMN folder_id CHAR(36)",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # Column already exists

    print("✓ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
