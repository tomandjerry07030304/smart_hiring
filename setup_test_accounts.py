"""
Setup Test Accounts for Smart Hiring System
============================================
Creates properly formatted test accounts for all roles.
Compatible with the authentication system's expected schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime
from bson import ObjectId

# Initialize bcrypt (same as app uses)
bcrypt = Bcrypt()

# MongoDB connection
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

def create_test_accounts():
    """Create test accounts with proper schema"""
    try:
        client = MongoClient(MONGO_URI)
        db = client['smart_hiring_db']
        users = db['users']
        
        print("\n🔐 Smart Hiring System - Test Account Setup")
        print("=" * 60)
        
        # Test accounts matching expected schema
        test_accounts = [
            {
                'email': 'admin@smarthiring.com',
                'password': 'Admin@123',
                'full_name': 'System Administrator',
                'role': 'admin',
                'company_name': 'Smart Hiring System'
            },
            {
                'email': 'admin@test.com',
                'password': 'admin123',
                'full_name': 'Test Admin',
                'role': 'admin',
                'company_name': 'Test Organization'
            },
            {
                'email': 'recruiter@test.com',
                'password': 'password123',
                'full_name': 'Test Recruiter',
                'role': 'recruiter',
                'company_name': 'Test Company Inc.'
            },
            {
                'email': 'company@test.com',
                'password': 'password123',
                'full_name': 'Company Manager',
                'role': 'recruiter',  # Note: 'company' role is treated as 'recruiter'
                'company_name': 'TechCorp Solutions'
            },
            {
                'email': 'candidate@test.com',
                'password': 'password123',
                'full_name': 'Test Candidate',
                'role': 'candidate',
                'skills': ['Python', 'JavaScript', 'React', 'SQL', 'Docker']
            },
            {
                'email': 'john.doe@example.com',
                'password': 'password123',
                'full_name': 'John Doe',
                'role': 'candidate',
                'skills': ['Java', 'Spring Boot', 'AWS', 'MongoDB']
            }
        ]
        
        created = 0
        updated = 0
        
        for account in test_accounts:
            existing = users.find_one({'email': account['email']})
            
            # Generate password hash using bcrypt (same as Flask-Bcrypt)
            password_hash = bcrypt.generate_password_hash(account['password']).decode('utf-8')
            
            user_doc = {
                'email': account['email'],
                'password_hash': password_hash,
                'full_name': account['full_name'],
                'role': account['role'],
                'is_active': True,
                'email_verified': True,
                'profile_completed': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Add role-specific fields
            if account['role'] == 'recruiter':
                user_doc['company_name'] = account.get('company_name', '')
            elif account['role'] == 'candidate':
                user_doc['skills'] = account.get('skills', [])
                user_doc['experience_years'] = 3
                user_doc['education'] = 'Bachelor\'s Degree'
            elif account['role'] == 'admin':
                user_doc['company_name'] = account.get('company_name', 'Smart Hiring System')
                user_doc['is_super_admin'] = True
            
            if existing:
                # Update existing account with proper schema
                users.update_one(
                    {'_id': existing['_id']},
                    {'$set': user_doc}
                )
                print(f"🔄 Updated: {account['email']} (pass: {account['password']})")
                updated += 1
            else:
                user_doc['_id'] = ObjectId()
                users.insert_one(user_doc)
                print(f"✅ Created: {account['email']} (pass: {account['password']})")
                created += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Summary: {created} created, {updated} updated")
        print("\n🎯 Quick Login Credentials:")
        print("-" * 40)
        print("Admin Portal:     admin@smarthiring.com / Admin@123")
        print("Company Portal:   recruiter@test.com / password123")
        print("Candidate Portal: candidate@test.com / password123")
        print("-" * 40)
        print("\n✅ Test accounts ready! You can now login.")
        
        # Verify accounts
        print("\n🔍 Verification:")
        for acc in ['admin@smarthiring.com', 'recruiter@test.com', 'candidate@test.com']:
            user = users.find_one({'email': acc})
            if user:
                print(f"   ✓ {acc}: role={user.get('role')}, active={user.get('is_active')}")
            else:
                print(f"   ✗ {acc}: NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    create_test_accounts()
