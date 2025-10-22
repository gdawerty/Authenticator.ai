"""
Comprehensive SQL Database Service for Document Storage
Handles all document-related database operations with proper SQL schema
"""

import sqlite3
import json
import os
import hashlib
import mimetypes
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import uuid
import base64

class DocumentDatabaseService:
    """
    Comprehensive database service for document storage, analysis, and management
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'documents.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize complete database schema for document management"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute('PRAGMA foreign_keys = ON')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    oauth_provider TEXT,
                    oauth_id TEXT,
                    profile_picture TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    settings TEXT DEFAULT '{}'
                )
            ''')
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type TEXT,
                    content_hash TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    simhash TEXT,
                    minhash TEXT,
                    text_content TEXT,
                    metadata TEXT DEFAULT '{}',
                    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    layer_results TEXT NOT NULL,
                    final_score REAL NOT NULL,
                    authenticity_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    flagged_content TEXT DEFAULT '[]',
                    recommendations TEXT DEFAULT '[]',
                    processing_time REAL,
                    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analysis_version TEXT DEFAULT '1.0',
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Layer analysis details
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS layer_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    layer_number INTEGER NOT NULL,
                    layer_name TEXT NOT NULL,
                    layer_score REAL NOT NULL,
                    layer_status TEXT NOT NULL,
                    layer_details TEXT DEFAULT '{}',
                    flagged_issues TEXT DEFAULT '[]',
                    processing_time REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            ''')
            
            # Clone detection matches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clone_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_document_id TEXT NOT NULL,
                    target_document_id TEXT NOT NULL,
                    similarity_score REAL NOT NULL,
                    match_type TEXT NOT NULL,
                    match_algorithm TEXT NOT NULL,
                    match_details TEXT DEFAULT '{}',
                    detected_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_document_id) REFERENCES documents (id),
                    FOREIGN KEY (target_document_id) REFERENCES documents (id)
                )
            ''')
            
            # Document highlights for UI
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_highlights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    analysis_id TEXT NOT NULL,
                    start_offset INTEGER NOT NULL,
                    end_offset INTEGER NOT NULL,
                    highlighted_text TEXT NOT NULL,
                    highlight_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    color TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    layer_source TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    details TEXT DEFAULT '{}',
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            ''')
            
            # User feedback for model improvement
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    accuracy_rating INTEGER CHECK(accuracy_rating >= 1 AND accuracy_rating <= 5),
                    correct_classification TEXT,
                    feedback_details TEXT DEFAULT '{}',
                    feedback_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Document collections/folders
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_collections (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Document collection membership
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collection_documents (
                    collection_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (collection_id, document_id),
                    FOREIGN KEY (collection_id) REFERENCES document_collections (id),
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            # Document sharing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_shares (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    shared_with_id TEXT,
                    share_token TEXT,
                    permissions TEXT DEFAULT 'read',
                    expires_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (owner_id) REFERENCES users (id),
                    FOREIGN KEY (shared_with_id) REFERENCES users (id)
                )
            ''')
            
            # Audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    document_id TEXT,
                    action TEXT NOT NULL,
                    details TEXT DEFAULT '{}',
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            # Create indexes for performance
            self._create_indexes(cursor)
            
            conn.commit()
    
    def _create_indexes(self, cursor):
        """Create database indexes for optimal performance"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            'CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash)',
            'CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash)',
            'CREATE INDEX IF NOT EXISTS idx_documents_upload_time ON documents(upload_timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_analysis_document_id ON analysis_results(document_id)',
            'CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_results(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_analysis_timestamp ON analysis_results(analysis_timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_layer_analysis_id ON layer_analysis(analysis_id)',
            'CREATE INDEX IF NOT EXISTS idx_clone_source ON clone_matches(source_document_id)',
            'CREATE INDEX IF NOT EXISTS idx_clone_target ON clone_matches(target_document_id)',
            'CREATE INDEX IF NOT EXISTS idx_clone_similarity ON clone_matches(similarity_score)',
            'CREATE INDEX IF NOT EXISTS idx_highlights_document ON document_highlights(document_id)',
            'CREATE INDEX IF NOT EXISTS idx_highlights_analysis ON document_highlights(analysis_id)',
            'CREATE INDEX IF NOT EXISTS idx_feedback_analysis ON user_feedback(analysis_id)',
            'CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_trail(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_audit_document ON audit_trail(document_id)',
            'CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_trail(timestamp)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def store_document(self, user_id: str, file_path: str, original_filename: str,
                      text_content: str = None, metadata: Dict[str, Any] = None) -> str:
        """Store a document in the database"""
        document_id = str(uuid.uuid4())
        
        # Calculate file properties
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(original_filename)
        
        # Calculate hashes
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
        
        if text_content:
            content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
        else:
            content_hash = file_hash
        
        # Generate unique filename to avoid conflicts
        filename = f"{document_id}_{original_filename}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents (
                    id, user_id, filename, original_filename, file_path,
                    file_size, mime_type, content_hash, file_hash,
                    text_content, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, user_id, filename, original_filename, file_path,
                file_size, mime_type, content_hash, file_hash,
                text_content, json.dumps(metadata or {})
            ))
            
            # Log the action
            self._log_audit_action(cursor, user_id, document_id, 'document_upload', {
                'filename': original_filename,
                'file_size': file_size,
                'mime_type': mime_type
            })
        
        return document_id
    
    def store_analysis_result(self, document_id: str, user_id: str, analysis_type: str,
                            layer_results: Dict[str, Any], final_score: float,
                            authenticity_score: float, risk_level: str, confidence: float,
                            flagged_content: List[Dict] = None, recommendations: List[str] = None,
                            processing_time: float = None) -> str:
        """Store analysis results for a document"""
        analysis_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results (
                    id, document_id, user_id, analysis_type, layer_results,
                    final_score, authenticity_score, risk_level, confidence,
                    flagged_content, recommendations, processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id, document_id, user_id, analysis_type,
                json.dumps(layer_results), final_score, authenticity_score,
                risk_level, confidence, json.dumps(flagged_content or []),
                json.dumps(recommendations or []), processing_time
            ))
            
            # Store individual layer results
            for layer_num, layer_data in layer_results.items():
                if isinstance(layer_data, dict) and 'score' in layer_data:
                    cursor.execute('''
                        INSERT INTO layer_analysis (
                            analysis_id, layer_number, layer_name, layer_score,
                            layer_status, layer_details, processing_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        analysis_id,
                        int(layer_num.replace('layer', '')) if 'layer' in layer_num else 0,
                        layer_data.get('name', layer_num),
                        layer_data.get('score', 0.0),
                        layer_data.get('status', 'completed'),
                        json.dumps(layer_data.get('details', {})),
                        layer_data.get('processing_time')
                    ))
            
            # Log the action
            self._log_audit_action(cursor, user_id, document_id, 'analysis_completed', {
                'analysis_type': analysis_type,
                'final_score': final_score,
                'risk_level': risk_level
            })
        
        return analysis_id
    
    def store_document_highlights(self, document_id: str, analysis_id: str,
                                highlights: List[Dict[str, Any]]):
        """Store document highlights for UI display"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for highlight in highlights:
                cursor.execute('''
                    INSERT INTO document_highlights (
                        document_id, analysis_id, start_offset, end_offset,
                        highlighted_text, highlight_type, severity, color,
                        explanation, layer_source, confidence, details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    document_id, analysis_id,
                    highlight.get('start', 0), highlight.get('end', 0),
                    highlight.get('text', ''), highlight.get('issue_type', 'unknown'),
                    highlight.get('severity', 'info'), highlight.get('color', '#888888'),
                    highlight.get('explanation', ''), highlight.get('layer_source', 'Unknown'),
                    highlight.get('confidence', 0.0), json.dumps(highlight.get('details', {}))
                ))
    
    def get_document(self, document_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_clause = 'WHERE id = ? AND is_deleted = FALSE'
            params = [document_id]
            
            if user_id:
                where_clause += ' AND user_id = ?'
                params.append(user_id)
            
            cursor.execute(f'''
                SELECT * FROM documents {where_clause}
            ''', params)
            
            row = cursor.fetchone()
            if row:
                doc = dict(row)
                doc['metadata'] = json.loads(doc['metadata'])
                return doc
        
        return None
    
    def get_user_documents(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM documents 
                WHERE user_id = ? AND is_deleted = FALSE
                ORDER BY upload_timestamp DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            documents = []
            for row in cursor.fetchall():
                doc = dict(row)
                doc['metadata'] = json.loads(doc['metadata'])
                documents.append(doc)
            
            return documents
    
    def get_analysis_results(self, document_id: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Get analysis results for a document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_clause = 'WHERE document_id = ?'
            params = [document_id]
            
            if user_id:
                where_clause += ' AND user_id = ?'
                params.append(user_id)
            
            cursor.execute(f'''
                SELECT * FROM analysis_results {where_clause}
                ORDER BY analysis_timestamp DESC
            ''', params)
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['layer_results'] = json.loads(result['layer_results'])
                result['flagged_content'] = json.loads(result['flagged_content'])
                result['recommendations'] = json.loads(result['recommendations'])
                results.append(result)
            
            return results
    
    def get_document_highlights(self, document_id: str, analysis_id: str = None) -> List[Dict[str, Any]]:
        """Get highlights for a document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_clause = 'WHERE document_id = ?'
            params = [document_id]
            
            if analysis_id:
                where_clause += ' AND analysis_id = ?'
                params.append(analysis_id)
            
            cursor.execute(f'''
                SELECT * FROM document_highlights {where_clause}
                ORDER BY start_offset
            ''', params)
            
            highlights = []
            for row in cursor.fetchall():
                highlight = dict(row)
                highlight['details'] = json.loads(highlight['details'])
                highlights.append(highlight)
            
            return highlights
    
    def find_similar_documents(self, content_hash: str, user_id: str = None,
                             threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find similar documents by content hash"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # For exact matches
            where_clause = 'WHERE content_hash = ? AND is_deleted = FALSE'
            params = [content_hash]
            
            if user_id:
                where_clause += ' AND user_id = ?'
                params.append(user_id)
            
            cursor.execute(f'''
                SELECT * FROM documents {where_clause}
                ORDER BY upload_timestamp DESC
            ''', params)
            
            similar_docs = []
            for row in cursor.fetchall():
                doc = dict(row)
                doc['similarity_score'] = 1.0  # Exact match
                doc['match_type'] = 'exact'
                similar_docs.append(doc)
            
            return similar_docs
    
    def store_clone_match(self, source_doc_id: str, target_doc_id: str,
                         similarity_score: float, match_type: str,
                         algorithm: str = 'content_hash', details: Dict = None):
        """Store a clone detection match"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clone_matches (
                    source_document_id, target_document_id, similarity_score,
                    match_type, match_algorithm, match_details
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                source_doc_id, target_doc_id, similarity_score,
                match_type, algorithm, json.dumps(details or {})
            ))
    
    def _log_audit_action(self, cursor, user_id: str, document_id: str = None,
                         action: str = '', details: Dict = None,
                         ip_address: str = None, user_agent: str = None):
        """Log an audit action"""
        cursor.execute('''
            INSERT INTO audit_trail (
                user_id, document_id, action, details, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id, document_id, action,
            json.dumps(details or {}), ip_address, user_agent
        ))
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count tables
            tables = ['users', 'documents', 'analysis_results', 'layer_analysis',
                     'clone_matches', 'document_highlights', 'user_feedback']
            
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Storage info
            cursor.execute('SELECT SUM(file_size) FROM documents WHERE is_deleted = FALSE')
            total_size = cursor.fetchone()[0] or 0
            stats['total_storage_bytes'] = total_size
            stats['total_storage_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats

# Global database service instance
document_db = DocumentDatabaseService()
