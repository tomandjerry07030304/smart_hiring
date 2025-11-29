"""
Job Processor for Background Workers
Processes jobs from queues: resume parsing, analytics, emails
"""

import os
import sys
import time
import logging
from typing import Dict, Any
import threading

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.workers.queue_manager import queue_manager
from backend.models.database import Database

logger = logging.getLogger(__name__)


class JobProcessor:
    """Processes background jobs from Redis queues"""
    
    def __init__(self):
        """Initialize job processor"""
        self.running = False
        self.threads = []
        self.db = Database()
        self.db.connect(os.getenv('FLASK_ENV', 'development'))
    
    def start(self, num_workers: int = 2):
        """
        Start worker threads
        
        Args:
            num_workers: Number of worker threads to spawn
        """
        if self.running:
            logger.warning("⚠️ Workers already running")
            return
        
        self.running = True
        logger.info(f"🚀 Starting {num_workers} worker threads...")
        
        # Start worker threads
        for i in range(num_workers):
            thread = threading.Thread(
                target=self._worker_loop,
                args=(f"worker-{i+1}",),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        logger.info(f"✅ {num_workers} workers started")
    
    def stop(self):
        """Stop all workers"""
        logger.info("🛑 Stopping workers...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        self.threads = []
        logger.info("✅ All workers stopped")
    
    def _worker_loop(self, worker_name: str):
        """
        Main worker loop
        
        Args:
            worker_name: Name of this worker
        """
        logger.info(f"👷 {worker_name} started")
        
        queues = [
            queue_manager.RESUME_PARSING_QUEUE,
            queue_manager.EMAIL_QUEUE,
            queue_manager.ANALYTICS_QUEUE,
            queue_manager.ML_SCORING_QUEUE,
            queue_manager.AUDIT_QUEUE
        ]
        
        while self.running:
            try:
                # Try each queue
                job_processed = False
                
                for queue_name in queues:
                    job = queue_manager.dequeue_job(queue_name)
                    
                    if job:
                        logger.info(f"📦 {worker_name} processing job: {job['job_id']}")
                        self._process_job(job)
                        job_processed = True
                        break
                
                # Sleep if no job found
                if not job_processed:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ {worker_name} error: {e}")
                time.sleep(5)
        
        logger.info(f"👋 {worker_name} stopped")
    
    def _process_job(self, job: Dict[str, Any]):
        """
        Process a single job
        
        Args:
            job: Job data dictionary
        """
        job_id = job['job_id']
        job_type = job['job_type']
        data = job['data']
        
        try:
            if job_type == 'resume_parsing':
                result = self._process_resume_parsing(data)
            elif job_type == 'email_send':
                result = self._process_email_send(data)
            elif job_type == 'analytics_aggregation':
                result = self._process_analytics_aggregation(data)
            elif job_type == 'ml_scoring':
                result = self._process_ml_scoring(data)
            elif job_type == 'audit_processing':
                result = self._process_audit_processing(data)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            queue_manager.complete_job(job_id, result)
            logger.info(f"✅ Job completed: {job_id}")
            
        except Exception as e:
            error_msg = f"Job failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            queue_manager.fail_job(job_id, error_msg, retry=True)
    
    def _process_resume_parsing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process resume parsing job
        
        Args:
            data: Job data containing candidate_id, file_path, etc.
        
        Returns:
            Result dictionary
        """
        candidate_id = data.get('candidate_id')
        file_path = data.get('file_path')
        
        # Import here to avoid circular imports
        from backend.utils.resume_parser import parse_resume
        
        # Parse resume
        parsed_data = parse_resume(file_path)
        
        # Update candidate profile in database
        if candidate_id and parsed_data:
            candidates = self.db.get_database().candidates
            
            update_data = {
                'parsed_resume': parsed_data,
                'skills': parsed_data.get('skills', []),
                'experience': parsed_data.get('experience', []),
                'education': parsed_data.get('education', [])
            }
            
            candidates.update_one(
                {'_id': candidate_id},
                {'$set': update_data}
            )
        
        return {
            'success': True,
            'candidate_id': candidate_id,
            'skills_count': len(parsed_data.get('skills', [])),
            'experience_count': len(parsed_data.get('experience', []))
        }
    
    def _process_email_send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email send job
        
        Args:
            data: Email data (to, subject, body, etc.)
        
        Returns:
            Result dictionary
        """
        # Import here to avoid circular imports
        from backend.utils.email_service import send_email
        
        to_email = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        html = data.get('html')
        
        success = send_email(to_email, subject, body, html)
        
        return {
            'success': success,
            'to': to_email,
            'subject': subject
        }
    
    def _process_analytics_aggregation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process analytics pre-aggregation job
        
        Args:
            data: Analytics data to aggregate
        
        Returns:
            Result dictionary
        """
        aggregation_type = data.get('type')  # 'daily', 'weekly', 'monthly'
        target = data.get('target')  # 'company', 'candidate', 'job'
        target_id = data.get('target_id')
        
        # Implement analytics pre-aggregation
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        try:
            db = self.database
            applications = db['applications']
            
            # Calculate time window based on aggregation type
            now = datetime.utcnow()
            if aggregation_type == 'daily':
                start_date = now - timedelta(days=1)
            elif aggregation_type == 'weekly':
                start_date = now - timedelta(days=7)
            else:  # monthly
                start_date = now - timedelta(days=30)
            
            # Build query based on target
            query = {'applied_date': {'$gte': start_date}}
            if target == 'job':
                query['job_id'] = target_id
            elif target == 'candidate':
                query['candidate_id'] = target_id
            elif target == 'company':
                # Get all jobs for this company and aggregate
                jobs = list(db['jobs'].find({'company_id': target_id}))
                job_ids = [str(job['_id']) for job in jobs]
                query['job_id'] = {'$in': job_ids}
            
            # Fetch applications
            apps = list(applications.find(query))
            
            # Calculate metrics
            metrics = {
                'total_applications': len(apps),
                'applications_per_day': len(apps) / ((now - start_date).days or 1),
                'avg_score': sum(app.get('overall_score', 0) for app in apps) / len(apps) if apps else 0,
                'status_distribution': defaultdict(int),
                'score_distribution': {'0-25': 0, '25-50': 0, '50-75': 0, '75-100': 0}
            }
            
            # Calculate distributions
            for app in apps:
                status = app.get('status', 'submitted')
                metrics['status_distribution'][status] += 1
                
                score = app.get('overall_score', 0)
                if score < 25:
                    metrics['score_distribution']['0-25'] += 1
                elif score < 50:
                    metrics['score_distribution']['25-50'] += 1
                elif score < 75:
                    metrics['score_distribution']['50-75'] += 1
                else:
                    metrics['score_distribution']['75-100'] += 1
            
            # Cache results using queue manager
            cache_key = f"analytics:{aggregation_type}:{target}:{target_id}"
            from backend.workers.queue_manager import queue_manager
            queue_manager.cache_set(cache_key, metrics, ttl=3600)  # Cache for 1 hour
            
            return {
                'success': True,
                'type': aggregation_type,
                'target': target,
                'target_id': target_id,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Analytics aggregation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_ml_scoring(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ML scoring job
        
        Args:
            data: Scoring data (candidate_id, job_id, etc.)
        
        Returns:
            Result dictionary with scores
        """
        candidate_id = data.get('candidate_id')
        job_id = data.get('job_id')
        
        # Import scoring utilities
        from backend.utils.matching import calculate_match_score
        
        # Get candidate and job data
        db = self.db.get_database()
        candidate = db.candidates.find_one({'_id': candidate_id})
        job = db.jobs.find_one({'_id': job_id})
        
        if not candidate or not job:
            raise ValueError("Candidate or job not found")
        
        # Calculate scores
        scores = calculate_match_score(candidate, job)
        
        # Store scores in applications collection
        db.applications.update_one(
            {'candidate_id': candidate_id, 'job_id': job_id},
            {'$set': {'scores': scores}}
        )
        
        return {
            'success': True,
            'candidate_id': candidate_id,
            'job_id': job_id,
            'scores': scores
        }
    
    def _process_audit_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process audit log processing job
        
        Args:
            data: Audit data to process
        
        Returns:
            Result dictionary
        """
        # This could handle:
        # - Aggregate audit logs
        # - Generate compliance reports
        # - Check for bias patterns
        # - Archive old logs
        
        return {
            'success': True,
            'processed_count': 0
        }


# Create global processor instance
job_processor = JobProcessor()


def start_workers(num_workers: int = 2):
    """
    Start background workers
    
    Args:
        num_workers: Number of worker threads
    """
    job_processor.start(num_workers)


def stop_workers():
    """Stop all background workers"""
    job_processor.stop()


if __name__ == '__main__':
    # Run as standalone worker process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting Smart Hiring System Workers")
    print("Press Ctrl+C to stop")
    
    try:
        start_workers(num_workers=3)
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        stop_workers()
