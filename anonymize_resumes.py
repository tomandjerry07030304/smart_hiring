"""
Apply anonymization to all existing candidate resumes in MongoDB
"""

from pymongo import MongoClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.utils.resume_parser import anonymize_text

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_hiring_db']

print("\n" + "="*60)
print("🔒 ANONYMIZING CANDIDATE RESUMES")
print("="*60)

candidates = list(db.candidates.find())
print(f"\n📊 Found {len(candidates)} candidates to anonymize\n")

updated_count = 0
for candidate in candidates:
    resume_text = candidate.get('resume_text', '')
    
    if not resume_text:
        print(f"⏭️  Skipping {candidate.get('name', 'Unknown')} - no resume text")
        continue
    
    # Apply anonymization
    anonymized = anonymize_text(resume_text)
    
    # Update database
    db.candidates.update_one(
        {'_id': candidate['_id']},
        {'$set': {'resume_anonymized': anonymized}}
    )
    
    updated_count += 1
    print(f"✅ {candidate.get('name', 'Unknown'):20s} - Anonymized {len(resume_text)} → {len(anonymized)} chars")

print("\n" + "="*60)
print(f"✅ Anonymized {updated_count}/{len(candidates)} resumes")
print("="*60 + "\n")
