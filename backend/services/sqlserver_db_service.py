"""
SQL Server Database Service for Authenticator.AI
Handles connections to auth_db, docs_db, and clones_db
"""
import pyodbc
import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
import uuid

class SQLServerDatabaseService:
    def __init__(self):
        self.server = os.getenv('DB_SERVER', 'localhost')
        self.username = os.getenv('DB_USER', 'sa')
        self.password = os.getenv('DB_PASS', '')
        
        # Use a simpler connection approach
        self.connection_params = {
            'server': self.server,
            'user': self.username,
            'password': self.password,
            'driver': '{ODBC Driver 17 for SQL Server}',  # More common driver
            'TrustServerCertificate': 'yes'
        }
        
        # Initialize database schemas
        self._initialize_schemas()
    
    def _get_connection(self, database: str):
        """Get connection to specified database"""
        conn_str = f'DRIVER={self.connection_params["driver"]};SERVER={self.connection_params["server"]};DATABASE={database};UID={self.connection_params["user"]};PWD={self.connection_params["password"]};TrustServerCertificate={self.connection_params["TrustServerCertificate"]}'
        return pyodbc.connect(conn_str)
    
    def _initialize_schemas(self):
        """Initialize database schemas for all three databases"""
        try:
            # Initialize auth_db schema
            self._init_auth_db_schema()
            
            # Initialize docs_db schema  
            self._init_docs_db_schema()
            
            # Initialize clones_db schema
            self._init_clones_db_schema()
            
        except Exception as e:
            print(f"❌ Error initializing database schemas: {e}")
    
    def _init_auth_db_schema(self):
        """Initialize auth_db tables"""
        with self._get_connection('auth_db') as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                CREATE TABLE users (
                    id NVARCHAR(50) PRIMARY KEY,
                    username NVARCHAR(100) UNIQUE NOT NULL,
                    email NVARCHAR(255) UNIQUE NOT NULL,
                    password_hash NVARCHAR(255) NOT NULL,
                    first_name NVARCHAR(100),
                    last_name NVARCHAR(100),
                    oauth_provider NVARCHAR(50),
                    oauth_id NVARCHAR(100),
                    profile_picture NVARCHAR(500),
                    is_active BIT DEFAULT 1,
                    is_verified BIT DEFAULT 0,
                    created_at DATETIME DEFAULT GETDATE(),
                    last_login DATETIME,
                    settings NVARCHAR(MAX) DEFAULT '{}'
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_sessions' AND xtype='U')
                CREATE TABLE user_sessions (
                    id NVARCHAR(50) PRIMARY KEY,
                    user_id NVARCHAR(50) NOT NULL,
                    token_hash NVARCHAR(255) NOT NULL,
                    ip_address NVARCHAR(45),
                    user_agent NVARCHAR(500),
                    created_at DATETIME DEFAULT GETDATE(),
                    expires_at DATETIME NOT NULL,
                    is_active BIT DEFAULT 1,
                    last_activity DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create indexes
            try:
                cursor.execute('CREATE INDEX idx_users_email ON users(email)')
            except:
                pass  # Index might already exist
            try:
                cursor.execute('CREATE INDEX idx_users_oauth ON users(oauth_provider, oauth_id)')
            except:
                pass  # Index might already exist
            
            conn.commit()
    
    def _init_docs_db_schema(self):
        """Initialize docs_db tables"""
        with self._get_connection('docs_db') as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='documents' AND xtype='U')
                CREATE TABLE documents (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    user_id NVARCHAR(50) NOT NULL,
                    filename NVARCHAR(255) NOT NULL,
                    original_filename NVARCHAR(255) NOT NULL,
                    file_size BIGINT NOT NULL,
                    file_type NVARCHAR(100) NOT NULL,
                    file_hash NVARCHAR(128),
                    upload_path NVARCHAR(500),
                    content_text NVARCHAR(MAX),
                    upload_date DATETIME DEFAULT GETDATE(),
                    last_modified DATETIME DEFAULT GETDATE(),
                    metadata NVARCHAR(MAX) DEFAULT '{}'
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='analysis_results' AND xtype='U')
                CREATE TABLE analysis_results (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    document_id INT NOT NULL,
                    analysis_type NVARCHAR(100) NOT NULL,
                    result_data NVARCHAR(MAX) NOT NULL,
                    confidence_score FLOAT,
                    processing_time FLOAT,
                    created_at DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            ''')
            
            # Document highlights table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='document_highlights' AND xtype='U')
                CREATE TABLE document_highlights (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    document_id INT NOT NULL,
                    highlight_type NVARCHAR(100) NOT NULL,
                    start_position INT NOT NULL,
                    end_position INT NOT NULL,
                    highlighted_text NVARCHAR(MAX) NOT NULL,
                    confidence_score FLOAT,
                    created_at DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            ''')
            
            # Create indexes
            try:
                cursor.execute('CREATE INDEX idx_documents_user_id ON documents(user_id)')
            except:
                pass
            try:
                cursor.execute('CREATE INDEX idx_documents_hash ON documents(file_hash)')
            except:
                pass
            try:
                cursor.execute('CREATE INDEX idx_analysis_document_id ON analysis_results(document_id)')
            except:
                pass
            
            conn.commit()
    
    def _init_clones_db_schema(self):
        """Initialize clones_db tables"""
        with self._get_connection('clones_db') as conn:
            cursor = conn.cursor()
            
            # Clone training documents table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='clone_training_docs' AND xtype='U')
                CREATE TABLE clone_training_docs (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    filename NVARCHAR(255) NOT NULL,
                    original_filename NVARCHAR(255) NOT NULL,
                    file_hash NVARCHAR(128) UNIQUE NOT NULL,
                    content_text NVARCHAR(MAX),
                    file_type NVARCHAR(100) NOT NULL,
                    file_size BIGINT NOT NULL,
                    upload_date DATETIME DEFAULT GETDATE(),
                    is_confirmed BIT DEFAULT 0,
                    similarity_vector NVARCHAR(MAX),
                    metadata NVARCHAR(MAX) DEFAULT '{}'
                )
            ''')
            
            # Clone matches table
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='clone_matches' AND xtype='U')
                CREATE TABLE clone_matches (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    document_id INT NOT NULL,
                    training_doc_id INT NOT NULL,
                    similarity_score FLOAT NOT NULL,
                    match_type NVARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (training_doc_id) REFERENCES clone_training_docs(id)
                )
            ''')
            
            # Create indexes
            try:
                cursor.execute('CREATE INDEX idx_clone_docs_hash ON clone_training_docs(file_hash)')
            except:
                pass
            try:
                cursor.execute('CREATE INDEX idx_clone_matches_doc_id ON clone_matches(document_id)')
            except:
                pass
            try:
                cursor.execute('CREATE INDEX idx_clone_matches_similarity ON clone_matches(similarity_score)')
            except:
                pass
            
            conn.commit()
    
    # Auth DB Methods
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user in auth_db"""
        user_id = str(uuid.uuid4())
        
        with self._get_connection('auth_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, first_name, last_name, 
                                 oauth_provider, oauth_id, profile_picture, settings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_data.get('username'),
                user_data.get('email'),
                user_data.get('password_hash'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('oauth_provider'),
                user_data.get('oauth_id'),
                user_data.get('profile_picture'),
                json.dumps(user_data.get('settings', {}))
            ))
            conn.commit()
        
        return user_id
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from auth_db"""
        with self._get_connection('auth_db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row.id,
                    'username': row.username,
                    'email': row.email,
                    'password_hash': row.password_hash,
                    'first_name': row.first_name,
                    'last_name': row.last_name,
                    'oauth_provider': row.oauth_provider,
                    'oauth_id': row.oauth_id,
                    'profile_picture': row.profile_picture,
                    'is_active': row.is_active,
                    'is_verified': row.is_verified,
                    'created_at': row.created_at,
                    'last_login': row.last_login,
                    'settings': json.loads(row.settings) if row.settings else {}
                }
        return None
    
    def update_user_login(self, user_id: str):
        """Update user's last login time"""
        with self._get_connection('auth_db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET last_login = GETDATE() WHERE id = ?',
                (user_id,)
            )
            conn.commit()
    
    # Docs DB Methods
    def store_document(self, user_id: str, document_data: Dict[str, Any]) -> int:
        """Store a document in docs_db"""
        with self._get_connection('docs_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (user_id, filename, original_filename, file_size, 
                                     file_type, file_hash, upload_path, content_text, metadata)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                document_data.get('filename'),
                document_data.get('original_filename'),
                document_data.get('file_size'),
                document_data.get('file_type'),
                document_data.get('file_hash'),
                document_data.get('upload_path'),
                document_data.get('content_text'),
                json.dumps(document_data.get('metadata', {}))
            ))
            
            document_id = cursor.fetchone()[0]
            conn.commit()
            return document_id
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a user from docs_db"""
        with self._get_connection('docs_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, original_filename, file_size, file_type, 
                       file_hash, upload_date, last_modified, metadata
                FROM documents 
                WHERE user_id = ?
                ORDER BY upload_date DESC
            ''', (user_id,))
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row.id,
                    'filename': row.filename,
                    'original_filename': row.original_filename,
                    'file_size': row.file_size,
                    'file_type': row.file_type,
                    'file_hash': row.file_hash,
                    'upload_date': row.upload_date,
                    'last_modified': row.last_modified,
                    'metadata': json.loads(row.metadata) if row.metadata else {}
                })
            
            return documents
    
    def get_document_details(self, document_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed document information including analysis results"""
        with self._get_connection('docs_db') as conn:
            cursor = conn.cursor()
            
            # Get document info
            cursor.execute('''
                SELECT * FROM documents 
                WHERE id = ? AND user_id = ?
            ''', (document_id, user_id))
            
            doc_row = cursor.fetchone()
            if not doc_row:
                return None
            
            # Get analysis results
            cursor.execute('''
                SELECT analysis_type, result_data, confidence_score, processing_time, created_at
                FROM analysis_results 
                WHERE document_id = ?
                ORDER BY created_at DESC
            ''', (document_id,))
            
            analysis_results = []
            for row in cursor.fetchall():
                analysis_results.append({
                    'analysis_type': row.analysis_type,
                    'result_data': json.loads(row.result_data),
                    'confidence_score': row.confidence_score,
                    'processing_time': row.processing_time,
                    'created_at': row.created_at
                })
            
            # Get highlights
            cursor.execute('''
                SELECT highlight_type, start_position, end_position, 
                       highlighted_text, confidence_score, created_at
                FROM document_highlights 
                WHERE document_id = ?
                ORDER BY start_position
            ''', (document_id,))
            
            highlights = []
            for row in cursor.fetchall():
                highlights.append({
                    'highlight_type': row.highlight_type,
                    'start_position': row.start_position,
                    'end_position': row.end_position,
                    'highlighted_text': row.highlighted_text,
                    'confidence_score': row.confidence_score,
                    'created_at': row.created_at
                })
            
            return {
                'id': doc_row.id,
                'filename': doc_row.filename,
                'original_filename': doc_row.original_filename,
                'file_size': doc_row.file_size,
                'file_type': doc_row.file_type,
                'file_hash': doc_row.file_hash,
                'upload_path': doc_row.upload_path,
                'content_text': doc_row.content_text,
                'upload_date': doc_row.upload_date,
                'last_modified': doc_row.last_modified,
                'metadata': json.loads(doc_row.metadata) if doc_row.metadata else {},
                'analysis_results': analysis_results,
                'highlights': highlights
            }
    
    def store_analysis_result(self, document_id: int, analysis_data: Dict[str, Any]) -> int:
        """Store analysis results in docs_db"""
        with self._get_connection('docs_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results (document_id, analysis_type, result_data, 
                                            confidence_score, processing_time)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?)
            ''', (
                document_id,
                analysis_data.get('analysis_type'),
                json.dumps(analysis_data.get('result_data', {})),
                analysis_data.get('confidence_score'),
                analysis_data.get('processing_time')
            ))
            
            result_id = cursor.fetchone()[0]
            conn.commit()
            return result_id
    
    def store_document_highlights(self, document_id: int, highlights: List[Dict[str, Any]]):
        """Store document highlights in docs_db"""
        with self._get_connection('docs_db') as conn:
            cursor = conn.cursor()
            
            for highlight in highlights:
                cursor.execute('''
                    INSERT INTO document_highlights (document_id, highlight_type, start_position, 
                                                   end_position, highlighted_text, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    document_id,
                    highlight.get('highlight_type'),
                    highlight.get('start_position'),
                    highlight.get('end_position'),
                    highlight.get('highlighted_text'),
                    highlight.get('confidence_score')
                ))
            
            conn.commit()
    
    # Clones DB Methods  
    def store_clone_training_document(self, document_data: Dict[str, Any]) -> int:
        """Store a document for clone detection training in clones_db"""
        with self._get_connection('clones_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clone_training_docs (filename, original_filename, file_hash, 
                                               content_text, file_type, file_size, 
                                               similarity_vector, metadata)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_data.get('filename'),
                document_data.get('original_filename'),
                document_data.get('file_hash'),
                document_data.get('content_text'),
                document_data.get('file_type'),
                document_data.get('file_size'),
                json.dumps(document_data.get('similarity_vector', [])),
                json.dumps(document_data.get('metadata', {}))
            ))
            
            doc_id = cursor.fetchone()[0]
            conn.commit()
            return doc_id
    
    def get_clone_training_documents(self) -> List[Dict[str, Any]]:
        """Get all clone training documents from clones_db"""
        with self._get_connection('clones_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, original_filename, file_hash, content_text, 
                       file_type, file_size, upload_date, is_confirmed, 
                       similarity_vector, metadata
                FROM clone_training_docs
                ORDER BY upload_date DESC
            ''')
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row.id,
                    'filename': row.filename,
                    'original_filename': row.original_filename,
                    'file_hash': row.file_hash,
                    'content_text': row.content_text,
                    'file_type': row.file_type,
                    'file_size': row.file_size,
                    'upload_date': row.upload_date,
                    'is_confirmed': row.is_confirmed,
                    'similarity_vector': json.loads(row.similarity_vector) if row.similarity_vector else [],
                    'metadata': json.loads(row.metadata) if row.metadata else {}
                })
            
            return documents
    
    def store_clone_match(self, document_id: int, training_doc_id: int, 
                         similarity_score: float, match_type: str) -> int:
        """Store a clone match result in clones_db"""
        with self._get_connection('clones_db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clone_matches (document_id, training_doc_id, similarity_score, match_type)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?)
            ''', (document_id, training_doc_id, similarity_score, match_type))
            
            match_id = cursor.fetchone()[0]
            conn.commit()
            return match_id
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics from all databases"""
        stats = {}
        
        try:
            # Auth DB stats
            with self._get_connection('auth_db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                stats['auth_db'] = {
                    'total_users': cursor.fetchone()[0],
                    'status': 'connected'
                }
                
            # Docs DB stats
            with self._get_connection('docs_db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM documents')
                total_docs = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM analysis_results')
                total_analysis = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM document_highlights')
                total_highlights = cursor.fetchone()[0]
                
                stats['docs_db'] = {
                    'total_documents': total_docs,
                    'total_analysis_results': total_analysis,
                    'total_highlights': total_highlights,
                    'status': 'connected'
                }
                
            # Clones DB stats
            with self._get_connection('clones_db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM clone_training_docs')
                total_training_docs = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM clone_matches')
                total_matches = cursor.fetchone()[0]
                
                stats['clones_db'] = {
                    'total_training_documents': total_training_docs,
                    'total_clone_matches': total_matches,
                    'status': 'connected'
                }
                
        except Exception as e:
            stats['error'] = str(e)
            
        return stats

# Global instance
sql_server_db = SQLServerDatabaseService()
