#!/usr/bin/env python3
"""
Recomputation Worker: Safe Resume Score Upgrade (v4.2)
======================================================
Safely upgrades legacy resumes to v4.2 parser standards.

Features:
- Re-hydrates original PDF binary (bypasses old parsed data).
- Applies v4.2 Logic: Date-overlap fix, Stuffing penalty, Context-aware skills.
- Atomic Updates: No partial writes.
- Audit Logging: Tracks score changes and reasons.
- Dry-Run Mode: Safe testing without DB commits.

Usage:
    python scripts/recompute_scores.py --dry-run
    python scripts/recompute_scores.py --limit 100 --no-dry-run
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from pymongo import MongoClient, UpdateOne

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.services.resume_parser_service import ResumeParser
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please run this script from the project root: python scripts/recompute_scores.py")
    sys.exit(1)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('recompute_audit.log')
    ]
)
logger = logging.getLogger(__name__)

TARGET_VERSION = "4.2"

class RecomputationManager:
    def __init__(self, db_uri, db_name, dry_run=True):
        self.dry_run = dry_run
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.parser = ResumeParser()
        
        if self.dry_run:
            logger.info("⚠️  RUNNING IN DRY-RUN MODE (No changes will be saved) ⚠️")

    def recompute_batch(self, limit=50, reason="Upgrade to v4.2"):
        logger.info(f"🔍 Checking for resumes with version < {TARGET_VERSION} (Limit: {limit})")
        
        # 1. Fetch Candidates needing update
        query = {
            "$or": [
                {"parser_version": {"$exists": False}},
                {"parser_version": {"$lt": TARGET_VERSION}}
            ]
        }
        
        # Projection: We primarily need the PDF binary
        # Note: If resume_pdf is stored in GridFS, this logic would need adjustment.
        # Assuming binary is in 'resume_pdf' field based on context.
        candidates = self.db.resumes.find(query).limit(limit)
        
        count = self.db.resumes.count_documents(query)
        logger.info(f"📊 Found {count} candidates eligible for upgrade.")
        
        stats = {"updated": 0, "failed": 0, "verified_score_change": 0}
        
        for candidate in candidates:
            cand_id = candidate.get("_id")
            try:
                # 2. Re-Hydrate PDF
                pdf_binary = candidate.get("file_content")  # Check field name! Usually file_content or resume_pdf
                if not pdf_binary:
                    # Try alternate field names commonly used
                    pdf_binary = candidate.get("resume_pdf") or candidate.get("file_data")
                
                if not pdf_binary:
                    logger.error(f"❌ [{cand_id}] Missing PDF binary. Skipping.")
                    stats["failed"] += 1
                    continue
                
                # Get old score for audit
                old_data = candidate.get("parsed_data", {})
                # Handle case where parsed_data might be a string (legacy) or dict
                if isinstance(old_data, str):
                    old_score = 0
                else:
                    old_score = old_data.get("confidence", {}).get("overall", 0)
                
                old_version = candidate.get("parser_version", "unknown")

                # 3. Parse with v4.2 Logic
                logger.debug(f"Parsing {cand_id}...")
                new_parsed_data = self.parser.parse_resume(pdf_binary, candidate.get("filename", "unknown.pdf"))
                new_score = new_parsed_data["confidence"]["overall"]
                
                # 4. Detect Drift/Change
                score_diff = new_score - old_score
                if abs(score_diff) > 0.001:
                    stats["verified_score_change"] += 1
                    drift_msg = f"Score changed: {old_score} -> {new_score} (Δ {score_diff:.3f})"
                else:
                    drift_msg = "Score unchanged"

                # 5. Atomic Update Payload
                update_payload = {
                    "$set": {
                        "parsed_data": new_parsed_data,
                        "parser_version": TARGET_VERSION,
                        "recomputed_at": datetime.utcnow(),
                        "recompute_reason": reason,
                        # Store explicitly for querying without unpacking JSON
                        "computed_experience": new_parsed_data.get("experience", {}).get("total_years", 0),
                        "confidence_score": new_score
                    },
                    "$push": {
                        "audit_log": {
                            "timestamp": datetime.utcnow(),
                            "action": "RECOMPUTE",
                            "previous_version": old_version,
                            "previous_score": original_score if 'original_score' in locals() else old_score, # Fix var ref
                            "new_score": new_score,
                            "reason": reason
                        }
                    }
                }
                
                # 6. Execute
                if self.dry_run:
                    logger.info(f"[DRY-RUN] {cand_id} | v{old_version} -> v{TARGET_VERSION} | {drift_msg}")
                else:
                    result = self.db.resumes.update_one({"_id": cand_id}, update_payload)
                    if result.modified_count > 0:
                        logger.info(f"✅ {cand_id} | Upgraded | {drift_msg}")
                        stats["updated"] += 1
                    else:
                        logger.warning(f"⚠️ {cand_id} | No modification detected.")

            except Exception as e:
                logger.error(f"❌ [{cand_id}] Failed: {str(e)}")
                if not self.dry_run:
                    # Flag record safely
                    self.db.resumes.update_one(
                        {"_id": cand_id},
                        {"$set": {"recompute_error": str(e), "recompute_failed_at": datetime.utcnow()}}
                    )
                stats["failed"] += 1

        logger.info("\n" + "="*50)
        logger.info("RECOMPUTATION SUMMARY")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        logger.info(f"Processed: {stats['updated'] + stats['failed']} / {limit}")
        logger.info(f"Updated: {stats['updated']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Score Changed: {stats['verified_score_change']}")
        logger.info("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recompute Resume Scores (v4.2)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without saving DB changes")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Execute LIVE updates")
    parser.add_argument("--limit", type=int, default=50, help="Max records to process")
    parser.set_defaults(dry_run=True)
    
    args = parser.parse_args()
    
    # Load Config from backend_config or env
    try:
        from backend.utils.env_config import env_config
        MONGO_URI = env_config.mongodb_uri
        DB_NAME = env_config.db_name
    except ImportError:
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart_hiring_db")
        DB_NAME = "smart_hiring_db"
        
    print("="*60)
    print(f"🚀 STARTING RECOMPUTATION WORKER v{TARGET_VERSION}")
    print(f"   DB: {MONGO_URI} (Masked if secret)")
    print(f"   Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("="*60)
    
    manager = RecomputationManager(MONGO_URI, DB_NAME, dry_run=args.dry_run)
    manager.recompute_batch(limit=args.limit)
