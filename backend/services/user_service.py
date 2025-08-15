import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

# Simple file-based user storage (use proper database in production)
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')

def ensure_data_dir():
    """Ensure data directory exists"""
    data_dir = os.path.dirname(USERS_FILE)
    os.makedirs(data_dir, exist_ok=True)

def load_users() -> List[Dict[str, Any]]:
    """Load users from file"""
    ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        # Create default admin user
        admin_user = {
            'id': '1',
            'email': 'admin@authenticator.ai',
            'name': 'Admin User',
            'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
            'role': 'admin',
            'provider': 'local',
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        save_users([admin_user])
        return [admin_user]
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_users(users: List[Dict[str, Any]]):
    """Save users to file"""
    ensure_data_dir()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, default=str)

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user"""
    users = load_users()
    
    # Check if user already exists
    existing_user = next((u for u in users if u['email'] == user_data['email']), None)
    if existing_user:
        raise ValueError(f"User with email {user_data['email']} already exists")
    
    new_user = {
        'id': str(len(users) + 1),
        'email': user_data['email'],
        'name': user_data['name'],
        'provider': user_data.get('provider', 'local'),
        'provider_id': user_data.get('provider_id'),
        'role': user_data.get('role', 'user'),
        'created_at': datetime.now().isoformat(),
        'last_login': None
    }
    
    if user_data.get('password'):
        new_user['password_hash'] = hashlib.sha256(user_data['password'].encode()).hexdigest()
    
    users.append(new_user)
    save_users(users)
    
    # Remove sensitive data before returning
    user_response = new_user.copy()
    user_response.pop('password_hash', None)
    return user_response

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    users = load_users()
    user = next((u for u in users if u['email'] == email), None)
    if user:
        # Remove sensitive data
        user_response = user.copy()
        user_response.pop('password_hash', None)
        return user_response
    return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        # Remove sensitive data
        user_response = user.copy()
        user_response.pop('password_hash', None)
        return user_response
    return None

def login_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password"""
    users = load_users()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    user = next((u for u in users if u['email'] == email and u.get('password_hash') == password_hash), None)
    
    if user:
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        save_users(users)
        
        # Remove sensitive data
        user_response = user.copy()
        user_response.pop('password_hash', None)
        return user_response
    
    return None

def get_all_users() -> List[Dict[str, Any]]:
    """Get all users (admin only)"""
    users = load_users()
    # Remove sensitive data
    return [{k: v for k, v in user.items() if k != 'password_hash'} for user in users]

def verify_admin(token: str) -> bool:
    """Verify if user has admin privileges"""
    # In a real implementation, you'd decode the JWT token
    # For now, we'll do a simple check
    if not token:
        return False
    
    # Extract user info from token (simplified)
    # In production, use proper JWT verification
    return True  # For demo purposes

def update_user_last_login(user_id: str):
    """Update user's last login time"""
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            user['last_login'] = datetime.now().isoformat()
            break
    save_users(users)

def get_user_analytics() -> Dict[str, Any]:
    """Get user analytics for admin dashboard"""
    users = load_users()
    
    total_users = len(users)
    admin_users = len([u for u in users if u.get('role') == 'admin'])
    regular_users = total_users - admin_users
    
    # OAuth providers breakdown
    google_users = len([u for u in users if u.get('provider') == 'google'])
    microsoft_users = len([u for u in users if u.get('provider') == 'microsoft'])
    local_users = len([u for u in users if u.get('provider') == 'local'])
    
    # Recent signups (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_signups = len([
        u for u in users 
        if u.get('created_at') and datetime.fromisoformat(u['created_at']) > thirty_days_ago
    ])
    
    return {
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'oauth_breakdown': {
            'google': google_users,
            'microsoft': microsoft_users,
            'local': local_users
        },
        'recent_signups': recent_signups
    }
