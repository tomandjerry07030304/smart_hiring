"""
Seed database with sample data for testing
"""

import sys
import os
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import Database
from backend.models.user import User, Candidate
from backend.models.job import Job

bcrypt = Bcrypt()

def seed_database():
    """Seed database with sample data"""
    print("🌱 Seeding database with sample data...")
    
    db_instance = Database()
    db = db_instance.connect('development')
    
    # Clear existing data (optional - comment out to keep existing data)
    # print("⚠️  Clearing existing data...")
    # for collection in ['users', 'candidates', 'jobs']:
    #     db[collection].delete_many({})
    
    # Create sample users
    print("\n👥 Creating sample users...")
    
    users_data = [
        {
            'email': 'recruiter@techcorp.com',
            'password': 'recruiter123',
            'full_name': 'Alice Recruiter',
            'role': 'recruiter',
            'phone': '+1234567890'
        },
        {
            'email': 'candidate1@example.com',
            'password': 'candidate123',
            'full_name': 'Bob Developer',
            'role': 'candidate',
            'phone': '+1234567891'
        },
        {
            'email': 'candidate2@example.com',
            'password': 'candidate123',
            'full_name': 'Carol Engineer',
            'role': 'candidate',
            'phone': '+1234567892'
        }
    ]
    
    user_ids = {}
    for user_data in users_data:
        # Check if user exists
        existing = db.users.find_one({'email': user_data['email']})
        if existing:
            print(f"⏭️  User exists: {user_data['email']}")
            user_ids[user_data['role'] + '_' + user_data['email']] = str(existing['_id'])
            continue
        
        password_hash = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        
        user = User(
            email=user_data['email'],
            password_hash=password_hash,
            role=user_data['role'],
            full_name=user_data['full_name'],
            phone=user_data['phone']
        )
        
        result = db.users.insert_one(user.to_dict())
        user_id = str(result.inserted_id)
        user_ids[user_data['role'] + '_' + user_data['email']] = user_id
        
        print(f"✅ Created user: {user_data['email']} ({user_data['role']})")
        
        # Create candidate profile for candidates
        if user_data['role'] == 'candidate':
            candidate = Candidate(
                user_id=user_id,
                skills=['python', 'javascript', 'sql', 'react', 'node'],
                total_experience_years=3
            )
            db.candidates.insert_one(candidate.to_dict())
            print(f"   ✅ Created candidate profile for {user_data['email']}")
    
    # Create sample jobs
    print("\n💼 Creating sample jobs...")
    
    recruiter_id = user_ids.get('recruiter_recruiter@techcorp.com')
    
    if recruiter_id:
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer with strong backend skills. Must have experience with Django/Flask, REST APIs, and databases.',
                'company_name': 'Tech Corp',
                'location': 'Remote',
                'job_type': 'Full-time',
                'required_skills': ['python', 'django', 'rest api', 'postgresql', 'docker'],
                'experience_required': 3,
                'salary_range': {'min': 80000, 'max': 120000, 'currency': 'USD'}
            },
            {
                'title': 'Frontend React Developer',
                'description': 'Seeking a talented React developer to build amazing user interfaces. Experience with React, Redux, and modern JavaScript required.',
                'company_name': 'Tech Corp',
                'location': 'New York',
                'job_type': 'Full-time',
                'required_skills': ['react', 'javascript', 'typescript', 'html', 'css', 'redux'],
                'experience_required': 2,
                'salary_range': {'min': 70000, 'max': 100000, 'currency': 'USD'}
            },
            {
                'title': 'Data Scientist',
                'description': 'Looking for a data scientist with machine learning experience. Must be proficient in Python, pandas, scikit-learn, and have experience with ML models.',
                'company_name': 'Tech Corp',
                'location': 'Remote',
                'job_type': 'Full-time',
                'required_skills': ['python', 'machine learning', 'pandas', 'numpy', 'scikit-learn', 'tensorflow'],
                'experience_required': 4,
                'salary_range': {'min': 90000, 'max': 140000, 'currency': 'USD'}
            }
        ]
        
        for job_data in jobs_data:
            job = Job(
                title=job_data['title'],
                description=job_data['description'],
                recruiter_id=recruiter_id,
                company_name=job_data['company_name'],
                location=job_data['location'],
                job_type=job_data['job_type'],
                required_skills=job_data['required_skills'],
                experience_required=job_data['experience_required'],
                salary_range=job_data['salary_range']
            )
            
            result = db.jobs.insert_one(job.to_dict())
            print(f"✅ Created job: {job_data['title']}")
    
    print("\n✅ Database seeding complete!")
    print("\n📋 Sample Credentials:")
    print("  Recruiter:")
    print("    Email: recruiter@techcorp.com")
    print("    Password: recruiter123")
    print("  Candidate 1:")
    print("    Email: candidate1@example.com")
    print("    Password: candidate123")
    print("  Candidate 2:")
    print("    Email: candidate2@example.com")
    print("    Password: candidate123")
    
    db_instance.close()

if __name__ == "__main__":
    seed_database()
