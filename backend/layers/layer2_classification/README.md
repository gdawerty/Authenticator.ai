# Layer 2: Document Classification

This layer classifies documents into categories using ML models.

## Purpose
- Classify documents by type (invoice, contract, ID, etc.)
- ML-based classification models
- RAG-enhanced classification for improved accuracy
- Confidence scoring

## Components
- Classification service
- ML models for document categorization
- Feature extraction utilities
- RAG integration for context-aware classification

## Integration
- Receives file type info from Layer 1
- Works with Layer 5 (RAG) for enhanced classification
- Outputs to subsequent analysis layers
