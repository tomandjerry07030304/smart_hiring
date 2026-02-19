"""
Seed a test video interview session for browser testing.
Run: python seed_test_interview.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models.database import get_db
from backend.services.video_interview_service import create_interview_session
from backend.services.ai_interviewer_service_v2 import generate_interview_questions
from bson import ObjectId
from datetime import datetime

db = get_db()

# Find or create a test job
job = db['jobs'].find_one()
if not job:
    result = db['jobs'].insert_one({
        'title': 'Software Developer',
        'company': 'Acme Tech',
        'description': 'Looking for a Python/Flask developer with REST API experience.',
        'skills': ['Python', 'Flask', 'REST APIs', 'MongoDB'],
        'experience_required': '2+ years',
        'created_at': datetime.utcnow(),
        'status': 'active'
    })
    job = db['jobs'].find_one({'_id': result.inserted_id})
    jid = str(job['_id'])
    print(f'Created test job: {jid}')
else:
    jid = str(job['_id'])
    jtitle = job.get('title', 'N/A')
    print(f'Using existing job: {jid} - {jtitle}')

# Find or create a test candidate user
candidate = db['users'].find_one({'role': 'candidate'})
if not candidate:
    result = db['users'].insert_one({
        'full_name': 'Test Candidate',
        'email': 'candidate@test.com',
        'role': 'candidate',
        'created_at': datetime.utcnow()
    })
    candidate = db['users'].find_one({'_id': result.inserted_id})
    cid = str(candidate['_id'])
    print(f'Created test candidate: {cid}')
else:
    cid = str(candidate['_id'])
    cname = candidate.get('full_name', candidate.get('name', 'N/A'))
    print(f'Using existing candidate: {cid} - {cname}')

# Find or create a scheduler user (company/admin)
scheduler = db['users'].find_one({'role': {'$in': ['company', 'admin']}})
if not scheduler:
    result = db['users'].insert_one({
        'full_name': 'Test Recruiter',
        'email': 'recruiter@test.com',
        'role': 'company',
        'created_at': datetime.utcnow()
    })
    scheduler = db['users'].find_one({'_id': result.inserted_id})
    sid = str(scheduler['_id'])
    print(f'Created test scheduler: {sid}')
else:
    sid = str(scheduler['_id'])
    sname = scheduler.get('full_name', scheduler.get('name', 'N/A'))
    print(f'Using existing scheduler: {sid} - {sname}')

# Generate AI questions
print('Generating interview questions...')
questions = generate_interview_questions(
    job={
        'title': job.get('title', 'Developer'),
        'description': job.get('description', ''),
        'skills': job.get('skills', []),
    },
    num_questions=25,
    include_behavioral=True,
)
print(f'Generated {len(questions)} questions')

# Create interview session
session = create_interview_session(
    job_id=str(job['_id']),
    candidate_id=str(candidate['_id']),
    scheduled_by=str(scheduler['_id']),
    interview_type='ai_automated',
    duration_minutes=30,
    expiry_hours=48,
    questions=questions,
    base_url='http://localhost:5000',
)

session_id = str(session['_id'])
token = session['token']
link = session['meeting_link']
status = session['status']
q_count = len(session['questions'])
expires = str(session['expires_at'])

print()
print('=' * 60)
print(f'SESSION ID:    {session_id}')
print(f'TOKEN:         {token}')
print(f'MEETING LINK:  {link}')
print(f'STATUS:        {status}')
print(f'QUESTIONS:     {q_count}')
print(f'EXPIRES:       {expires}')
print('=' * 60)
print()
print(f'>>> Open in browser: {link}')
