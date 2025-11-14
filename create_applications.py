"""
Create job applications and run matching algorithm
This links candidates to jobs with scores
"""

from pymongo import MongoClient
from datetime import datetime
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import matching functions
from backend.utils.matching import compute_overall_score
from backend.utils.cci_calculator import calculate_career_consistency_index

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_hiring_db']

def create_applications_for_all_candidates():
    """Create applications for all candidates to all jobs"""
    
    print("\n" + "="*60)
    print("🚀 CREATING JOB APPLICATIONS")
    print("="*60)
    
    # Get all active jobs
    jobs = list(db.jobs.find({'status': 'active'}))
    candidates = list(db.candidates.find())
    
    if not jobs:
        print("❌ No active jobs found!")
        return
    
    if not candidates:
        print("❌ No candidates found!")
        return
    
    print(f"\n📊 Found {len(jobs)} jobs and {len(candidates)} candidates")
    print(f"📝 Will create up to {len(jobs) * len(candidates)} applications\n")
    
    created_count = 0
    skipped_count = 0
    
    # Take first job for demo (or loop through all)
    job = jobs[0]  # First job
    job_title = job.get('title', 'Unknown')
    required_skills = job.get('required_skills', [])
    
    print(f"📌 Job: {job_title}")
    print(f"🛠️  Required Skills: {', '.join(required_skills)}\n")
    print("-" * 60)
    
    for candidate in candidates:
        candidate_id = candidate.get('_id')
        candidate_email = candidate.get('email')
        candidate_name = candidate.get('name', 'Unknown')
        candidate_skills = candidate.get('skills', [])
        resume_text = candidate.get('resume_text', '')
        
        # Check if application already exists
        existing = db.applications.find_one({
            'candidate_id': candidate_id,
            'job_id': job['_id']
        })
        
        if existing:
            skipped_count += 1
            continue
        
        # Calculate scores
        try:
            # Simple skill matching
            matched_skills = [s for s in candidate_skills if s in required_skills]
            skill_match_score = len(matched_skills) / len(required_skills) if required_skills else 0
            
            # Resume similarity (simplified)
            resume_match_score = 0.5  # Placeholder - would use TF-IDF
            
            # CCI score (placeholder - needs work history)
            cci_score = 50  # Default
            
            # Overall score (weighted average)
            overall_score = (
                0.5 * resume_match_score * 100 +
                0.3 * skill_match_score * 100 +
                0.2 * cci_score
            )
            
            # Create application
            application = {
                'job_id': job['_id'],
                'candidate_id': candidate_id,
                'candidate_email': candidate_email,
                'candidate_name': candidate_name,
                'status': 'pending',
                'applied_at': datetime.utcnow(),
                'resume_match_score': resume_match_score,
                'skill_match_score': skill_match_score,
                'cci_score': cci_score,
                'overall_score': overall_score,
                'matched_skills': matched_skills,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            db.applications.insert_one(application)
            created_count += 1
            
            print(f"✅ {candidate_name:20s} | Score: {overall_score:5.1f} | Skills: {len(matched_skills)}/{len(required_skills)}")
            
        except Exception as e:
            print(f"❌ Error for {candidate_name}: {e}")
            continue
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"✅ Applications created: {created_count}")
    print(f"⏭️  Skipped (already exist): {skipped_count}")
    print(f"📝 Total in database: {db.applications.count_documents({})}")
    print("="*60 + "\n")

if __name__ == '__main__':
    create_applications_for_all_candidates()
    
    # Show top candidates
    print("\n🏆 TOP CANDIDATES:")
    print("-" * 60)
    top_apps = db.applications.find().sort('overall_score', -1).limit(5)
    
    for i, app in enumerate(top_apps, 1):
        print(f"{i}. {app['candidate_name']:20s} - Score: {app['overall_score']:.2f}")
    
    print("\n✅ Done! Applications are now in MongoDB.\n")
