#!/usr/bin/env python3
"""
Rescore All Applications with Improved Matching (v4.3)
======================================================
Re-runs analyze_candidate() on all applications using the
updated fuzzy skill matching and TF-IDF calibration.

Usage:
    python scripts/rescore_applications.py             (dry-run, shows what would change)
    python scripts/rescore_applications.py --live      (actually updates DB)
"""
import os
import sys
import argparse
import io
from datetime import datetime

# Fix Windows Unicode encoding for emoji in console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from bson import ObjectId

# Import the improved matching service
from backend.services.ml_matching_service import analyze_candidate

def main():
    parser = argparse.ArgumentParser(description="Rescore all applications with improved matching")
    parser.add_argument("--live", action="store_true", help="Actually update the database (default: dry-run)")
    parser.add_argument("--limit", type=int, default=100, help="Max applications to process")
    parser.add_argument("--cleanup", action="store_true", help="Remove orphaned applications (missing candidate/job)")
    args = parser.parse_args()

    dry_run = not args.live
    cleanup = args.cleanup

    # Connect to MongoDB - Direct connection to avoid env_config DB_NAME mismatch bug
    # (env_config reads DB_NAME but .env sets MONGODB_DATABASE — different var names!)
    MONGO_URI = "mongodb://localhost:27017/smart_hiring_db"
    DB_NAME = "smart_hiring_db"

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print("=" * 60)
    print(f"  RESCORE APPLICATIONS v4.3 - {'DRY-RUN' if dry_run else 'LIVE UPDATE'}")
    print(f"  DB: {DB_NAME}")
    if cleanup:
        print("  MODE: Cleanup enabled (orphaned apps will be deleted)")
    print("=" * 60)

    applications = list(db['applications'].find().limit(args.limit))
    print(f"\n  Found {len(applications)} applications to rescore.\n")

    stats = {"updated": 0, "skipped": 0, "failed": 0, "improved": 0, "decreased": 0, "deleted": 0}

    for app in applications:
        app_id = app['_id']
        job_id = app.get('job_id')
        candidate_id = app.get('candidate_id')
        old_score = app.get('overall_score', 0)

        try:
            # Fetch job data
            job = db['jobs'].find_one({'_id': ObjectId(job_id)})
            if not job:
                print(f"  [SKIP] App {app_id} - Job {job_id} not found")
                if cleanup and not dry_run:
                    db['applications'].delete_one({'_id': app_id})
                    print(f"    -> DELETED orphaned application")
                    stats["deleted"] += 1
                stats["skipped"] += 1
                continue

            # Fetch candidate data
            candidate = db['candidates'].find_one({'user_id': candidate_id})
            if not candidate:
                print(f"  [SKIP] App {app_id} - Candidate {candidate_id} not found")
                if cleanup and not dry_run:
                    db['applications'].delete_one({'_id': app_id})
                    print(f"    -> DELETED orphaned application")
                    stats["deleted"] += 1
                stats["skipped"] += 1
                continue

            resume_text = candidate.get('anonymized_resume', '') or candidate.get('resume_text', '')
            if not resume_text:
                print(f"  [SKIP] App {app_id} - No resume text")
                if cleanup and not dry_run:
                    db['applications'].delete_one({'_id': app_id})
                    print(f"    -> DELETED orphaned application")
                    stats["deleted"] += 1
                stats["skipped"] += 1
                continue

            # Rescore with improved matching
            analysis = analyze_candidate(
                job_description=job.get('description', ''),
                job_skills=job.get('required_skills', []),
                resume_text=resume_text,
                resume_skills=candidate.get('skills', []),
                cci_score=candidate.get('cci_score')
            )

            new_score = analysis['overall_score']
            delta = new_score - old_score
            direction = "+" if delta > 0 else ""
            
            # Auto-shortlist logic
            new_status = app.get('status', 'pending')
            status_msg = ""
            if new_score >= 70 and new_status == 'pending':
                new_status = 'shortlisted'
                status_msg = " [AUTO-SHORTLIST]"

            # Get user info for display
            user = db['users'].find_one({'_id': ObjectId(candidate_id)})
            name = user.get('full_name', 'Unknown') if user else 'Unknown'
            job_title = job.get('title', 'Unknown')

            print(f"  {name:25s} | {job_title:30s} | {old_score:5.1f}% -> {new_score:5.1f}% ({direction}{delta:.1f}){status_msg}")
            print(f"    Matched: {analysis['matched_skills']}")

            if delta > 0:
                stats["improved"] += 1
            elif delta < 0:
                stats["decreased"] += 1

            # Update DB if live
            if not dry_run:
                update_data = {
                    'overall_score': new_score,
                    'resume_match_score': analysis['tfidf_score'],
                    'skill_match_score': analysis['skill_match'],
                    'matched_skills': analysis['matched_skills'],
                    'missing_skills': analysis.get('missing_skills', []),
                    'decision': analysis['decision'],
                    'rescored_at': datetime.utcnow(),
                    'rescore_reason': 'v4.3 fuzzy skill matching upgrade'
                }
                
                # Only update status if improved to shortlist range
                if new_status == 'shortlisted' and app.get('status') == 'pending':
                    update_data['status'] = 'shortlisted'
                    update_data['auto_status_reason'] = f"Auto-shortlisted during rescore (score: {new_score:.0f}%)"
                
                db['applications'].update_one(
                    {'_id': app_id},
                    {'$set': update_data}
                )

            stats["updated"] += 1

        except Exception as e:
            print(f"  [FAIL] App {app_id}: {e}")
            stats["failed"] += 1

    print("\n" + "=" * 60)
    print("  RESCORE SUMMARY")
    print(f"  Mode:      {'DRY-RUN (no changes saved)' if dry_run else 'LIVE (changes saved!)'}")
    print(f"  Processed: {stats['updated'] + stats['skipped'] + stats['failed']}")
    print(f"  Updated:   {stats['updated']}")
    print(f"  Improved:  {stats['improved']} (score went UP)")
    print(f"  Deleted:   {stats['deleted']} (orphaned apps)")
    print(f"  Skipped:   {stats['skipped']}")
    print(f"  Failed:    {stats['failed']}")
    print("=" * 60)

    if dry_run and stats['improved'] > 0:
        print("\n  Looks good! Run with --live to apply changes:")
        print("  python scripts/rescore_applications.py --live\n")
    if dry_run and stats['skipped'] > 0:
        print("\n  Tip: Run with --live --cleanup to remove orphaned applications")

if __name__ == "__main__":
    main()
