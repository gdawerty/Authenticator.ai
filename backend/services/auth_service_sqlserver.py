"""
Authentication Service for Authenticator.AI - SQL Server Version
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
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, email: str, password: str = None, **kwargs) -> Dict[str, Any]:
        """
        Create a new user account
        
        Args:
            email: User's email address
            password: User's password (optional for OAuth)
            **kwargs: Additional user data
            
        Returns:
            Dict containing user data or error information
        """
        try:
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = self.hash_password(password)
            
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'username': kwargs.get('username', email.split('@')[0]),
                'first_name': kwargs.get('first_name'),
                'last_name': kwargs.get('last_name'),
                'oauth_provider': kwargs.get('oauth_provider'),
                'oauth_id': kwargs.get('oauth_id'),
                'profile_picture': kwargs.get('profile_picture'),
                'settings': kwargs.get('settings', {})
            }
            
            user_id = self.db_service.create_user(user_data)
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
            
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e) or 'Violation of UNIQUE KEY constraint' in str(e):
                return {
                    'success': False,
                    'error': 'Email already exists',
                    'code': 'EMAIL_EXISTS'
                }
            
            return {
                'success': False,
                'error': f'User creation failed: {str(e)}',
                'code': 'CREATION_FAILED'
            }
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict containing authentication result
        """
        user = self.db_service.get_user_by_email(email)
        
        if not user:
            return {
                'success': False,
                'error': 'Invalid email or password',
                'code': 'INVALID_CREDENTIALS'
            }
        
        if not user.get('is_active'):
            return {
                'success': False,
                'error': 'Account is deactivated',
                'code': 'ACCOUNT_DEACTIVATED'
            }
        
        # Check password
        if not user.get('password_hash'):
            return {
                'success': False,
                'error': 'Password not set for this account',
                'code': 'NO_PASSWORD'
            }
        
        if not self.verify_password(password, user['password_hash']):
            return {
                'success': False,
                'error': 'Invalid email or password',
                'code': 'INVALID_CREDENTIALS'
            }
        
        # Update last login
        self.db_service.update_user_login(user['id'])
        
        return {
            'success': True,
            'user': user
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        # This method would need to be implemented in sqlserver_db_service
        # For now, we'll use get_user_by_email which we have
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.db_service.get_user_by_email(email)
    
    def generate_jwt_token(self, user_data: Dict[str, Any], 
                          expires_delta: Optional[timedelta] = None) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_data: User information to encode
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'username': user_data.get('username'),
            'exp': datetime.utcnow() + expires_delta,
            'iat': datetime.utcnow(),
            'iss': 'authenticator-ai'
        }
        
        secret_key = current_app.config.get('SECRET_KEY', 'fallback-secret-key')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Dict containing verification result and user data
        """
        try:
            secret_key = current_app.config.get('SECRET_KEY', 'fallback-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            return {
                'success': True,
                'payload': payload,
                'user_id': payload.get('user_id'),
                'email': payload.get('email')
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token has expired',
                'code': 'TOKEN_EXPIRED'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid token',
                'code': 'INVALID_TOKEN'
            }
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Complete login process with authentication and token generation
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict containing login result and token
        """
        auth_result = self.authenticate_user(email, password)
        
        if not auth_result['success']:
            return auth_result
        
        user = auth_result['user']
        token = self.generate_jwt_token(user)
        
        return {
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'profile_picture': user.get('profile_picture'),
                'is_verified': user.get('is_verified', False)
            }
        }
    
    def register_user(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Complete user registration process
        
        Args:
            email: User's email
            password: User's password
            **kwargs: Additional user data
            
        Returns:
            Dict containing registration result and token
        """
        create_result = self.create_user(email, password, **kwargs)
        
        if not create_result['success']:
            return create_result
        
        # Login the newly created user
        return self.login_user(email, password)
    
    def get_current_user_context(self) -> Optional[Dict[str, Any]]:
        """Get current user context from Flask g object"""
        return getattr(g, 'current_user', None)
    
    def require_authentication(self, f):
        """Decorator to require authentication for routes"""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = None
            
            # Try to get token from request
            from flask import request
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }, 401
            
            token = auth_header.split(' ')[1]
            verification_result = self.verify_jwt_token(token)
            
            if not verification_result['success']:
                return {
                    'error': verification_result['error'],
                    'code': verification_result['code']
                }, 401
            
            # Store user context
            g.current_user = verification_result['payload']
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def optional_authentication(self, f):
        """Decorator for optional authentication (doesn't fail if no token)"""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            auth_header = request.headers.get('Authorization')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                verification_result = self.verify_jwt_token(token)
                
                if verification_result['success']:
                    g.current_user = verification_result['payload']
            
            return f(*args, **kwargs)
        
        return decorated_function

# Global authentication service instance
auth_service = AuthenticationService()
