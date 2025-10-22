"""
Authentication Routes for Authenticator.AI - SQL Server Version
Handles user registration, login, and token management
"""

from flask import Blueprint, request, jsonify, g
from ..services.auth_service_sqlserver import auth_service
import traceback

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Additional user data
        user_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'username': data.get('username')
        }
        
        result = auth_service.register_user(email, password, **user_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'token': result['token'],
                'user': result['user']
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        result = auth_service.login_user(email, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': result['token'],
                'user': result['user']
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route("/me", methods=["GET"])
@auth_service.require_authentication
def get_current_user():
    """Get current user information"""
    try:
        user_context = auth_service.get_current_user_context()
        
        if not user_context:
            return jsonify({
                'success': False,
                'error': 'User context not found'
            }), 401
        
        # Get full user data
        user = auth_service.get_user_by_email(user_context.get('email'))
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'profile_picture': user.get('profile_picture'),
                'is_verified': user.get('is_verified', False),
                'created_at': user.get('created_at')
            }
        })
        
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route("/logout", methods=["POST"])
@auth_service.require_authentication
def logout():
    """Logout endpoint (token invalidation would go here)"""
    try:
        # In a more complete implementation, you would invalidate the token
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route("/refresh", methods=["POST"])
@auth_service.require_authentication
def refresh_token():
    """Refresh JWT token"""
    try:
        user_context = auth_service.get_current_user_context()
        
        if not user_context:
            return jsonify({
                'success': False,
                'error': 'User context not found'
            }), 401
        
        # Get user data and generate new token
        user = auth_service.get_user_by_email(user_context.get('email'))
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        new_token = auth_service.generate_jwt_token(user)
        
        return jsonify({
            'success': True,
            'token': new_token
        })
        
    except Exception as e:
        print(f"❌ Refresh token error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# OAuth placeholder routes (for future implementation)
@auth_bp.route("/oauth/providers", methods=["GET"])
def get_oauth_providers():
    """Get available OAuth providers"""
    return jsonify({
        'success': True,
        'providers': [
            {
                'name': 'google',
                'display_name': 'Google',
                'enabled': False
            },
            {
                'name': 'github',
                'display_name': 'GitHub', 
                'enabled': False
            }
        ]
    })

@auth_bp.route("/oauth/<provider>", methods=["GET"])
def oauth_login(provider):
    """OAuth login redirect (placeholder)"""
    return jsonify({
        'success': False,
        'error': f'OAuth provider {provider} not yet implemented'
    }), 501

@auth_bp.route("/oauth/<provider>/callback", methods=["GET"])
def oauth_callback(provider):
    """OAuth callback handler (placeholder)"""
    return jsonify({
        'success': False,
        'error': f'OAuth provider {provider} not yet implemented'
    }), 501
