# Layer 5: RAG (Retrieval-Augmented Generation)

This layer provides context-aware analysis using RAG architecture.

## Purpose
- Retrieve similar documents from knowledge base
- Enhance classification with historical context
- Provide semantic similarity analysis
- Generate insights from document database

## Components
- RAG service with vector embeddings
- Knowledge base management
- Similarity search using embeddings
- Context retrieval for analysis enhancement

## Integration
- Enhances Layer 2 (Classification) with context
- Supports Layer 3 (Clone Detection) with semantic similarity
- Maintains document knowledge base
- Integrates with all analysis layers

## API Endpoints
- `/api/rag/classify` - RAG-enhanced classification
- `/api/rag/similarity` - Similarity analysis
- `/api/rag/comprehensive` - Full RAG analysis
- `/api/rag/retrieve` - Document retrieval
- `/api/rag/knowledge-base/*` - Knowledge base management
