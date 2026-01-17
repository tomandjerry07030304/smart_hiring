"""
Celery configuration for background task processing

P0 FIX STATUS (Updated 2026-01-17):
===================================
DECISION: ROBUST HYBRID MODE
- Tries to import Celery.
- If missing/fails: Fallback to MOCK/SYNC mode automatically.
- Prevents startup crashes (ModuleNotFoundError).
- Forces ASYNC_ENABLED=False if Celery is missing.

Current behavior: Auto-detects environment capability.
"""

import os
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Safe Import Logic
CELERY_INSTALLED = False
Celery = None

try:
    from celery import Celery
    CELERY_INSTALLED = True
except (ImportError, ModuleNotFoundError) as e:
    logger.warning(f"⚠️ Celery module not found: {e}. Running in MOCK/SYNC mode.")
    # print(f"⚠️ Celery module not found: {e}. Running in MOCK/SYNC mode.")
    CELERY_INSTALLED = False

# P0 FIX: Default to FALSE - async is NOT enabled by default
# This ensures honest behavior - no silent failures
# Force False if Celery is not installed
REQUESTED_ASYNC = os.getenv('ENABLE_BACKGROUND_WORKERS', 'false').lower() == 'true'
ASYNC_ENABLED = REQUESTED_ASYNC and CELERY_INSTALLED

# Log async status clearly at startup
if ASYNC_ENABLED:
    logger.info("🔄 ASYNC MODE ENABLED - Celery workers required")
    # print("🔄 ASYNC MODE ENABLED - Celery workers must be running")
elif REQUESTED_ASYNC and not CELERY_INSTALLED:
    logger.warning("⚠️ ASYNC REQUESTED BUT CELERY MISSING - Falling back to SYNC mode")
    # print("⚠️ ASYNC REQUESTED BUT CELERY MISSING - Falling back to SYNC mode")
else:
    logger.info("⚡ SYNC MODE - Emails sent synchronously (no Redis/Celery required)")
    # print("⚡ SYNC MODE - Emails sent synchronously (production-ready, no dependencies)")

if ASYNC_ENABLED and CELERY_INSTALLED:
    # Initialize Celery (only used if ASYNC_ENABLED)
    celery_app = Celery(
        'smart_hiring',
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=[
            'backend.tasks.email_tasks',
            'backend.tasks.resume_tasks',
            'backend.tasks.notification_tasks'
        ]
    )

    # Celery configuration
    celery_app.conf.update(
        # Task routing
        task_routes={
            'backend.tasks.email_tasks.*': {'queue': 'email'},
            'backend.tasks.resume_tasks.*': {'queue': 'resume'},
            'backend.tasks.notification_tasks.*': {'queue': 'notifications'},
        },
        
        # Task serialization
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task execution
        task_acks_late=True,  # Tasks are acknowledged after completion
        task_reject_on_worker_lost=True,  # Reject tasks if worker dies
        worker_prefetch_multiplier=1,  # One task at a time per worker
        
        # Task time limits
        task_soft_time_limit=300,  # 5 minutes soft limit
        task_time_limit=600,  # 10 minutes hard limit
        
        # Task retries
        task_autoretry_for=(Exception,),
        task_retry_kwargs={'max_retries': 3},
        task_retry_backoff=True,
        task_retry_backoff_max=600,  # Max 10 minutes between retries
        task_retry_jitter=True,  # Add randomness to avoid thundering herd
        
        # Result backend
        result_expires=3600,  # Results expire after 1 hour
        result_backend_transport_options={
            'master_name': 'mymaster',
            'visibility_timeout': 3600,
        },
        
        # Dead letter queue
        task_default_max_retries=3,
        task_default_retry_delay=60,  # 1 minute default delay
        
        # Beat schedule for periodic tasks
        beat_schedule={
            'cleanup-expired-tokens': {
                'task': 'backend.tasks.maintenance_tasks.cleanup_expired_tokens',
                'schedule': timedelta(hours=1),
            },
            'send-daily-digest': {
                'task': 'backend.tasks.email_tasks.send_daily_digest',
                'schedule': timedelta(days=1),
                'kwargs': {'hour': 9}  # Send at 9 AM UTC
            },
            'analyze-quiz-performance': {
                'task': 'backend.tasks.analytics_tasks.analyze_quiz_performance',
                'schedule': timedelta(hours=6),
            },
        },
        
        # Worker monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Logging
        worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
        worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    )

    # Task base class with error handling
    class SafeTask(celery_app.Task):
        """Base task with automatic error logging"""
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            """Log task failures"""
            print(f'Task {self.name} failed: {exc}')
            # Could also send alert to monitoring service
            
        def on_retry(self, exc, task_id, args, kwargs, einfo):
            """Log task retries"""
            print(f'Task {self.name} retrying: {exc}')
            
        def on_success(self, retval, task_id, args, kwargs):
            """Log task success"""
            # print(f'Task {self.name} succeeded')
            pass

else:
    # MOCK IMPLEMENTATION FOR LITE VERSION OR MISSING CELERY
    logger.info("⚠️ Initializing MockCelery (Sync Mode)")
    
    class MockResult:
        def __init__(self, result=None):
            self.id = 'mock-sync-id'
            self.result = result
            
        def get(self, timeout=None):
            return self.result
            
        def forget(self):
            pass

    class MockTask:
        def __init__(self):
            self.request = type('Request', (), {'retries': 0})()
            self.name = 'MockTask'
            
        def delay(self, *args, **kwargs):
            # In sync mode, we can't easily execute the original function here
            # because we don't have access to it in this scope if it's decorated.
            # BUT, the wrapper in MockCelery.task handles this.
            return MockResult({'status': 'mock_queued'})
            
        def retry(self, exc=None, countdown=None, **kwargs):
            # In sync mode, we just raise the exception
            if exc: raise exc
            raise Exception("Task retry requested in sync mode")

    class MockCelery:
        def __init__(self, *args, **kwargs):
            self.conf = type('Config', (), {'update': lambda *a, **k: None})()
            self.Task = MockTask
            self.tasks = {} # Mock tasks registry
            
        def task(self, *args, **kwargs):
            bind = kwargs.get('bind', False)
            base = kwargs.get('base', None)
            name = kwargs.get('name', 'unknown_task')
            
            def decorator(f):
                def wrapper(*a, **k):
                    try:
                        if bind:
                            res = f(MockTask(), *a, **k)
                        else:
                            res = f(*a, **k)
                        return MockResult(res)
                    except Exception as e:
                        logger.error(f"Error in synchronous task {name}: {e}")
                        raise e
                
                # Mock .delay() to call wrapper synchronously
                wrapper.delay = wrapper
                wrapper.apply_async = lambda args=(), kwargs={}, **opts: wrapper(*args, **kwargs)
                wrapper.name = name
                return wrapper
            return decorator

    celery_app = MockCelery()
    SafeTask = MockTask


# Export
__all__ = ['celery_app', 'SafeTask']
