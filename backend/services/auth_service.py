"""
Authentication Service for Authenticator.AI
Handles JWT tokens, user sessions, and secure access control
"""

import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from flask import current_app, g
import json
from .sqlserver_db_service import sql_server_db

class AuthenticationService:
    """
    Comprehensive authentication service with JWT, user management, and session handling
    """
    
    def __init__(self):
        # Use SQL Server instead of SQLite
        self.db_service = sql_server_db
    
    def _initialize_database(self):
        """Initialize authentication database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
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
            
            # Create indexes for users table
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id)')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # API keys table for service authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_name TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    permissions TEXT DEFAULT '[]',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_used DATETIME,
                    usage_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, email: str, password: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new user account"""
        import uuid
        
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password) if password else None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO users (
                        id, email, username, password_hash, first_name, last_name,
                        oauth_provider, oauth_id, profile_picture, settings
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, email, kwargs.get('username'), password_hash,
                    kwargs.get('first_name'), kwargs.get('last_name'),
                    kwargs.get('oauth_provider'), kwargs.get('oauth_id'),
                    kwargs.get('profile_picture'), json.dumps(kwargs.get('settings', {}))
                ))
                
                return {
                    'user_id': user_id,
                    'email': email,
                    'created': True
                }
                
        except sqlite3.IntegrityError as e:
            if 'email' in str(e):
                return {'error': 'Email already exists'}
            elif 'username' in str(e):
                return {'error': 'Username already exists'}
            else:
                return {'error': 'User creation failed'}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = ? AND is_active = TRUE
            ''', (email,))
            
            user = cursor.fetchone()
            
            if user and user['password_hash'] and self.verify_password(password, user['password_hash']):
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user['id'],))
                
                return {
                    'user_id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'profile_picture': user['profile_picture'],
                    'settings': json.loads(user['settings'] or '{}')
                }
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE id = ? AND is_active = TRUE
            ''', (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'user_id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'profile_picture': user['profile_picture'],
                    'oauth_provider': user['oauth_provider'],
                    'is_verified': user['is_verified'],
                    'created_at': user['created_at'],
                    'last_login': user['last_login'],
                    'settings': json.loads(user['settings'] or '{}')
                }
        
        return None
    
    def generate_jwt_token(self, user_id: str, secret_key: str, expires_hours: int = 24) -> str:
        """Generate JWT token for user"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        payload = {
            'user_id': user_id,
            'email': user['email'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow(),
            'type': 'access_token'
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # Store session in database
        self._create_session(user_id, token)
        
        return token
    
    def verify_jwt_token(self, token: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Check if session is still active
            if self._is_session_active(payload['user_id'], token):
                # Update last activity
                self._update_session_activity(payload['user_id'], token)
                return payload
            else:
                return None
                
        except jwt.ExpiredSignatureError:
            self._deactivate_session_by_token(token)
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _create_session(self, user_id: str, token: str):
        """Create user session record"""
        import uuid
        import hashlib
        
        session_id = str(uuid.uuid4())
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions (
                    id, user_id, token_hash, expires_at
                ) VALUES (?, ?, ?, ?)
            ''', (
                session_id, user_id, token_hash,
                datetime.utcnow() + timedelta(hours=24)
            ))
    
    def _is_session_active(self, user_id: str, token: str) -> bool:
        """Check if session is active"""
        import hashlib
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM user_sessions 
                WHERE user_id = ? AND token_hash = ? 
                AND is_active = TRUE AND expires_at > CURRENT_TIMESTAMP
            ''', (user_id, token_hash))
            
            return cursor.fetchone() is not None
    
    def _update_session_activity(self, user_id: str, token: str):
        """Update session last activity"""
        import hashlib
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE user_id = ? AND token_hash = ?
            ''', (user_id, token_hash))
    
    def _deactivate_session_by_token(self, token: str):
        """Deactivate session by token"""
        import hashlib
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE token_hash = ?
            ''', (token_hash,))
    
    def logout_user(self, user_id: str, token: str = None):
        """Logout user - deactivate session(s)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if token:
                # Logout specific session
                import hashlib
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                cursor.execute('''
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE user_id = ? AND token_hash = ?
                ''', (user_id, token_hash))
            else:
                # Logout all sessions
                cursor.execute('''
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE user_id = ?
                ''', (user_id,))
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE expires_at < CURRENT_TIMESTAMP
            ''')
            
            # Delete old inactive sessions (older than 30 days)
            cursor.execute('''
                DELETE FROM user_sessions 
                WHERE is_active = FALSE 
                AND created_at < datetime('now', '-30 days')
            ''')
    
    def get_user_sessions(self, user_id: str) -> list:
        """Get active sessions for user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, ip_address, user_agent, created_at, last_activity
                FROM user_sessions 
                WHERE user_id = ? AND is_active = TRUE
                ORDER BY last_activity DESC
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]

# Global authentication service instance
auth_service = AuthenticationService()
