"""
Similarity Indexing Service for Clone Detection
Implements vector-based similarity search with FAISS-like functionality
"""

import json
import sqlite3
import hashlib
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class SimilarityIndexService:
    """
    Service for building and querying similarity indexes for clone detection
    Uses TF-IDF vectorization and cosine similarity for document comparison
    """
    
    def __init__(self, db_path: str = None, index_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'similarity_index.db')
        
        if index_path is None:
            index_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'similarity_vectors')
        
        self.db_path = db_path
        self.index_path = index_path
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(index_path, exist_ok=True)
        
        self._initialize_database()
        self.vectorizer = None
        self.document_vectors = None
        self.document_metadata = []
        
        # Load existing index if available
        self._load_index()
    
    def _initialize_database(self):
        """Initialize similarity index database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Document vectors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_vectors (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    text_content TEXT NOT NULL,
                    vector_index INTEGER,
                    metadata TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vectors_user_id ON document_vectors(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vectors_content_hash ON document_vectors(content_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vectors_index ON document_vectors(vector_index)')
            
            # Similarity matches table for caching
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS similarity_matches (
                    id TEXT PRIMARY KEY,
                    query_doc_id TEXT NOT NULL,
                    match_doc_id TEXT NOT NULL,
                    similarity_score REAL NOT NULL,
                    match_type TEXT DEFAULT 'cosine',
                    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for similarity matches
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_query ON similarity_matches(query_doc_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_target ON similarity_matches(match_doc_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_score ON similarity_matches(similarity_score)')
            
            # Index metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS index_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_document(self, user_id: str, filename: str, text_content: str, 
                    document_id: str = None, metadata: Dict[str, Any] = None) -> str:
        """Add document to similarity index"""
        import uuid
        
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
        
        # Generate content hash
        content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
        
        # Check if document already exists
        existing_doc = self._get_document_by_hash(content_hash, user_id)
        if existing_doc:
            return existing_doc['id']
        
        # Preprocess text for vectorization
        processed_text = self._preprocess_text(text_content)
        
        # Store document in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO document_vectors (
                    id, user_id, filename, content_hash, text_content, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (document_id, user_id, filename, content_hash, processed_text, json.dumps(metadata)))
        
        # Rebuild index to include new document
        self._rebuild_index()
        
        return document_id
    
    def find_similar_documents(self, text_content: str, user_id: str = None, 
                             threshold: float = 0.7, limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar documents using cosine similarity"""
        
        if self.vectorizer is None or self.document_vectors is None:
            return []
        
        # Preprocess query text
        processed_text = self._preprocess_text(text_content)
        
        # Vectorize query text
        query_vector = self.vectorizer.transform([processed_text])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # Get similar documents above threshold
        similar_docs = []
        for i, score in enumerate(similarities):
            if score >= threshold and i < len(self.document_metadata):
                doc_meta = self.document_metadata[i]
                
                # Filter by user if specified
                if user_id and doc_meta.get('user_id') != user_id:
                    continue
                
                similar_docs.append({
                    'document_id': doc_meta['id'],
                    'user_id': doc_meta['user_id'],
                    'filename': doc_meta['filename'],
                    'similarity_score': float(score),
                    'content_hash': doc_meta['content_hash'],
                    'metadata': doc_meta.get('metadata', {}),
                    'created_at': doc_meta.get('created_at')
                })
        
        # Sort by similarity score (descending) and limit results
        similar_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_docs[:limit]
    
    def find_duplicates(self, user_id: str = None, threshold: float = 0.95) -> List[Dict[str, Any]]:
        """Find near-duplicate documents"""
        duplicates = []
        
        if self.document_vectors is None:
            return duplicates
        
        # Calculate pairwise similarities
        similarity_matrix = cosine_similarity(self.document_vectors)
        
        for i in range(len(self.document_metadata)):
            for j in range(i + 1, len(self.document_metadata)):
                similarity = similarity_matrix[i][j]
                
                if similarity >= threshold:
                    doc1 = self.document_metadata[i]
                    doc2 = self.document_metadata[j]
                    
                    # Filter by user if specified
                    if user_id and (doc1.get('user_id') != user_id or doc2.get('user_id') != user_id):
                        continue
                    
                    duplicates.append({
                        'document1': {
                            'id': doc1['id'],
                            'filename': doc1['filename'],
                            'user_id': doc1['user_id']
                        },
                        'document2': {
                            'id': doc2['id'],
                            'filename': doc2['filename'], 
                            'user_id': doc2['user_id']
                        },
                        'similarity_score': float(similarity),
                        'match_type': 'near_duplicate'
                    })
        
        return duplicates
    
    def get_document_neighbors(self, document_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """Get k nearest neighbors for a document"""
        # Get document from database
        doc = self._get_document_by_id(document_id)
        if not doc:
            return []
        
        # Find similar documents
        return self.find_similar_documents(doc['text_content'], limit=k)
    
    def remove_document(self, document_id: str, user_id: str = None) -> bool:
        """Remove document from index"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if document exists and user has permission
            if user_id:
                cursor.execute('''
                    SELECT id FROM document_vectors 
                    WHERE id = ? AND user_id = ?
                ''', (document_id, user_id))
            else:
                cursor.execute('''
                    SELECT id FROM document_vectors 
                    WHERE id = ?
                ''', (document_id,))
            
            if not cursor.fetchone():
                return False
            
            # Delete document
            cursor.execute('DELETE FROM document_vectors WHERE id = ?', (document_id,))
            
            # Delete similarity matches
            cursor.execute('''
                DELETE FROM similarity_matches 
                WHERE query_doc_id = ? OR match_doc_id = ?
            ''', (document_id, document_id))
        
        # Rebuild index
        self._rebuild_index()
        return True
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for vectorization"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _rebuild_index(self):
        """Rebuild the similarity index from database"""
        # Get all documents from database
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM document_vectors 
                ORDER BY created_at
            ''')
            
            documents = cursor.fetchall()
        
        if not documents:
            self.vectorizer = None
            self.document_vectors = None
            self.document_metadata = []
            return
        
        # Extract text content and metadata
        texts = []
        metadata = []
        
        for doc in documents:
            texts.append(doc['text_content'])
            metadata.append({
                'id': doc['id'],
                'user_id': doc['user_id'],
                'filename': doc['filename'],
                'content_hash': doc['content_hash'],
                'metadata': json.loads(doc['metadata']),
                'created_at': doc['created_at']
            })
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            min_df=1,
            max_df=0.95
        )
        
        # Fit and transform documents
        self.document_vectors = self.vectorizer.fit_transform(texts)
        self.document_metadata = metadata
        
        # Update vector indices in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for i, doc_meta in enumerate(metadata):
                cursor.execute('''
                    UPDATE document_vectors 
                    SET vector_index = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (i, doc_meta['id']))
        
        # Save index to disk
        self._save_index()
        
        # Update index metadata
        self._update_index_metadata()
    
    def _save_index(self):
        """Save vectorizer and vectors to disk"""
        try:
            # Save vectorizer
            vectorizer_path = os.path.join(self.index_path, 'vectorizer.pkl')
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            # Save document vectors
            vectors_path = os.path.join(self.index_path, 'document_vectors.pkl')
            with open(vectors_path, 'wb') as f:
                pickle.dump(self.document_vectors, f)
            
            # Save metadata
            metadata_path = os.path.join(self.index_path, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(self.document_metadata, f, indent=2)
                
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def _load_index(self):
        """Load vectorizer and vectors from disk"""
        try:
            vectorizer_path = os.path.join(self.index_path, 'vectorizer.pkl')
            vectors_path = os.path.join(self.index_path, 'document_vectors.pkl')
            metadata_path = os.path.join(self.index_path, 'metadata.json')
            
            if all(os.path.exists(p) for p in [vectorizer_path, vectors_path, metadata_path]):
                # Load vectorizer
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                # Load document vectors
                with open(vectors_path, 'rb') as f:
                    self.document_vectors = pickle.load(f)
                
                # Load metadata
                with open(metadata_path, 'r') as f:
                    self.document_metadata = json.load(f)
                    
        except Exception as e:
            print(f"Error loading index: {e}")
            # Rebuild index if loading fails
            self._rebuild_index()
    
    def _update_index_metadata(self):
        """Update index metadata in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            metadata = {
                'document_count': len(self.document_metadata),
                'last_rebuild': datetime.utcnow().isoformat(),
                'vectorizer_features': self.vectorizer.max_features if self.vectorizer else 0
            }
            
            for key, value in metadata.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO index_metadata (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, str(value)))
    
    def _get_document_by_hash(self, content_hash: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document by content hash and user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM document_vectors 
                WHERE content_hash = ? AND user_id = ?
            ''', (content_hash, user_id))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def _get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM document_vectors 
                WHERE id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get similarity index statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get document count
            cursor.execute('SELECT COUNT(*) FROM document_vectors')
            doc_count = cursor.fetchone()[0]
            
            # Get user count
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM document_vectors')
            user_count = cursor.fetchone()[0]
            
            # Get index metadata
            cursor.execute('SELECT key, value FROM index_metadata')
            metadata = dict(cursor.fetchall())
        
        return {
            'document_count': doc_count,
            'user_count': user_count,
            'index_size': len(self.document_metadata) if self.document_metadata else 0,
            'vectorizer_features': metadata.get('vectorizer_features', 0),
            'last_rebuild': metadata.get('last_rebuild'),
            'index_loaded': self.vectorizer is not None
        }

# Global service instance
similarity_service = SimilarityIndexService()
