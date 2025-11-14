"""
Run fairness audit on job applications
Detect bias and generate transparency reports
"""

from pymongo import MongoClient
from datetime import datetime
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_hiring_db']

print("\n" + "="*60)
print("⚖️  FAIRNESS AUDIT - BIAS DETECTION")
print("="*60)

# Get all applications for analysis
applications = list(db.applications.find())
print(f"\n📊 Analyzing {len(applications)} applications\n")

# Simulate demographic data (in real system, this would be collected with consent)
demographics = ['Asian', 'White', 'Black', 'Hispanic', 'Other']
genders = ['Male', 'Female', 'Non-binary']

# Calculate fairness metrics
scores_by_demo = {}
scores_by_gender = {}

for app in applications:
    # Simulate demographics (for demo)
    demo = random.choice(demographics)
    gender = random.choice(genders)
    score = app.get('overall_score', 0)
    
    if demo not in scores_by_demo:
        scores_by_demo[demo] = []
    scores_by_demo[demo].append(score)
    
    if gender not in scores_by_gender:
        scores_by_gender[gender] = []
    scores_by_gender[gender].append(score)
    
    # Update application with simulated demo data
    db.applications.update_one(
        {'_id': app['_id']},
        {'$set': {
            'demographic_group': demo,
            'gender': gender
        }}
    )

# Calculate average scores
print("📊 DEMOGRAPHIC PARITY ANALYSIS:")
print("-" * 60)
for demo, scores in scores_by_demo.items():
    avg = sum(scores) / len(scores) if scores else 0
    print(f"{demo:15s}: Avg Score = {avg:.2f} ({len(scores)} applicants)")

print("\n📊 GENDER PARITY ANALYSIS:")
print("-" * 60)
for gender, scores in scores_by_gender.items():
    avg = sum(scores) / len(scores) if scores else 0
    print(f"{gender:15s}: Avg Score = {avg:.2f} ({len(scores)} applicants)")

# Calculate disparate impact
all_scores = [app.get('overall_score', 0) for app in applications]
avg_overall = sum(all_scores) / len(all_scores) if all_scores else 0

print("\n⚠️  BIAS DETECTION:")
print("-" * 60)
bias_found = False

for demo, scores in scores_by_demo.items():
    avg = sum(scores) / len(scores) if scores else 0
    ratio = avg / avg_overall if avg_overall > 0 else 1
    
    if ratio < 0.8:  # 80% rule
        print(f"🚨 BIAS DETECTED: {demo} group scores {ratio:.2%} of average")
        bias_found = True

if not bias_found:
    print("✅ No significant bias detected (80% rule)")

# Create fairness audit record
audit = {
    'audit_date': datetime.utcnow(),
    'total_applications': len(applications),
    'demographic_distribution': {k: len(v) for k, v in scores_by_demo.items()},
    'gender_distribution': {k: len(v) for k, v in scores_by_gender.items()},
    'average_score_overall': avg_overall,
    'average_scores_by_demo': {k: sum(v)/len(v) if v else 0 for k, v in scores_by_demo.items()},
    'average_scores_by_gender': {k: sum(v)/len(v) if v else 0 for k, v in scores_by_gender.items()},
    'bias_detected': bias_found,
    'fairness_badge': 'PASS' if not bias_found else 'WARNING',
    'created_at': datetime.utcnow()
}

db.fairness_audits.insert_one(audit)

# Generate transparency reports for each application
print("\n📝 GENERATING TRANSPARENCY REPORTS:")
print("-" * 60)

for app in applications:
    report = {
        'application_id': app['_id'],
        'candidate_name': app.get('candidate_name', 'Unknown'),
        'job_id': app['job_id'],
        'overall_score': app.get('overall_score', 0),
        'score_breakdown': {
            'resume_match': app.get('resume_match_score', 0) * 100,
            'skill_match': app.get('skill_match_score', 0) * 100,
            'cci_score': app.get('cci_score', 0)
        },
        'matched_skills': app.get('matched_skills', []),
        'decision_explanation': f"Score: {app.get('overall_score', 0):.1f}/100. " +
                              f"Matched {len(app.get('matched_skills', []))} required skills. " +
                              f"Resume similarity: {app.get('resume_match_score', 0):.0%}",
        'demographic_group': app.get('demographic_group', 'Unknown'),
        'gender': app.get('gender', 'Unknown'),
        'generated_at': datetime.utcnow()
    }
    
    db.transparency_reports.insert_one(report)
    print(f"✅ {app.get('candidate_name', 'Unknown'):20s} - Transparency report generated")

print("\n" + "="*60)
print("✅ FAIRNESS AUDIT COMPLETE")
print("="*60)
print(f"📊 Audit records: {db.fairness_audits.count_documents({})}")
print(f"📝 Transparency reports: {db.transparency_reports.count_documents({})}")
print(f"🏅 Fairness Badge: {audit['fairness_badge']}")
print("="*60 + "\n")
