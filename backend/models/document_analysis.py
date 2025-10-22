"""
Database models for document analysis and storage
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib
import os

class DocumentAnalysisDB:
    """
    Database manager for document analysis results and clone detection storage
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'document_analysis.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Documents table for clone detection storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    simhash TEXT,
                    minhash TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analysis_id TEXT
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_user_email ON documents(user_email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash)')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    document_id TEXT,
                    filename TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    layer_results TEXT, -- JSON
                    final_score REAL,
                    threat_level TEXT,
                    confidence REAL,
                    flagged_content TEXT, -- JSON array of specific issues
                    recommendations TEXT, -- JSON array
                    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processing_time REAL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                )
            ''')
            
            # Clone matches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clone_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_document_id TEXT NOT NULL,
                    target_document_id TEXT NOT NULL,
                    similarity_score REAL NOT NULL,
                    match_type TEXT NOT NULL, -- 'exact', 'near_duplicate', 'similar'
                    match_details TEXT, -- JSON with specific match information
                    detected_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(source_document_id) REFERENCES documents(id),
                    FOREIGN KEY(target_document_id) REFERENCES documents(id)
                )
            ''')
            
            # User feedback table for model improvement
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    user_email TEXT NOT NULL,
                    feedback_type TEXT NOT NULL, -- 'correct', 'incorrect', 'partially_correct'
                    actual_result TEXT, -- What the user says is correct
                    feedback_details TEXT, -- JSON with specific feedback
                    feedback_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(analysis_id) REFERENCES analysis_results(id)
                )
            ''')
            
            conn.commit()
    
    def store_document_for_clone_detection(self, user_email: str, filename: str, 
                                         file_path: str, content_hash: str, 
                                         simhash: str = None, minhash: str = None,
                                         analysis_id: str = None) -> str:
        """Store document in database for clone detection"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Generate document ID
            doc_id = hashlib.md5(f"{user_email}_{filename}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Get file info
            file_size = os.path.getsize(file_path)
            import mimetypes
            mime_type, _ = mimetypes.guess_type(filename)
            
            # Insert document
            cursor.execute('''
                INSERT INTO documents 
                (id, user_email, filename, file_hash, content_hash, simhash, minhash, 
                 file_size, mime_type, analysis_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (doc_id, user_email, filename, file_hash, content_hash, 
                  simhash, minhash, file_size, mime_type, analysis_id))
            
            conn.commit()
            return doc_id
    
    def find_similar_documents(self, user_email: str, content_hash: str, 
                             simhash: str = None, similarity_threshold: float = 0.8) -> List[Dict]:
        """Find similar documents for clone detection"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            similar_docs = []
            
            # Exact content hash match
            cursor.execute('''
                SELECT id, filename, file_hash, upload_timestamp, analysis_id
                FROM documents 
                WHERE user_email = ? AND content_hash = ?
                ORDER BY upload_timestamp DESC
            ''', (user_email, content_hash))
            
            exact_matches = cursor.fetchall()
            for match in exact_matches:
                similar_docs.append({
                    'document_id': match[0],
                    'filename': match[1],
                    'file_hash': match[2],
                    'upload_timestamp': match[3],
                    'analysis_id': match[4],
                    'match_type': 'exact',
                    'similarity_score': 1.0
                })
            
            # SimHash similarity (if available)
            if simhash:
                cursor.execute('''
                    SELECT id, filename, simhash, upload_timestamp, analysis_id
                    FROM documents 
                    WHERE user_email = ? AND simhash IS NOT NULL AND id NOT IN (
                        SELECT id FROM documents WHERE content_hash = ?
                    )
                ''', (user_email, content_hash))
                
                simhash_docs = cursor.fetchall()
                for doc in simhash_docs:
                    # Calculate SimHash similarity (simplified)
                    similarity = self._calculate_simhash_similarity(simhash, doc[2])
                    if similarity >= similarity_threshold:
                        similar_docs.append({
                            'document_id': doc[0],
                            'filename': doc[1],
                            'upload_timestamp': doc[3],
                            'analysis_id': doc[4],
                            'match_type': 'similar',
                            'similarity_score': similarity
                        })
            
            return similar_docs
    
    def store_clone_matches(self, source_doc_id: str, matches: List[Dict]):
        """Store clone detection matches"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for match in matches:
                cursor.execute('''
                    INSERT INTO clone_matches 
                    (source_document_id, target_document_id, similarity_score, 
                     match_type, match_details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (source_doc_id, match['document_id'], match['similarity_score'],
                      match['match_type'], json.dumps(match)))
            
            conn.commit()
    
    def store_analysis_result(self, analysis_id: str, user_email: str, 
                            filename: str, layer_results: Dict, 
                            final_score: float, threat_level: str, 
                            confidence: float, flagged_content: List[Dict],
                            recommendations: List[str], processing_time: float,
                            document_id: str = None) -> str:
        """Store complete analysis result"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results 
                (id, user_email, document_id, filename, analysis_type, layer_results,
                 final_score, threat_level, confidence, flagged_content, 
                 recommendations, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (analysis_id, user_email, document_id, filename, '7-layer-analysis',
                  json.dumps(layer_results), final_score, threat_level, confidence,
                  json.dumps(flagged_content), json.dumps(recommendations), processing_time))
            
            conn.commit()
            return analysis_id
    
    def get_user_documents(self, user_email: str) -> List[Dict]:
        """Get all documents for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT d.id, d.filename, d.file_size, d.mime_type, d.upload_timestamp,
                       ar.final_score, ar.threat_level, ar.confidence
                FROM documents d
                LEFT JOIN analysis_results ar ON d.analysis_id = ar.id
                WHERE d.user_email = ?
                ORDER BY d.upload_timestamp DESC
            ''', (user_email,))
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row[0],
                    'filename': row[1],
                    'file_size': row[2],
                    'mime_type': row[3],
                    'upload_timestamp': row[4],
                    'final_score': row[5],
                    'threat_level': row[6],
                    'confidence': row[7]
                })
            
            return documents
    
    def get_analysis_details(self, analysis_id: str, user_email: str) -> Optional[Dict]:
        """Get detailed analysis results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM analysis_results 
                WHERE id = ? AND user_email = ?
            ''', (analysis_id, user_email))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'user_email': result[1],
                    'document_id': result[2],
                    'filename': result[3],
                    'analysis_type': result[4],
                    'layer_results': json.loads(result[5]),
                    'final_score': result[6],
                    'threat_level': result[7],
                    'confidence': result[8],
                    'flagged_content': json.loads(result[9]),
                    'recommendations': json.loads(result[10]),
                    'analysis_timestamp': result[11],
                    'processing_time': result[12]
                }
            
            return None
    
    def _calculate_simhash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate SimHash similarity (simplified implementation)"""
        try:
            # Convert hex strings to integers
            int1 = int(hash1, 16)
            int2 = int(hash2, 16)
            
            # XOR and count different bits
            xor = int1 ^ int2
            diff_bits = bin(xor).count('1')
            
            # Calculate similarity (64-bit SimHash)
            similarity = 1.0 - (diff_bits / 64.0)
            return max(0.0, similarity)
        except:
            return 0.0

    def get_user_documents(self, user_email: str):
        """Get all documents for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id as file_id, 
                    filename, 
                    file_size, 
                    upload_timestamp,
                    content_hash,
                    mime_type
                FROM documents 
                WHERE user_email = ? 
                ORDER BY upload_timestamp DESC
            """, (user_email,))
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'file_id': row['file_id'],
                    'filename': row['filename'],
                    'file_size': row['file_size'],
                    'upload_timestamp': row['upload_timestamp'],
                    'content_hash': row['content_hash'],
                    'mime_type': row['mime_type']
                })
            
            conn.close()
            return documents
            
        except Exception as e:
            print(f"Error retrieving user documents: {e}")
            return []
