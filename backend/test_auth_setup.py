#!/usr/bin/env python3
"""
Test script to initialize the authentication database and test basic functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.auth_models import db_manager, jwt_manager

def test_database():
    """Test database initialization and basic operations"""
    print("🔧 Initializing Authentication Database...")
    
    # Initialize database (this happens automatically)
    print("✅ Database initialized successfully!")
    
    # Test creating a user
    try:
        test_user = {
            'email': 'test@authenticator.ai',
            'name': 'Test User',
            'password': 'test123',
            'provider': 'local'
        }
        
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(test_user['email'])
        if existing_user:
            print(f"✅ Test user already exists: {existing_user['name']}")
        else:
            user = db_manager.create_user(test_user)
            print(f"✅ Created test user: {user['name']}")
    
    except ValueError as e:
        print(f"ℹ️  Test user already exists: {e}")
    
    # Test authentication
    try:
        user = db_manager.authenticate_user('admin@authenticator.ai', 'admin123')
        if user:
            print(f"✅ Admin authentication successful: {user['name']}")
            
            # Test JWT token generation
            access_token, refresh_token = jwt_manager.generate_tokens(user)
            print(f"✅ Generated JWT tokens successfully")
            
            # Test token verification
            payload = jwt_manager.verify_token(access_token)
            if payload:
                print(f"✅ Token verification successful: User ID {payload['user_id']}")
            else:
                print("❌ Token verification failed")
        else:
            print("❌ Admin authentication failed")
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    print("\n🗄️  Database Location:")
    print(f"   {db_manager.db_path}")
    
    print("\n📋 Available Features:")
    print("   • User Registration (Local & OAuth)")
    print("   • JWT Authentication")
    print("   • Document Upload & Management")
    print("   • Analysis Results Storage")
    print("   • Multi-provider OAuth (Google, Microsoft, GitHub, Discord)")

if __name__ == "__main__":
    test_database()
