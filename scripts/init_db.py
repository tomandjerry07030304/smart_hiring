"""
Database Initialization Script
Creates admin user and sets up initial database structure
Run this script after first installation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from backend.backend_config import config
import bcrypt
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user(mongo_db):
    """Create default admin user"""
    users_collection = mongo_db['users']
    
    # Check if admin already exists
    existing_admin = users_collection.find_one({'email': 'admin@smarthiring.com'})
    
    if existing_admin:
        logger.info("✓ Admin user already exists")
        return existing_admin
    
    # Hash password
    hashed_password = bcrypt.hashpw(
        config.ADMIN_PASSWORD.encode('utf-8'),
        bcrypt.gensalt()
    )
    
    # Create admin user
    admin_user = {
        'name': 'System Administrator',
        'email': 'admin@smarthiring.com',
        'password': hashed_password.decode('utf-8'),
        'role': 'admin',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'email_verified': True
    }
    
    result = users_collection.insert_one(admin_user)
    logger.info(f"✓ Admin user created with ID: {result.inserted_id}")
    logger.info(f"  Email: admin@smarthiring.com")
    logger.info(f"  Password: {config.ADMIN_PASSWORD}")
    logger.info("  ⚠️  Please change the admin password after first login!")
    
    return admin_user


def create_indexes(db):
    """Create database indexes for better performance"""
    logger.info("Creating database indexes...")
    
    # Users indexes
    users = db.get_collection('users')
    users.create_index('email', unique=True)
    users.create_index('role')
    logger.info("  ✓ Users indexes created")
    
    # Candidates indexes
    candidates = db.get_collection('candidates')
    candidates.create_index('user_id')
    candidates.create_index('email')
    candidates.create_index('skills')
    logger.info("  ✓ Candidates indexes created")
    
    # Jobs indexes
    jobs = db.get_collection('jobs')
    jobs.create_index('title')
    jobs.create_index('status')
    jobs.create_index('created_by')
    jobs.create_index('created_at')
    logger.info("  ✓ Jobs indexes created")
    
    # Applications indexes
    applications = db.get_collection('applications')
    applications.create_index('job_id')
    applications.create_index('candidate_id')
    applications.create_index('user_id')
    applications.create_index('status')
    applications.create_index([('job_id', 1), ('candidate_id', 1)], unique=True)
    logger.info("  ✓ Applications indexes created")
    
    # Assessments indexes
    assessments = db.get_collection('assessments')
    assessments.create_index('type')
    assessments.create_index('job_id')
    logger.info("  ✓ Assessments indexes created")


def create_collections(db):
    """Create necessary collections if they don't exist"""
    required_collections = [
        'users',
        'candidates',
        'jobs',
        'applications',
        'assessments',
        'fairness_audits',
        'transparency_reports',
        'notifications'
    ]
    
    existing_collections = db.list_collection_names()
    
    for collection_name in required_collections:
        if collection_name not in existing_collections:
            db.db.create_collection(collection_name)
            logger.info(f"  ✓ Created collection: {collection_name}")
        else:
            logger.info(f"  ○ Collection exists: {collection_name}")


def initialize_settings(db):
    """Initialize system settings"""
    settings_collection = db.get_collection('settings')
    
    default_settings = {
        'app_version': config.APP_VERSION,
        'initialized_at': datetime.utcnow(),
        'features': {
            'email_notifications': config.ENABLE_EMAIL_NOTIFICATIONS,
            'fairness_audit': config.ENABLE_FAIRNESS_AUDIT,
            'resume_anonymization': config.ENABLE_RESUME_ANONYMIZATION,
            'ml_features': config.ENABLE_ML_FEATURES
        },
        'limits': {
            'max_upload_size': config.MAX_UPLOAD_SIZE,
            'rate_limit_per_minute': config.RATE_LIMIT_PER_MINUTE
        },
        'updated_at': datetime.utcnow()
    }
    
    existing_settings = settings_collection.find_one()
    if not existing_settings:
        settings_collection.insert_one(default_settings)
        logger.info("✓ System settings initialized")
    else:
        logger.info("✓ System settings already exist")


def main():
    """Main initialization function"""
    logger.info("="*60)
    logger.info("Smart Hiring System - Database Initialization")
    logger.info("="*60)
    logger.info("")
    
    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        logger.info(f"URI: {config.MONGODB_URI.split('@')[1] if '@' in config.MONGODB_URI else config.MONGODB_URI}")
        
        client = MongoClient(config.MONGODB_URI)
        mongo_db = client[config.DB_NAME]
        logger.info(f"✅ Connected to MongoDB: {config.DB_NAME}")
        logger.info("✓ Connected to MongoDB")
        logger.info("")
        
        # Create collections
        logger.info("Setting up collections...")
        create_collections(mongo_db)
        logger.info("")
        
        # Create indexes
        logger.info("Creating indexes...")
        create_indexes(mongo_db)
        logger.info("")
        
        # Create admin user
        logger.info("Creating admin user...")
        create_admin_user(mongo_db)
        logger.info("")
        
        # Initialize settings
        logger.info("Initializing settings...")
        initialize_settings(mongo_db)
        logger.info("")
        
        logger.info("="*60)
        logger.info("✅ Database initialization completed successfully!")
        logger.info("="*60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Login with: admin@smarthiring.com")
        logger.info(f"2. Password: {config.ADMIN_PASSWORD}")
        logger.info("3. Change admin password immediately")
        logger.info("4. Run seed_db.py to load sample data (optional)")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
