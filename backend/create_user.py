#!/usr/bin/env python3
"""
Create a specific user account
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.auth_models import db_manager

def create_user_account():
    """Create user account with specified credentials"""
    print("🔧 Creating user account...")
    
    try:
        user_data = {
            'email': 'psaurabh6@gatech.edu',
            'name': 'Pratham Saurabh',
            'password': 'Moshis4*',
            'provider': 'local',
            'is_verified': True
        }
        
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(user_data['email'])
        if existing_user:
            print(f"✅ User already exists: {existing_user['name']} ({existing_user['email']})")
            return existing_user
        else:
            user = db_manager.create_user(user_data)
            print(f"✅ Created user account: {user['name']} ({user['email']})")
            return user
    
    except ValueError as e:
        print(f"❌ Error creating user: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    user = create_user_account()
    if user:
        print(f"\n🎉 Account ready!")
        print(f"   Email: psaurabh6@gatech.edu")
        print(f"   Password: Moshis4*")
        print(f"   Name: {user['name']}")
        print(f"   User ID: {user['id']}")
        print(f"\n📍 You can now login with these credentials!")
    else:
        print("❌ Failed to create account")
