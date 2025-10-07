import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import jwt

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'auth_users.db')
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the authentication database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT,
                    avatar_url TEXT,
                    provider TEXT NOT NULL DEFAULT 'local',
                    provider_id TEXT,
                    role TEXT DEFAULT 'user',
                    is_verified BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # OAuth providers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS oauth_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    provider TEXT NOT NULL,
                    provider_id TEXT NOT NULL,
                    access_token TEXT,
                    refresh_token TEXT,
                    token_expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(provider, provider_id)
                )
            ''')
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    mime_type TEXT,
                    content_hash TEXT,
                    analysis_status TEXT DEFAULT 'pending',
                    analysis_result TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analyzed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    layer_name TEXT NOT NULL,
                    score REAL,
                    status TEXT,
                    result_data TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            # Sessions table for JWT token management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    refresh_token TEXT UNIQUE,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            
            # Create default admin user if not exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('admin@authenticator.ai',))
            if cursor.fetchone()[0] == 0:
                self.create_admin_user()
    
    def create_admin_user(self):
        """Create default admin user"""
        admin_data = {
            'email': 'admin@authenticator.ai',
            'name': 'System Administrator',
            'password': 'admin123',
            'role': 'admin',
            'is_verified': True
        }
        self.create_user(admin_data)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (user_data['email'],))
            if cursor.fetchone():
                raise ValueError(f"User with email {user_data['email']} already exists")
            
            # Hash password if provided
            password_hash = None
            if user_data.get('password'):
                password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (email, name, password_hash, avatar_url, provider, provider_id, role, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['email'],
                user_data['name'],
                password_hash,
                user_data.get('avatar_url'),
                user_data.get('provider', 'local'),
                user_data.get('provider_id'),
                user_data.get('role', 'user'),
                user_data.get('is_verified', False)
            ))
            
            user_id = cursor.lastrowid
            
            # Get created user
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = dict(cursor.fetchone())
            user.pop('password_hash', None)
            return user
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user.pop('password_hash', None)
                return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user.pop('password_hash', None)
                return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = ? AND password_hash = ? AND is_active = 1
            ''', (email, password_hash))
            
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user.pop('password_hash', None)
                
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user['id'],))
                
                return user
        return None
    
    def create_oauth_user(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update user from OAuth provider"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists with this email
            cursor.execute('SELECT * FROM users WHERE email = ?', (provider_data['email'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                user = dict(existing_user)
                user_id = user['id']
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users (email, name, avatar_url, provider, provider_id, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    provider_data['email'],
                    provider_data['name'],
                    provider_data.get('avatar_url'),
                    provider_data['provider'],
                    provider_data['provider_id'],
                    True
                ))
                user_id = cursor.lastrowid
                
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = dict(cursor.fetchone())
            
            # Update or create OAuth provider record
            cursor.execute('''
                INSERT OR REPLACE INTO oauth_providers 
                (user_id, provider, provider_id, access_token, refresh_token, token_expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                provider_data['provider'],
                provider_data['provider_id'],
                provider_data.get('access_token'),
                provider_data.get('refresh_token'),
                provider_data.get('token_expires_at')
            ))
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            user.pop('password_hash', None)
            return user
    
    def save_document(self, user_id: int, document_data: Dict[str, Any]) -> int:
        """Save uploaded document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents 
                (user_id, filename, original_filename, file_path, file_size, mime_type, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                document_data['filename'],
                document_data['original_filename'],
                document_data['file_path'],
                document_data.get('file_size'),
                document_data.get('mime_type'),
                document_data.get('content_hash')
            ))
            
            return cursor.lastrowid
    
    def get_user_documents(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM documents 
                WHERE user_id = ? 
                ORDER BY uploaded_at DESC
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_document_analysis(self, document_id: int, analysis_data: Dict[str, Any]):
        """Update document analysis results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE documents 
                SET analysis_status = ?, analysis_result = ?, analyzed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                analysis_data['status'],
                analysis_data.get('result'),
                document_id
            ))
    
    def save_analysis_layer_result(self, document_id: int, layer_data: Dict[str, Any]):
        """Save individual layer analysis result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results 
                (document_id, layer_name, score, status, result_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                document_id,
                layer_data['layer_name'],
                layer_data.get('score'),
                layer_data.get('status'),
                layer_data.get('result_data')
            ))

class JWTManager:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
    
    def generate_tokens(self, user_data: Dict[str, Any]) -> Tuple[str, str]:
        """Generate access and refresh tokens"""
        # Access token payload
        access_payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'role': user_data.get('role', 'user'),
            'exp': datetime.utcnow() + self.access_token_expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_data['id'],
            'exp': datetime.utcnow() + self.refresh_token_expire,
            'iat': datetime.utcnow(),
            'type': 'refresh',
            'jti': secrets.token_urlsafe(32)  # Unique token ID
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return access_token, refresh_token
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get('type') != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
        
        # Generate new access token
        db_manager = DatabaseManager()
        user = db_manager.get_user_by_id(payload['user_id'])
        if not user:
            return None
        
        access_token, _ = self.generate_tokens(user)
        return access_token

# Global instances
db_manager = DatabaseManager()
jwt_manager = JWTManager()
