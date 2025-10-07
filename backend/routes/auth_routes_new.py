from flask import Blueprint, request, jsonify, redirect, url_for, session
from flasgger import swag_from
from ..models.auth_models import db_manager, jwt_manager
from ..services.oauth_service import oauth_manager
import requests
import os
import traceback

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
@swag_from({
    "summary": "User Authentication",
    "description": "Authenticate a user with email and password",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "user@example.com"
                    },
                    "password": {
                        "type": "string",
                        "example": "password123"
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Login successful",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user": {"type": "object"},
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"}
                }
            }
        },
        "401": {"description": "Invalid credentials"}
    }
})
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        user = db_manager.authenticate_user(email, password)
        if user:
            access_token, refresh_token = jwt_manager.generate_tokens(user)
            return jsonify({
                "message": "Login successful",
                "user": user,
                "access_token": access_token,
                "refresh_token": refresh_token
            })
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/signup", methods=["POST"])
@swag_from({
    "summary": "User Registration",
    "description": "Register a new user account",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["email", "password", "name"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "minLength": 6},
                    "name": {"type": "string"},
                    "avatar_url": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "User created successfully"},
        "400": {"description": "Invalid input or user already exists"}
    }
})
def signup():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        
        if not all([email, password, name]):
            return jsonify({"error": "Email, password, and name are required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(email)
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400
        
        # Create user
        user_data = {
            "email": email,
            "password": password,
            "name": name,
            "avatar_url": data.get("avatar_url"),
            "provider": "local"
        }
        
        user = db_manager.create_user(user_data)
        access_token, refresh_token = jwt_manager.generate_tokens(user)
        
        return jsonify({
            "message": "User created successfully",
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/refresh", methods=["POST"])
@swag_from({
    "summary": "Refresh Access Token",
    "description": "Get a new access token using refresh token",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "refresh_token": {"type": "string"}
                }
            }
        }
    ]
})
def refresh_token():
    try:
        data = request.get_json()
        refresh_token = data.get("refresh_token")
        
        if not refresh_token:
            return jsonify({"error": "Refresh token is required"}), 400
        
        new_access_token = jwt_manager.refresh_access_token(refresh_token)
        if new_access_token:
            return jsonify({"access_token": new_access_token})
        
        return jsonify({"error": "Invalid or expired refresh token"}), 401
    except Exception as e:
        print(f"Token refresh error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# OAuth Routes

@auth_bp.route("/oauth/providers", methods=["GET"])
@swag_from({
    "summary": "Get Available OAuth Providers",
    "description": "Get list of configured OAuth providers",
    "responses": {
        "200": {
            "description": "List of available providers",
            "schema": {
                "type": "object",
                "properties": {
                    "providers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "display_name": {"type": "string"},
                                "login_url": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_oauth_providers():
    try:
        providers = oauth_manager.get_available_providers()
        return jsonify({"providers": providers})
    except Exception as e:
        print(f"OAuth providers error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/oauth/<provider>", methods=["GET"])
@swag_from({
    "summary": "OAuth Login",
    "description": "Redirect to OAuth provider for authentication",
    "parameters": [
        {
            "name": "provider",
            "in": "path",
            "required": True,
            "type": "string",
            "enum": ["google", "microsoft", "github", "discord"]
        }
    ]
})
def oauth_login(provider):
    try:
        auth_url = oauth_manager.get_provider_login_url(provider)
        if auth_url:
            return redirect(auth_url)
        return jsonify({"error": f"Provider {provider} not configured"}), 400
    except Exception as e:
        print(f"OAuth login error for {provider}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/oauth/<provider>/callback", methods=["GET"])
@swag_from({
    "summary": "OAuth Callback",
    "description": "Handle OAuth provider callback",
    "parameters": [
        {
            "name": "provider",
            "in": "path",
            "required": True,
            "type": "string"
        },
        {
            "name": "code",
            "in": "query",
            "required": True,
            "type": "string"
        },
        {
            "name": "state",
            "in": "query",
            "required": True,
            "type": "string"
        }
    ]
})
def oauth_callback(provider):
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({"error": f"OAuth error: {error}"}), 400
        
        if not code or not state:
            return jsonify({"error": "Missing authorization code or state"}), 400
        
        # Handle OAuth callback
        user_info = oauth_manager.handle_callback(provider, code, state)
        if not user_info:
            return jsonify({"error": "OAuth authentication failed"}), 400
        
        # Create or update user in database
        user = db_manager.create_oauth_user(user_info)
        access_token, refresh_token = jwt_manager.generate_tokens(user)
        
        # Redirect to frontend with tokens (in production, use secure methods)
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}")
        
    except Exception as e:
        print(f"OAuth callback error for {provider}: {e}")
        traceback.print_exc()
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/auth/error?message=Authentication failed")

@auth_bp.route("/me", methods=["GET"])
@swag_from({
    "summary": "Get Current User",
    "description": "Get current authenticated user information",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {"description": "User information"},
        "401": {"description": "Unauthorized"}
    }
})
def get_current_user():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt_manager.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user = db_manager.get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({"user": user})
    except Exception as e:
        print(f"Get current user error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/logout", methods=["POST"])
@swag_from({
    "summary": "User Logout",
    "description": "Logout user and invalidate session",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {"description": "Logout successful"},
        "401": {"description": "Unauthorized"}
    }
})
def logout():
    try:
        # In a full implementation, you would invalidate the token in the database
        # For now, we'll just return success and let the client handle token removal
        return jsonify({"message": "Logout successful"})
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({"error": "Internal server error"}), 500
