-- Authenticator.AI Document Pipeline Schema
-- Created: 2025-12-21

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(10) NOT NULL CHECK (type IN ('pdf', 'docx', 'image')),
    canonical_path TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    company_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document spans table (atomic units)
CREATE TABLE IF NOT EXISTS document_spans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    span_type VARCHAR(20) NOT NULL CHECK (span_type IN ('title', 'paragraph', 'table', 'image', 'heading')),
    text TEXT NOT NULL,
    page INT,
    bbox JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evidence table (for explainability)
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    span_id UUID NOT NULL REFERENCES document_spans(id) ON DELETE CASCADE,
    signal_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    explanation TEXT NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_company_id ON documents(company_id);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_document_spans_document_id ON document_spans(document_id);
CREATE INDEX IF NOT EXISTS idx_document_spans_span_type ON document_spans(span_type);
CREATE INDEX IF NOT EXISTS idx_evidence_span_id ON evidence(span_id);
CREATE INDEX IF NOT EXISTS idx_evidence_signal_type ON evidence(signal_type);
CREATE INDEX IF NOT EXISTS idx_evidence_confidence ON evidence(confidence);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to documents
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
