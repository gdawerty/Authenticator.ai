from flask import Blueprint, request, jsonify, redirect, url_for, session
from flasgger import swag_from
from ..services.user_service import login_user, create_user, get_user_by_email
import requests
import os

auth_bp = Blueprint("auth", __name__)

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID', 'your-microsoft-client-id')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET', 'your-microsoft-client-secret')

@auth_bp.route("/login", methods=["POST"])
@swag_from({
    "summary": "User Authentication",
    "description": "Authenticate a user with username and password",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "username": {
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
                    "message": {
                        "type": "string",
                        "example": "Login successful"
                    },
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "email": {"type": "string"},
                            "name": {"type": "string"},
                            "role": {"type": "string"}
                        }
                    },
                    "token": {"type": "string"}
                }
            }
        },
        "401": {
            "description": "Invalid credentials"
        }
    }
})
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = login_user(username, password)
    if user:
        return jsonify({
            "message": "Login successful",
            "user": user,
            "token": "jwt_token_here"  # Generate actual JWT token
        })
    return jsonify({"error": "Invalid credentials"}), 401

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
                    "email": {
                        "type": "string",
                        "format": "email",
                        "example": "user@example.com"
                    },
                    "password": {
                        "type": "string",
                        "minimum": 6,
                        "example": "password123"
                    },
                    "name": {
                        "type": "string",
                        "example": "John Doe"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "User created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "User created successfully"
                    },
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "email": {"type": "string"},
                            "name": {"type": "string"},
                            "role": {"type": "string"}
                        }
                    },
                    "token": {"type": "string"}
                }
            }
        },
        "400": {
            "description": "Invalid input or user already exists"
        }
    }
})
def signup():
    data = request.get_json()
    
    # Validate required fields
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    
    if not all([email, password, name]):
        return jsonify({"error": "Email, password, and name are required"}), 400
    
    # Validate email format (basic validation)
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate password strength
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    
    # Check if user already exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400
    
    # Create new user
    user_data = {
        "email": email,
        "password": password,
        "name": name,
        "role": "user",
        "provider": "local"
    }
    
    try:
        user = create_user(user_data)
        return jsonify({
            "message": "User created successfully",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            },
            "token": "jwt_token_here"  # Generate actual JWT token
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500

@auth_bp.route("/oauth/google", methods=["GET"])
def google_oauth():
    """Initiate Google OAuth flow"""
    auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:8000/auth/oauth/google/callback&scope=openid email profile&response_type=code"
    return redirect(auth_url)

@auth_bp.route("/oauth/google/callback", methods=["GET"])
def google_oauth_callback():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400
    
    # Exchange code for token
    token_response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8000/auth/oauth/google/callback'
    })
    
    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        # Get user info
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            
            # Create or get user
            user = get_user_by_email(user_data.get('email'))
            if not user:
                user = create_user({
                    'email': user_data.get('email'),
                    'name': user_data.get('name'),
                    'provider': 'google',
                    'provider_id': user_data.get('id'),
                    'role': 'user'
                })
            
            # Redirect to frontend with token
            return redirect(f"http://localhost:5173/auth/success?token=jwt_token_here&user={user['id']}")
    
    return jsonify({"error": "OAuth authentication failed"}), 400

@auth_bp.route("/oauth/microsoft", methods=["GET"])
def microsoft_oauth():
    """Initiate Microsoft OAuth flow"""
    auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={MICROSOFT_CLIENT_ID}&response_type=code&redirect_uri=http://localhost:8000/auth/oauth/microsoft/callback&scope=openid email profile"
    return redirect(auth_url)

@auth_bp.route("/oauth/microsoft/callback", methods=["GET"])
def microsoft_oauth_callback():
    """Handle Microsoft OAuth callback"""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400
    
    # Exchange code for token
    token_response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data={
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8000/auth/oauth/microsoft/callback'
    })
    
    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        # Get user info
        user_response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            
            # Create or get user
            user = get_user_by_email(user_data.get('userPrincipalName'))
            if not user:
                user = create_user({
                    'email': user_data.get('userPrincipalName'),
                    'name': user_data.get('displayName'),
                    'provider': 'microsoft',
                    'provider_id': user_data.get('id'),
                    'role': 'user'
                })
            
            # Redirect to frontend with token
            return redirect(f"http://localhost:5173/auth/success?token=jwt_token_here&user={user['id']}")
    
    return jsonify({"error": "OAuth authentication failed"}), 400

@auth_bp.route("/user/logs/<user_id>", methods=["GET"])
def get_user_logs(user_id):
    """Get analysis logs for a specific user"""
    from ..services.log_service import get_user_analysis_logs
    
    logs = get_user_analysis_logs(user_id)
    return jsonify({"logs": logs})

@auth_bp.route("/admin/users", methods=["GET"])
def get_all_users():
    """Admin endpoint to get all users"""
    from ..services.user_service import get_all_users, verify_admin
    
    # Verify admin access
    token = request.headers.get('Authorization')
    if not verify_admin(token):
        return jsonify({"error": "Admin access required"}), 403
    
    users = get_all_users()
    return jsonify({"users": users})

@auth_bp.route("/admin/logs", methods=["GET"])
def get_all_logs():
    """Admin endpoint to get all analysis logs"""
    from ..services.log_service import get_all_analysis_logs
    from ..services.user_service import verify_admin
    
    # Verify admin access
    token = request.headers.get('Authorization')
    if not verify_admin(token):
        return jsonify({"error": "Admin access required"}), 403
    
    logs = get_all_analysis_logs()
    return jsonify({"logs": logs})
