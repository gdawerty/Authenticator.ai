#!/usr/bin/env python3
"""Initialize the database with required tables"""

from app.db.session import engine, Base
from app.models.db_models import DocumentModel, DocumentSpanModel, EvidenceModel, UserModel

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
