"""
Quick Test Accounts Creator
Creates test accounts via direct MongoDB insertion (no auth required)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from bson import ObjectId

# Connect to MongoDB (same as app - no auth for local development)
MONGO_URI = "mongodb://localhost:27017/"

try:
    client = MongoClient(MONGO_URI)
    db = client['smart_hiring_db']
    users = db['users']
    
    print("\n🔐 Creating Test Accounts...")
    print("=" * 60)
    
    test_accounts = [
        {
            'email': 'recruiter@test.com',
            'password': 'password123',
            'role': 'recruiter',
            'name': 'Test Recruiter',
            'company': 'Test Company Inc.'
        },
        {
            'email': 'candidate@test.com',
            'password': 'password123',
            'role': 'candidate',
            'name': 'Test Candidate',
            'skills': ['Python', 'JavaScript', 'React']
        },
        {
            'email': 'admin@test.com',
            'password': 'admin123',
            'role': 'admin',
            'name': 'System Admin',
            'company': 'Smart Hiring System'
        }
    ]
    
    created_count = 0
    for account in test_accounts:
        # Check if exists
        existing = users.find_one({'email': account['email']})
        if existing:
            print(f"⏭️  {account['email']} already exists")
            continue
        
        # Create user document
        user_doc = {
            '_id': ObjectId(),
            'email': account['email'],
            'password_hash': generate_password_hash(account['password']),
            'name': account['name'],
            'role': account['role'],
            'created_at': datetime.utcnow(),
            'is_active': True,
            'email_verified': True,
            'two_factor_enabled': False
        }
        
        # Add role-specific fields
        if account['role'] == 'recruiter':
            user_doc['company'] = account.get('company', '')
        elif account['role'] == 'candidate':
            user_doc['skills'] = account.get('skills', [])
            user_doc['resume_url'] = ''
        
        # Insert
        users.insert_one(user_doc)
        created_count += 1
        print(f"✅ Created: {account['email']} (password: {account['password']})")
    
    print("=" * 60)
    print(f"\n🎉 Test accounts ready! Created {created_count} new accounts")
    print("\n📝 LOGIN CREDENTIALS:")
    print("-" * 60)
    for account in test_accounts:
        print(f"Email: {account['email']}")
        print(f"Password: {account['password']}")
        print(f"Role: {account['role']}")
        print("-" * 60)
    
    print("\n🌐 Access your app at: http://localhost:5000")
    print("✅ All set! Use these credentials to login.\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Make sure:")
    print("  1. MongoDB is running")
    print("  2. The Flask app is running (it connects to MongoDB)")
    print("  3. MongoDB credentials in .env are correct")
