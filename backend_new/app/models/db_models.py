from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, Text, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base


# SQLite-compatible UUID type
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


class DocumentModel(Base):
    """Database model for documents table"""
    __tablename__ = "documents"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    type = Column(String(10), nullable=False)
    canonical_path = Column(Text, nullable=False)
    original_filename = Column(Text, nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID, nullable=True)
    doc_metadata = Column('metadata', JSON, default={})
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    contract_id = Column(UUID, ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True, index=True)
    folder_id = Column(UUID, ForeignKey("contract_folders.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("UserModel", back_populates="documents")
    spans = relationship("DocumentSpanModel", back_populates="document", cascade="all, delete-orphan")
    contract = relationship("ContractModel", foreign_keys=[contract_id])
    folder = relationship("ContractFolderModel", foreign_keys=[folder_id])


class DocumentSpanModel(Base):
    """Database model for document_spans table"""
    __tablename__ = "document_spans"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    span_type = Column(String(20), nullable=False)
    text = Column(Text, nullable=False)
    page = Column(Integer, nullable=True)
    bbox = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    document = relationship("DocumentModel", back_populates="spans")
    evidence = relationship("EvidenceModel", back_populates="span", cascade="all, delete-orphan")


class EvidenceModel(Base):
    """Database model for evidence table"""
    __tablename__ = "evidence"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    span_id = Column(UUID, ForeignKey("document_spans.id", ondelete="CASCADE"), nullable=False)
    signal_type = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    span = relationship("DocumentSpanModel", back_populates="evidence")


class UserModel(Base):
    """Database model for users table"""
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    oauth_provider = Column(String(50), nullable=True)  # e.g., 'google', 'github', 'microsoft'
    profile_picture = Column(Text, nullable=True)  # URL to profile picture
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    documents = relationship("DocumentModel", back_populates="user", cascade="all, delete-orphan")
    audits = relationship("AuditModel", back_populates="user", cascade="all, delete-orphan")
    contracts = relationship("ContractModel", back_populates="user", cascade="all, delete-orphan")


class AuditModel(Base):
    """Database model for audits table"""
    __tablename__ = "audits"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    document_id = Column(UUID, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="clean")  # clean, warning, flagged
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="audits")
    document = relationship("DocumentModel", foreign_keys=[document_id])


class ContractModel(Base):
    """A contract project - top-level folder"""
    __tablename__ = "contracts"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, in_progress, complete
    pinned = Column(Integer, nullable=False, default=0)
    shared = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("UserModel", back_populates="contracts")
    folders = relationship("ContractFolderModel", back_populates="contract", cascade="all, delete-orphan")


class ContractFolderModel(Base):
    """A folder inside a contract (can be nested)"""
    __tablename__ = "contract_folders"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(UUID, ForeignKey("contract_folders.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    contract = relationship("ContractModel", back_populates="folders")
    children = relationship("ContractFolderModel", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("ContractFolderModel", back_populates="children", remote_side=[id])
