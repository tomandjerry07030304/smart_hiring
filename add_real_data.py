"""
Simple script to add real data to Smart Hiring System MongoDB
Run this to add your own candidates, jobs, and applications
"""

from pymongo import MongoClient
from datetime import datetime
import bcrypt

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_hiring_db']

def hash_password(password):
    """Hash a password for storing"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def add_recruiter(email, password, name, company):
    """Add a recruiter user"""
    user_data = {
        'email': email,
        'password': hash_password(password),
        'name': name,
        'role': 'recruiter',
        'company': company,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Check if user already exists
    existing = db.users.find_one({'email': email})
    if existing:
        print(f"❌ User {email} already exists!")
        return None
    
    result = db.users.insert_one(user_data)
    print(f"✅ Recruiter added: {name} ({email})")
    return str(result.inserted_id)

def add_candidate(email, password, name, phone, skills):
    """Add a candidate user"""
    user_data = {
        'email': email,
        'password': hash_password(password),
        'name': name,
        'role': 'candidate',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    candidate_data = {
        'email': email,
        'name': name,
        'phone': phone,
        'skills': skills,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Check if user already exists
    existing = db.users.find_one({'email': email})
    if existing:
        print(f"❌ User {email} already exists!")
        return None
    
    db.users.insert_one(user_data)
    result = db.candidates.insert_one(candidate_data)
    print(f"✅ Candidate added: {name} ({email})")
    return str(result.inserted_id)

def add_job(title, company, description, required_skills, salary_min, salary_max, posted_by_email):
    """Add a job posting"""
    # Get recruiter info
    recruiter = db.users.find_one({'email': posted_by_email, 'role': 'recruiter'})
    if not recruiter:
        print(f"❌ Recruiter {posted_by_email} not found!")
        return None
    
    job_data = {
        'title': title,
        'company': company,
        'description': description,
        'required_skills': required_skills,
        'salary_range': {
            'min': salary_min,
            'max': salary_max,
            'currency': 'USD'
        },
        'posted_by': posted_by_email,
        'status': 'active',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = db.jobs.insert_one(job_data)
    print(f"✅ Job posted: {title} at {company}")
    return str(result.inserted_id)

def list_all_data():
    """List all data in the database"""
    print("\n" + "="*60)
    print("📊 DATABASE CONTENTS")
    print("="*60)
    
    print(f"\n👥 Users: {db.users.count_documents({})}")
    for user in db.users.find():
        name = user.get('name', 'N/A')
        print(f"   - {name} ({user['email']}) - Role: {user['role']}")
    
    print(f"\n👨‍💼 Candidates: {db.candidates.count_documents({})}")
    for candidate in db.candidates.find():
        name = candidate.get('name', 'N/A')
        print(f"   - {name} - Skills: {', '.join(candidate.get('skills', []))}")
    
    print(f"\n💼 Jobs: {db.jobs.count_documents({})}")
    for job in db.jobs.find():
        company = job.get('company', 'N/A')
        print(f"   - {job['title']} at {company}")
    
    print(f"\n📝 Applications: {db.applications.count_documents({})}")
    for app in db.applications.find():
        print(f"   - Application ID: {app['_id']}")
    
    print("\n" + "="*60)

# Example usage
if __name__ == '__main__':
    print("\n🚀 Smart Hiring System - Add Real Data")
    print("="*60)
    
    # Example: Add a recruiter
    add_recruiter(
        email='john.doe@company.com',
        password='password123',
        name='John Doe',
        company='Tech Corp'
    )
    
    # Example: Add a candidate
    add_candidate(
        email='jane.smith@email.com',
        password='password123',
        name='Jane Smith',
        phone='+1234567890',
        skills=['Python', 'Machine Learning', 'Flask', 'MongoDB']
    )
    
    # Example: Add a job
    add_job(
        title='Senior Python Developer',
        company='Tech Corp',
        description='We are looking for an experienced Python developer...',
        required_skills=['Python', 'Flask', 'MongoDB', 'REST APIs'],
        salary_min=80000,
        salary_max=120000,
        posted_by_email='john.doe@company.com'
    )
    
    # List all data
    list_all_data()
    
    print("\n✅ Done! You can now customize this script to add your own data.")
    print("To add more data, modify the examples above or call the functions directly.\n")
