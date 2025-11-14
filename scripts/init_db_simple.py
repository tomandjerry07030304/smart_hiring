"""
Simple Database Initialization Script
Creates admin user and sets up initial database structure
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient, ASCENDING, DESCENDING
from backend.backend_config import config
import bcrypt
from datetime import datetime

def main():
    print("="*60)
    print("Smart Hiring System - Database Initialization")
    print("="*60)
    print()
    
    try:
        # Connect to MongoDB
        print("Connecting to MongoDB...")
        client = MongoClient(config.MONGODB_URI)
        db = client[config.DB_NAME]
        print(f"✅ Connected to MongoDB: {config.DB_NAME}")
        print()
        
        # Create collections
        print("Setting up collections...")
        collections = ['users', 'candidates', 'jobs', 'applications', 'assessments', 
                      'fairness_audits', 'transparency_reports', 'notifications']
        
        existing = db.list_collection_names()
        for coll in collections:
            if coll not in existing:
                db.create_collection(coll)
                print(f"  ✓ Created: {coll}")
            else:
                print(f"  ○ Exists: {coll}")
        print()
        
        # Create indexes
        print("Creating indexes...")
        db.users.create_index([('email', ASCENDING)], unique=True)
        db.candidates.create_index([('email', ASCENDING)])
        db.jobs.create_index([('status', ASCENDING)])
        db.jobs.create_index([('created_at', DESCENDING)])
        db.applications.create_index([('job_id', ASCENDING)])
        db.applications.create_index([('candidate_id', ASCENDING)])
        print("  ✓ All indexes created")
        print()
        
        # Create admin user
        print("Creating admin user...")
        users = db.users
        
        admin_email = "admin@smarthiring.com"
        existing_admin = users.find_one({'email': admin_email})
        
        if existing_admin:
            print(f"  ○ Admin user already exists: {admin_email}")
        else:
            admin_password = config.ADMIN_PASSWORD if hasattr(config, 'ADMIN_PASSWORD') else 'Admin@123!'
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            
            admin_user = {
                'email': admin_email,
                'password': hashed_password.decode('utf-8'),
                'name': 'System Administrator',
                'role': 'admin',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'last_login': None
            }
            
            users.insert_one(admin_user)
            print(f"  ✓ Admin user created: {admin_email}")
            print(f"  ✓ Default password: {admin_password}")
            print("  ⚠️  IMPORTANT: Change password after first login!")
        print()
        
        # Initialize settings
        print("Initializing settings...")
        settings = db.settings
        
        if settings.count_documents({}) == 0:
            default_settings = {
                'app_name': 'Smart Hiring System',
                'version': '1.0.0',
                'anonymization_enabled': True,
                'ml_matching_enabled': True,
                'email_notifications_enabled': True,
                'audit_logs_enabled': True,
                'max_file_size_mb': 10,
                'allowed_file_types': ['pdf', 'doc', 'docx', 'txt'],
                'created_at': datetime.utcnow()
            }
            settings.insert_one(default_settings)
            print("  ✓ Default settings initialized")
        else:
            print("  ○ Settings already exist")
        print()
        
        print("="*60)
        print("✅ Database initialization completed successfully!")
        print("="*60)
        print()
        print("Next steps:")
        print(f"1. Login with: {admin_email}")
        print(f"2. Password: {config.ADMIN_PASSWORD if hasattr(config, 'ADMIN_PASSWORD') else 'Admin@123!'}")
        print("3. Change admin password immediately")
        print("4. Start the application: python backend/app.py")
        print()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
