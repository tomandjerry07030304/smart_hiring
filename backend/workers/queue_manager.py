"""
Queue Manager for Background Job Processing
Uses Redis for queue management and job persistence
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Safe import of redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False
    logger.warning("⚠️ Redis module not installed. Queue manager will run in fallback mode.")


class QueueManager:
    """Manages background job queues using Redis"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = None
        if REDIS_AVAILABLE:
            self._connect()
        else:
            logger.warning("⚠️ Redis not available - running without background queues")
        
        # Queue names
        self.RESUME_PARSING_QUEUE = 'queue:resume_parsing'
        self.ANALYTICS_QUEUE = 'queue:analytics'
        self.EMAIL_QUEUE = 'queue:email'
        self.AUDIT_QUEUE = 'queue:audit'
        self.ML_SCORING_QUEUE = 'queue:ml_scoring'
        
    def _connect(self):
        """Establish Redis connection"""
        if not REDIS_AVAILABLE:
            return
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using fallback mode.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def enqueue_job(
        self,
        queue_name: str,
        job_type: str,
        data: Dict[str, Any],
        priority: int = 0,
        delay_seconds: int = 0
    ) -> Optional[str]:
        """
        Add a job to the queue
        
        Args:
            queue_name: Name of the queue
            job_type: Type of job (e.g., 'resume_parsing', 'email_send')
            data: Job data as dictionary
            priority: Job priority (higher = more important)
            delay_seconds: Delay before processing (for scheduled jobs)
        
        Returns:
            Job ID if successful, None otherwise
        """
        if not self.is_available():
            logger.warning(f"Redis unavailable, processing {job_type} synchronously")
            return None
        
        try:
            job_id = f"{job_type}:{datetime.utcnow().timestamp()}"
            
            job_data = {
                'job_id': job_id,
                'job_type': job_type,
                'data': data,
                'priority': priority,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending',
                'attempts': 0
            }
            
            # Store job data
            self.redis_client.setex(
                f"job:{job_id}",
                timedelta(days=7),  # Job data expires after 7 days
                json.dumps(job_data)
            )
            
            # Add to queue with score (for priority + delay)
            score = datetime.utcnow().timestamp() + delay_seconds - (priority * 1000)
            self.redis_client.zadd(queue_name, {job_id: score})
            
            logger.info(f"✅ Job enqueued: {job_id} in {queue_name}")
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue job: {e}")
            return None
    
    def dequeue_job(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """
        Get next job from queue
        
        Args:
            queue_name: Name of the queue
        
        Returns:
            Job data if available, None otherwise
        """
        if not self.is_available():
            return None
        
        try:
            # Get jobs that are ready (score <= current time)
            current_time = datetime.utcnow().timestamp()
            jobs = self.redis_client.zrangebyscore(
                queue_name,
                '-inf',
                current_time,
                start=0,
                num=1
            )
            
            if not jobs:
                return None
            
            job_id = jobs[0]
            
            # Remove from queue
            self.redis_client.zrem(queue_name, job_id)
            
            # Get job data
            job_data_str = self.redis_client.get(f"job:{job_id}")
            if not job_data_str:
                logger.warning(f"⚠️ Job data not found: {job_id}")
                return None
            
            job_data = json.loads(job_data_str)
            job_data['status'] = 'processing'
            job_data['started_at'] = datetime.utcnow().isoformat()
            
            # Update job data
            self.redis_client.setex(
                f"job:{job_id}",
                timedelta(days=7),
                json.dumps(job_data)
            )
            
            return job_data
            
        except Exception as e:
            logger.error(f"❌ Failed to dequeue job: {e}")
            return None
    
    def complete_job(self, job_id: str, result: Dict[str, Any] = None):
        """Mark job as completed"""
        if not self.is_available():
            return
        
        try:
            job_data_str = self.redis_client.get(f"job:{job_id}")
            if job_data_str:
                job_data = json.loads(job_data_str)
                job_data['status'] = 'completed'
                job_data['completed_at'] = datetime.utcnow().isoformat()
                job_data['result'] = result
                
                # Store for 24 hours
                self.redis_client.setex(
                    f"job:{job_id}",
                    timedelta(hours=24),
                    json.dumps(job_data)
                )
                logger.info(f"✅ Job completed: {job_id}")
        except Exception as e:
            logger.error(f"❌ Failed to mark job as completed: {e}")
    
    def fail_job(self, job_id: str, error: str, retry: bool = True):
        """Mark job as failed and optionally retry"""
        if not self.is_available():
            return
        
        try:
            job_data_str = self.redis_client.get(f"job:{job_id}")
            if job_data_str:
                job_data = json.loads(job_data_str)
                job_data['attempts'] += 1
                job_data['last_error'] = error
                job_data['failed_at'] = datetime.utcnow().isoformat()
                
                max_attempts = 3
                if retry and job_data['attempts'] < max_attempts:
                    # Re-queue with exponential backoff
                    delay = 60 * (2 ** job_data['attempts'])  # 2min, 4min, 8min
                    job_data['status'] = 'retry'
                    
                    self.redis_client.setex(
                        f"job:{job_id}",
                        timedelta(days=7),
                        json.dumps(job_data)
                    )
                    
                    # Re-add to queue
                    score = datetime.utcnow().timestamp() + delay
                    queue_name = self._get_queue_for_job_type(job_data['job_type'])
                    self.redis_client.zadd(queue_name, {job_id: score})
                    
                    logger.warning(f"⚠️ Job failed, retrying: {job_id} (attempt {job_data['attempts']})")
                else:
                    job_data['status'] = 'failed'
                    self.redis_client.setex(
                        f"job:{job_id}",
                        timedelta(hours=24),
                        json.dumps(job_data)
                    )
                    logger.error(f"❌ Job permanently failed: {job_id}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to handle job failure: {e}")
    
    def _get_queue_for_job_type(self, job_type: str) -> str:
        """Get queue name for job type"""
        mapping = {
            'resume_parsing': self.RESUME_PARSING_QUEUE,
            'analytics_aggregation': self.ANALYTICS_QUEUE,
            'email_send': self.EMAIL_QUEUE,
            'audit_processing': self.AUDIT_QUEUE,
            'ml_scoring': self.ML_SCORING_QUEUE
        }
        return mapping.get(job_type, self.RESUME_PARSING_QUEUE)
    
    def get_queue_stats(self, queue_name: str) -> Dict[str, int]:
        """Get statistics for a queue"""
        if not self.is_available():
            return {'pending': 0, 'processing': 0, 'failed': 0}
        
        try:
            pending = self.redis_client.zcard(queue_name)
            
            # Count processing and failed jobs
            processing = 0
            failed = 0
            
            return {
                'pending': pending,
                'processing': processing,
                'failed': failed
            }
        except Exception as e:
            logger.error(f"❌ Failed to get queue stats: {e}")
            return {'pending': 0, 'processing': 0, 'failed': 0}
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        if not self.is_available():
            return None
        
        try:
            job_data_str = self.redis_client.get(f"job:{job_id}")
            if job_data_str:
                return json.loads(job_data_str)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get job status: {e}")
            return None
    
    # Caching methods
    def cache_set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set a cached value"""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.setex(
                f"cache:{key}",
                timedelta(seconds=ttl_seconds),
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set cache: {e}")
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get a cached value"""
        if not self.is_available():
            return None
        
        try:
            value_str = self.redis_client.get(f"cache:{key}")
            if value_str:
                return json.loads(value_str)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get cache: {e}")
            return None
    
    def cache_delete(self, key: str):
        """Delete a cached value"""
        if not self.is_available():
            return
        
        try:
            self.redis_client.delete(f"cache:{key}")
        except Exception as e:
            logger.error(f"❌ Failed to delete cache: {e}")


# Global queue manager instance
queue_manager = QueueManager()
