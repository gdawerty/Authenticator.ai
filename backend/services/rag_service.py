"""
RAG (Retrieval-Augmented Generation) Service for Enhanced Classification
Integrates with existing BERT, ViT, and clone detection models
"""

import os
import json
import sqlite3
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
import hashlib
from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer
import faiss
from dataclasses import dataclass

@dataclass
class RAGResult:
    """RAG retrieval result"""
    query_embedding: np.ndarray
    retrieved_documents: List[Dict[str, Any]]
    similarity_scores: List[float]
    context_text: str
    metadata: Dict[str, Any]

class RAGService:
    """
    RAG Service for Enhanced Document Classification and Authenticity Verification
    
    Features:
    - Multi-modal retrieval (text + image embeddings)
    - Contextual classification enhancement
    - Knowledge base integration
    - Similarity-based document retrieval
    - Cross-verification with historical data
    """
    
    def __init__(self, db_path: str = "data/rag_knowledge_base.db"):
        self.db_path = db_path
        self.embedding_model = None
        self.vector_index = None
        self.document_store = {}
        
        # Initialize RAG components
        self._init_embedding_model()
        self._init_database()
        self._init_vector_index()
        
        print("🧠 RAG Service initialized")
        print("   📊 Multi-modal retrieval enabled")
        print("   🔍 Contextual classification support")
        print("   📚 Knowledge base integration ready")
    
    def _init_embedding_model(self):
        """Initialize embedding model for RAG"""
        try:
            # Use sentence-transformers for text embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model loaded: all-MiniLM-L6-v2")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _init_database(self):
        """Initialize RAG knowledge base database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Document knowledge base
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rag_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                document_type TEXT NOT NULL,
                content_text TEXT,
                content_embedding BLOB,
                metadata TEXT,
                classification_result TEXT,
                authenticity_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Image knowledge base
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rag_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                image_type TEXT NOT NULL,
                visual_embedding BLOB,
                classification_result TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Classification examples and patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                example_text TEXT,
                example_embedding BLOB,
                confidence_score REAL,
                source_document_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Similarity cache for performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS similarity_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT NOT NULL,
                document_id TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                retrieval_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(query_hash, document_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rag_docs_type ON rag_documents(document_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rag_docs_authenticity ON rag_documents(authenticity_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_classification_category ON classification_examples(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_similarity_query ON similarity_cache(query_hash)')
        
        conn.commit()
        conn.close()
    
    def _init_vector_index(self):
        """Initialize FAISS vector index for fast similarity search"""
        try:
            # Initialize FAISS index
            embedding_dim = 384  # all-MiniLM-L6-v2 dimension
            self.vector_index = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity
            
            # Load existing embeddings if available
            self._load_existing_embeddings()
            
            print("✅ FAISS vector index initialized")
        except ImportError:
            print("⚠️ FAISS not available, using fallback similarity search")
            self.vector_index = None
    
    def _load_existing_embeddings(self):
        """Load existing embeddings into vector index"""
        if not self.vector_index:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load document embeddings
            cursor.execute('SELECT document_id, content_embedding FROM rag_documents WHERE content_embedding IS NOT NULL')
            rows = cursor.fetchall()
            
            embeddings = []
            document_ids = []
            
            for row in rows:
                doc_id, embedding_blob = row
                if embedding_blob:
                    embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    embeddings.append(embedding)
                    document_ids.append(doc_id)
            
            if embeddings:
                embeddings_array = np.vstack(embeddings)
                self.vector_index.add(embeddings_array)
                self.document_store = {doc_id: i for i, doc_id in enumerate(document_ids)}
                print(f"✅ Loaded {len(embeddings)} existing embeddings into vector index")
            
            conn.close()
        except Exception as e:
            print(f"❌ Failed to load existing embeddings: {e}")
    
    def add_document_to_knowledge_base(
        self, 
        document_id: str, 
        filename: str, 
        content_text: str, 
        document_type: str,
        classification_result: Dict[str, Any] = None,
        authenticity_score: float = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Add document to RAG knowledge base
        
        Args:
            document_id: Unique document identifier
            filename: Original filename
            content_text: Extracted text content
            document_type: Classified document type
            classification_result: BERT/ViT classification results
            authenticity_score: Document authenticity score
            metadata: Additional metadata
        
        Returns:
            bool: Success status
        """
        try:
            if not self.embedding_model:
                print("❌ Embedding model not available")
                return False
            
            # Generate embedding
            embedding = self.embedding_model.encode(content_text)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO rag_documents 
                (document_id, filename, document_type, content_text, content_embedding, 
                 classification_result, authenticity_score, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id,
                filename,
                document_type,
                content_text,
                embedding.tobytes(),
                json.dumps(classification_result) if classification_result else None,
                authenticity_score,
                json.dumps(metadata) if metadata else None,
                datetime.now().isoformat()
            ))
            
            # Add to vector index
            if self.vector_index:
                self.vector_index.add(embedding.reshape(1, -1))
                self.document_store[document_id] = self.vector_index.ntotal - 1
            
            # Extract classification examples
            if classification_result:
                self._extract_classification_examples(document_id, content_text, classification_result)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added document {filename} to RAG knowledge base")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add document to knowledge base: {e}")
            return False
    
    def retrieve_similar_documents(
        self, 
        query_text: str, 
        document_type: str = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> RAGResult:
        """
        Retrieve similar documents using RAG
        
        Args:
            query_text: Text to find similar documents for
            document_type: Filter by document type (optional)
            top_k: Number of similar documents to retrieve
            similarity_threshold: Minimum similarity score
        
        Returns:
            RAGResult: Retrieved documents and context
        """
        try:
            if not self.embedding_model:
                return RAGResult(
                    query_embedding=np.array([]),
                    retrieved_documents=[],
                    similarity_scores=[],
                    context_text="",
                    metadata={"error": "Embedding model not available"}
                )
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text)
            
            # Search for similar documents
            if self.vector_index and self.vector_index.ntotal > 0:
                # Use FAISS for fast similarity search
                similarities, indices = self.vector_index.search(
                    query_embedding.reshape(1, -1), 
                    min(top_k, self.vector_index.ntotal)
                )
                
                retrieved_docs = []
                similarity_scores = []
                
                for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                    if similarity >= similarity_threshold:
                        # Get document details
                        doc_id = list(self.document_store.keys())[list(self.document_store.values()).index(idx)]
                        doc_details = self._get_document_details(doc_id)
                        
                        if doc_details:
                            # Apply document type filter if specified
                            if not document_type or doc_details.get('document_type') == document_type:
                                retrieved_docs.append(doc_details)
                                similarity_scores.append(float(similarity))
            else:
                # Fallback to database similarity search
                retrieved_docs, similarity_scores = self._fallback_similarity_search(
                    query_embedding, document_type, top_k, similarity_threshold
                )
            
            # Generate context text
            context_text = self._generate_context_text(retrieved_docs)
            
            return RAGResult(
                query_embedding=query_embedding,
                retrieved_documents=retrieved_docs,
                similarity_scores=similarity_scores,
                context_text=context_text,
                metadata={
                    "retrieval_method": "faiss" if self.vector_index else "database",
                    "total_documents_searched": self.vector_index.ntotal if self.vector_index else 0,
                    "filter_applied": document_type is not None
                }
            )
            
        except Exception as e:
            print(f"❌ Document retrieval failed: {e}")
            return RAGResult(
                query_embedding=np.array([]),
                retrieved_documents=[],
                similarity_scores=[],
                context_text="",
                metadata={"error": str(e)}
            )
    
    def enhance_classification_with_rag(
        self, 
        text_content: str, 
        current_classification: Dict[str, Any],
        document_type: str = None
    ) -> Dict[str, Any]:
        """
        Enhance classification results using RAG-retrieved context
        
        Args:
            text_content: Document text content
            current_classification: Current BERT/ViT classification result
            document_type: Document type hint
        
        Returns:
            Enhanced classification with RAG context
        """
        try:
            # Retrieve similar documents
            rag_result = self.retrieve_similar_documents(
                text_content, 
                document_type=document_type,
                top_k=3,
                similarity_threshold=0.6
            )
            
            # Analyze retrieved documents for classification patterns
            classification_patterns = self._analyze_classification_patterns(rag_result.retrieved_documents)
            
            # Enhance current classification with RAG insights
            enhanced_classification = current_classification.copy()
            enhanced_classification['rag_enhancement'] = {
                'similar_documents_found': len(rag_result.retrieved_documents),
                'average_similarity': np.mean(rag_result.similarity_scores) if rag_result.similarity_scores else 0.0,
                'classification_patterns': classification_patterns,
                'context_confidence_boost': self._calculate_confidence_boost(rag_result),
                'retrieval_metadata': rag_result.metadata
            }
            
            # Adjust confidence based on similar documents
            if rag_result.retrieved_documents:
                similar_types = [doc.get('document_type') for doc in rag_result.retrieved_documents]
                if current_classification.get('predicted_category') in similar_types:
                    # Boost confidence if similar documents have same classification
                    enhanced_classification['confidence'] = min(1.0, 
                        current_classification.get('confidence', 0.0) + 0.1
                    )
                    enhanced_classification['rag_enhancement']['confidence_boost'] = 0.1
            
            return enhanced_classification
            
        except Exception as e:
            print(f"❌ RAG classification enhancement failed: {e}")
            return current_classification
    
    def verify_authenticity_with_rag(
        self, 
        document_id: str, 
        authenticity_score: float,
        document_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify document authenticity using RAG knowledge base
        
        Args:
            document_id: Document identifier
            authenticity_score: Current authenticity score
            document_type: Document type
            metadata: Document metadata
        
        Returns:
            RAG-enhanced authenticity verification
        """
        try:
            # Retrieve similar authentic documents
            similar_docs = self.retrieve_similar_documents(
                metadata.get('content_text', ''),
                document_type=document_type,
                top_k=5,
                similarity_threshold=0.5
            )
            
            # Analyze authenticity patterns
            authenticity_patterns = self._analyze_authenticity_patterns(similar_docs.retrieved_documents)
            
            # Cross-verify with historical data
            verification_result = {
                'original_score': authenticity_score,
                'rag_verification': {
                    'similar_authentic_documents': len(similar_docs.retrieved_documents),
                    'average_authenticity_of_similar': np.mean([
                        doc.get('authenticity_score', 0) for doc in similar_docs.retrieved_documents
                    ]) if similar_docs.retrieved_documents else 0.0,
                    'authenticity_patterns': authenticity_patterns,
                    'verification_confidence': self._calculate_verification_confidence(similar_docs)
                },
                'recommendations': self._generate_authenticity_recommendations(authenticity_patterns)
            }
            
            return verification_result
            
        except Exception as e:
            print(f"❌ RAG authenticity verification failed: {e}")
            return {'error': str(e), 'original_score': authenticity_score}
    
    def _get_document_details(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document details from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT document_id, filename, document_type, content_text, 
                       classification_result, authenticity_score, metadata
                FROM rag_documents 
                WHERE document_id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'document_id': row[0],
                    'filename': row[1],
                    'document_type': row[2],
                    'content_text': row[3],
                    'classification_result': json.loads(row[4]) if row[4] else None,
                    'authenticity_score': row[5],
                    'metadata': json.loads(row[6]) if row[6] else None
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get document details: {e}")
            return None
    
    def _fallback_similarity_search(
        self, 
        query_embedding: np.ndarray, 
        document_type: str = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """Fallback similarity search using database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all documents with embeddings
            query = '''
                SELECT document_id, content_embedding, filename, document_type, 
                       classification_result, authenticity_score, metadata
                FROM rag_documents 
                WHERE content_embedding IS NOT NULL
            '''
            params = []
            
            if document_type:
                query += ' AND document_type = ?'
                params.append(document_type)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            similarities = []
            documents = []
            
            for row in rows:
                doc_id, embedding_blob, filename, doc_type, classification, auth_score, metadata = row
                
                if embedding_blob:
                    stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, stored_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                    )
                    
                    if similarity >= similarity_threshold:
                        similarities.append(similarity)
                        documents.append({
                            'document_id': doc_id,
                            'filename': filename,
                            'document_type': doc_type,
                            'classification_result': json.loads(classification) if classification else None,
                            'authenticity_score': auth_score,
                            'metadata': json.loads(metadata) if metadata else None
                        })
            
            # Sort by similarity and return top_k
            sorted_indices = np.argsort(similarities)[::-1][:top_k]
            
            return (
                [documents[i] for i in sorted_indices],
                [similarities[i] for i in sorted_indices]
            )
            
        except Exception as e:
            print(f"❌ Fallback similarity search failed: {e}")
            return [], []
        finally:
            conn.close()
    
    def _generate_context_text(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Generate context text from retrieved documents"""
        if not retrieved_docs:
            return ""
        
        context_parts = []
        for doc in retrieved_docs[:3]:  # Use top 3 documents
            doc_type = doc.get('document_type', 'unknown')
            auth_score = doc.get('authenticity_score', 0)
            context_parts.append(f"Similar {doc_type} document (authenticity: {auth_score:.2f})")
        
        return " | ".join(context_parts)
    
    def _analyze_classification_patterns(self, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze classification patterns from retrieved documents"""
        if not retrieved_docs:
            return {}
        
        patterns = {
            'common_types': {},
            'confidence_distribution': [],
            'authenticity_scores': []
        }
        
        for doc in retrieved_docs:
            doc_type = doc.get('document_type', 'unknown')
            patterns['common_types'][doc_type] = patterns['common_types'].get(doc_type, 0) + 1
            
            classification = doc.get('classification_result', {})
            if classification:
                patterns['confidence_distribution'].append(classification.get('confidence', 0))
            
            auth_score = doc.get('authenticity_score')
            if auth_score is not None:
                patterns['authenticity_scores'].append(auth_score)
        
        return patterns
    
    def _analyze_authenticity_patterns(self, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze authenticity patterns from retrieved documents"""
        if not retrieved_docs:
            return {}
        
        auth_scores = [doc.get('authenticity_score', 0) for doc in retrieved_docs if doc.get('authenticity_score') is not None]
        
        return {
            'average_authenticity': np.mean(auth_scores) if auth_scores else 0,
            'authenticity_range': (min(auth_scores), max(auth_scores)) if auth_scores else (0, 0),
            'high_authenticity_count': len([s for s in auth_scores if s > 80]),
            'low_authenticity_count': len([s for s in auth_scores if s < 50])
        }
    
    def _calculate_confidence_boost(self, rag_result: RAGResult) -> float:
        """Calculate confidence boost based on RAG results"""
        if not rag_result.retrieved_documents:
            return 0.0
        
        # Boost confidence based on similarity and number of similar documents
        avg_similarity = np.mean(rag_result.similarity_scores) if rag_result.similarity_scores else 0
        doc_count = len(rag_result.retrieved_documents)
        
        # Higher similarity and more documents = higher confidence boost
        boost = min(0.2, (avg_similarity * doc_count) / 10)
        return boost
    
    def _calculate_verification_confidence(self, rag_result: RAGResult) -> float:
        """Calculate verification confidence based on RAG results"""
        if not rag_result.retrieved_documents:
            return 0.0
        
        # Base confidence on similarity and document quality
        avg_similarity = np.mean(rag_result.similarity_scores) if rag_result.similarity_scores else 0
        doc_count = len(rag_result.retrieved_documents)
        
        # More similar documents with higher similarity = higher confidence
        confidence = min(1.0, (avg_similarity * doc_count) / 5)
        return confidence
    
    def _generate_authenticity_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate authenticity recommendations based on patterns"""
        recommendations = []
        
        avg_auth = patterns.get('average_authenticity', 0)
        high_auth_count = patterns.get('high_authenticity_count', 0)
        low_auth_count = patterns.get('low_authenticity_count', 0)
        
        if avg_auth > 80:
            recommendations.append("Document authenticity aligns with similar high-quality documents")
        elif avg_auth < 50:
            recommendations.append("Document shows lower authenticity compared to similar documents - requires review")
        
        if high_auth_count > low_auth_count:
            recommendations.append("Similar documents show high authenticity patterns")
        elif low_auth_count > high_auth_count:
            recommendations.append("Similar documents show authenticity concerns - investigate further")
        
        return recommendations
    
    def _extract_classification_examples(
        self, 
        document_id: str, 
        content_text: str, 
        classification_result: Dict[str, Any]
    ):
        """Extract classification examples for future RAG enhancement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            category = classification_result.get('predicted_category', 'unknown')
            subcategory = classification_result.get('predicted_subcategory', '')
            confidence = classification_result.get('confidence', 0.0)
            
            # Generate embedding for the example
            if self.embedding_model:
                example_embedding = self.embedding_model.encode(content_text[:500])  # Use first 500 chars
                
                cursor.execute('''
                    INSERT INTO classification_examples 
                    (category, subcategory, example_text, example_embedding, confidence_score, source_document_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    category,
                    subcategory,
                    content_text[:500],
                    example_embedding.tobytes(),
                    confidence,
                    document_id
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Failed to extract classification examples: {e}")
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Document statistics
            cursor.execute('SELECT COUNT(*) FROM rag_documents')
            total_documents = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT document_type) FROM rag_documents')
            document_types = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(authenticity_score) FROM rag_documents WHERE authenticity_score IS NOT NULL')
            avg_authenticity = cursor.fetchone()[0] or 0
            
            # Classification examples
            cursor.execute('SELECT COUNT(*) FROM classification_examples')
            total_examples = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_documents': total_documents,
                'document_types': document_types,
                'average_authenticity': round(avg_authenticity, 2),
                'classification_examples': total_examples,
                'vector_index_size': self.vector_index.ntotal if self.vector_index else 0,
                'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else 'Not loaded'
            }
            
        except Exception as e:
            return {'error': str(e)}


# Global RAG service instance
rag_service = RAGService()
