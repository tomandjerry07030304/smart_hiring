"""
Database initialization script
Creates collections and indexes for optimal performance
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import Database

def init_database():
    """Initialize database with collections and indexes"""
    print("🔄 Initializing Smart Hiring Database...")
    
    # Connect to database
    db_instance = Database()
    db = db_instance.connect('development')
    
    # Create collections
    collections = [
        'users',
        'candidates',
        'jobs',
        'applications',
        'assessments',
        'assessment_responses',
        'interviews',
        'fairness_audits',
        'transparency_reports'
    ]
    
    existing_collections = db.list_collection_names()
    
    for collection_name in collections:
        if collection_name not in existing_collections:
            db.create_collection(collection_name)
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"⏭️  Collection exists: {collection_name}")
    
    # Create indexes for better performance
    print("\n🔄 Creating indexes...")
    
    # Users indexes
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    print("✅ Users indexes created")
    
    # Candidates indexes
    db.candidates.create_index("user_id", unique=True)
    db.candidates.create_index("skills")
    print("✅ Candidates indexes created")
    
    # Jobs indexes
    db.jobs.create_index("recruiter_id")
    db.jobs.create_index("status")
    db.jobs.create_index("posted_date")
    db.jobs.create_index([("title", "text"), ("description", "text")])
    print("✅ Jobs indexes created")
    
    # Applications indexes
    db.applications.create_index([("job_id", 1), ("candidate_id", 1)], unique=True)
    db.applications.create_index("job_id")
    db.applications.create_index("candidate_id")
    db.applications.create_index("status")
    db.applications.create_index("overall_score")
    print("✅ Applications indexes created")
    
    # Assessments indexes
    db.assessments.create_index("job_id")
    db.assessments.create_index("assessment_type")
    print("✅ Assessments indexes created")
    
    # Interviews indexes
    db.interviews.create_index("application_id")
    db.interviews.create_index("candidate_id")
    db.interviews.create_index("recruiter_id")
    db.interviews.create_index("scheduled_time")
    print("✅ Interviews indexes created")
    
    print("\n✅ Database initialization complete!")
    print(f"📊 Total collections: {len(collections)}")
    
    # Print database stats
    print("\n📈 Database Statistics:")
    for collection_name in collections:
        count = db[collection_name].count_documents({})
        print(f"  - {collection_name}: {count} documents")
    
    db_instance.close()

if __name__ == "__main__":
    init_database()
