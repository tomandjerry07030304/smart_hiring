"""
Upgrade User Role Script
========================
Use this script to change a user's role in the database.
Useful when a user registered as 'candidate' but needs 'recruiter' access.

Usage:
    python upgrade_user_role.py <email> <new_role>
    
Examples:
    python upgrade_user_role.py techcorps030707@gmail.com recruiter
    python upgrade_user_role.py user@example.com candidate
    python upgrade_user_role.py admin@example.com admin
"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'smart_hiring_db'

def get_user(email):
    """Fetch user by email"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    user = db.users.find_one({'email': email})
    client.close()
    return user

def upgrade_role(email, new_role):
    """Change user's role"""
    valid_roles = ['candidate', 'recruiter', 'admin']
    
    if new_role not in valid_roles:
        print(f"❌ Invalid role: {new_role}")
        print(f"   Valid roles: {', '.join(valid_roles)}")
        return False
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Find user first
    user = db.users.find_one({'email': email})
    
    if not user:
        print(f"❌ User not found: {email}")
        client.close()
        return False
    
    old_role = user.get('role', 'unknown')
    
    if old_role == new_role:
        print(f"ℹ️ User already has role '{new_role}'. No changes made.")
        client.close()
        return True
    
    # Update the role
    result = db.users.update_one(
        {'email': email},
        {
            '$set': {
                'role': new_role,
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    if result.modified_count > 0:
        print(f"✅ SUCCESS: Role updated!")
        print(f"   Email: {email}")
        print(f"   Old Role: {old_role}")
        print(f"   New Role: {new_role}")
        print(f"\n🎉 User can now login via the {new_role.title()} portal!")
    else:
        print(f"❌ Failed to update role")
        client.close()
        return False
    
    client.close()
    return True

def list_users():
    """List all users and their roles"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users = db.users.find({}, {'email': 1, 'full_name': 1, 'role': 1, 'is_active': 1})
    
    print("\n📋 All Users in Database:")
    print("=" * 80)
    print(f"{'Email':<40} {'Name':<25} {'Role':<12} {'Active'}")
    print("-" * 80)
    
    count = 0
    for user in users:
        email = user.get('email', 'N/A')
        name = user.get('full_name', 'N/A')[:24]
        role = user.get('role', 'N/A')
        active = '✓' if user.get('is_active', False) else '✗'
        print(f"{email:<40} {name:<25} {role:<12} {active}")
        count += 1
    
    print("-" * 80)
    print(f"Total: {count} users")
    client.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nQuick Commands:")
        print("  python upgrade_user_role.py --list      # List all users")
        print("  python upgrade_user_role.py EMAIL ROLE  # Upgrade user role")
        return
    
    if sys.argv[1] == '--list':
        list_users()
        return
    
    if len(sys.argv) < 3:
        print("❌ Usage: python upgrade_user_role.py <email> <new_role>")
        print("   Example: python upgrade_user_role.py user@example.com recruiter")
        return
    
    email = sys.argv[1]
    new_role = sys.argv[2].lower()
    
    # Show current user info
    user = get_user(email)
    if user:
        print(f"\n📧 Found User: {email}")
        print(f"   Current Role: {user.get('role', 'unknown')}")
        print(f"   Name: {user.get('full_name', 'N/A')}")
        print(f"   Active: {'Yes' if user.get('is_active') else 'No'}")
        print()
    
    upgrade_role(email, new_role)

if __name__ == '__main__':
    main()
