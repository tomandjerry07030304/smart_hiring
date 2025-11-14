"""
Bulk Upload Resumes to MongoDB
This script processes all resumes in the smart_hiring_resumes folder
and uploads them to MongoDB as candidate profiles
"""

import os
import sys
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
import bcrypt

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import resume parser
try:
    from backend.utils.resume_parser import extract_text_from_file
    print("✅ Successfully imported resume parser")
except ImportError:
    print("⚠️ Could not import resume_parser, using simple extraction")
    
    def extract_text_from_file(file_path):
        """Simple text extraction fallback"""
        from docx import Document
        try:
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_hiring_db']

def hash_password(password):
    """Hash a password for storing"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def extract_basic_info(resume_text, filename):
    """Extract basic information from resume text"""
    # Simple extraction - you can enhance this
    lines = resume_text.split('\n')
    name = None
    email = None
    phone = None
    
    # Look for common patterns
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if not name and len(line) > 0 and len(line.split()) <= 4:
            # First non-empty short line is likely the name
            if not any(char.isdigit() for char in line) and '@' not in line:
                name = line
        
        # Look for email
        if '@' in line and not email:
            import re
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
            if email_match:
                email = email_match.group()
        
        # Look for phone
        if not phone:
            import re
            phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', line)
            if phone_match:
                phone = phone_match.group()
    
    # Fallback values
    if not name:
        name = filename.replace('.docx', '').replace('.pdf', '').replace('_', ' ').title()
    if not email:
        email = f"{filename.replace('.docx', '').replace('.pdf', '').lower()}@example.com"
    if not phone:
        phone = "+1234567890"
    
    return name, email, phone

def extract_skills(resume_text):
    """Extract skills from resume text"""
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring Boot',
        'MongoDB', 'MySQL', 'PostgreSQL', 'Redis', 'SQL', 'NoSQL',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
        'Machine Learning', 'Deep Learning', 'AI', 'Data Science', 'NLP',
        'HTML', 'CSS', 'REST API', 'GraphQL', 'Microservices',
        'Agile', 'Scrum', 'CI/CD', 'DevOps', 'TDD',
        'Communication', 'Leadership', 'Problem Solving', 'Team Work'
    ]
    
    found_skills = []
    resume_lower = resume_text.lower()
    
    for skill in common_skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill)
    
    return found_skills if found_skills else ['General Skills']

def upload_resume(file_path, default_password='candidate123'):
    """Upload a single resume to MongoDB"""
    filename = os.path.basename(file_path)
    print(f"\n📄 Processing: {filename}")
    
    try:
        # Read file as binary
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Extract text from resume
        resume_text = extract_text_from_file(file_data, filename)
        
        if not resume_text or len(resume_text.strip()) < 50:
            print(f"   ⚠️ Could not extract meaningful text from {filename}")
            return False
        
        print(f"   ✅ Extracted {len(resume_text)} characters")
        
        # Extract basic information
        name, email, phone = extract_basic_info(resume_text, filename)
        skills = extract_skills(resume_text)
        
        print(f"   👤 Name: {name}")
        print(f"   📧 Email: {email}")
        print(f"   📱 Phone: {phone}")
        print(f"   🛠️ Skills: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
        
        # Check if candidate already exists
        existing = db.users.find_one({'email': email})
        if existing:
            print(f"   ⚠️ Candidate {email} already exists in database")
            return False
        
        # Create user account
        user_data = {
            'email': email,
            'password': hash_password(default_password),
            'name': name,
            'role': 'candidate',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Create candidate profile
        candidate_data = {
            'email': email,
            'name': name,
            'phone': phone,
            'resume_text': resume_text,
            'resume_file': filename,
            'skills': skills,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert into database
        user_result = db.users.insert_one(user_data)
        user_id = user_result.inserted_id
        
        # Add user_id to candidate data
        candidate_data['user_id'] = user_id
        db.candidates.insert_one(candidate_data)
        
        print(f"   ✅ Successfully uploaded to MongoDB")
        return True
        
    except Exception as e:
        print(f"   ❌ Error processing {filename}: {str(e)}")
        return False

def bulk_upload_resumes(folder_path='smart_hiring_resumes'):
    """Upload all resumes from a folder"""
    print("\n" + "="*60)
    print("🚀 BULK RESUME UPLOAD TO MONGODB")
    print("="*60)
    
    # Get all resume files
    resume_files = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder '{folder_path}' not found!")
        return
    
    for ext in ['.pdf', '.docx', '.doc', '.txt']:
        resume_files.extend(folder.glob(f'*{ext}'))
    
    if not resume_files:
        print(f"❌ No resume files found in '{folder_path}'")
        return
    
    print(f"\n📁 Found {len(resume_files)} resume files")
    print(f"📂 Folder: {folder_path}")
    print(f"🔑 Default password for all candidates: 'candidate123'")
    print("\n" + "-"*60)
    
    # Upload each resume
    success_count = 0
    failed_count = 0
    
    for resume_file in resume_files:
        if upload_resume(str(resume_file)):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 UPLOAD SUMMARY")
    print("="*60)
    print(f"✅ Successfully uploaded: {success_count}")
    print(f"⚠️ Failed/Skipped: {failed_count}")
    print(f"📝 Total processed: {len(resume_files)}")
    
    # Show database stats
    print("\n" + "="*60)
    print("💾 DATABASE STATISTICS")
    print("="*60)
    print(f"👥 Total Users: {db.users.count_documents({})}")
    print(f"👨‍💼 Total Candidates: {db.candidates.count_documents({})}")
    print(f"💼 Total Jobs: {db.jobs.count_documents({})}")
    print(f"📝 Total Applications: {db.applications.count_documents({})}")
    print("="*60 + "\n")
    
    print("✅ Done! Your resumes are now in MongoDB.")
    print("🔐 All candidates can login with password: 'candidate123'")
    print("\n💡 You can now view them in MongoDB Compass or via the API\n")

if __name__ == '__main__':
    # Run bulk upload
    bulk_upload_resumes('smart_hiring_resumes')
