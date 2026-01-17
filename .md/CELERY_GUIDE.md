# Celery Background Tasks Guide

## Overview
Smart Hiring System uses Celery with Redis as the message broker for asynchronous task processing, improving system responsiveness and reliability.

## Architecture

### Components
- **Celery Worker**: Processes background tasks
- **Redis**: Message broker and result backend
- **Celery Beat**: Scheduler for periodic tasks
- **Flower**: Real-time monitoring dashboard

### Task Queues
- `email`: Email sending tasks
- `resume`: Resume parsing and analysis
- `notifications`: In-app notifications
- `default`: General background tasks

## Running Celery

### Development

**Start Celery Worker:**
```powershell
cd smart-hiring-system
celery -A backend.celery_config.celery_app worker --loglevel=info --pool=solo
```

**Start Celery Beat (Scheduler):**
```powershell
celery -A backend.celery_config.celery_app beat --loglevel=info
```

**Start Flower (Monitoring):**
```powershell
celery -A backend.celery_config.celery_app flower --port=5555
```
Visit: http://localhost:5555

### Production

**Docker Compose** (already configured in `docker-compose.yml`):
```yaml
worker:
  build: .
  command: celery -A backend.celery_config.celery_app worker --loglevel=info
  depends_on:
    - redis
    - mongodb
```

**Render.com** (update `render.yaml`):
```yaml
- type: worker
  name: celery-worker
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: celery -A backend.celery_config.celery_app worker --loglevel=info
```

## Task Types

### Email Tasks (`backend/tasks/email_tasks.py`)

**Send Email:**
```python
from backend.tasks.email_tasks import send_email_task

# Queue email
task = send_email_task.delay(
    to_email='user@example.com',
    subject='Welcome',
    body='Welcome to our platform',
    html_body='<h1>Welcome!</h1>'
)

# Check status
result = task.get(timeout=10)
```

**Send Welcome Email:**
```python
from backend.tasks.email_tasks import send_welcome_email

send_welcome_email.delay('user@example.com', 'John Doe')
```

**Application Status Update:**
```python
from backend.tasks.email_tasks import send_application_status_email

send_application_status_email.delay(
    user_email='candidate@example.com',
    job_title='Senior Developer',
    new_status='interview_scheduled'
)
```

### Resume Tasks (`backend/tasks/resume_tasks.py`)

**Parse Resume:**
```python
from backend.tasks.resume_tasks import parse_resume_task

task = parse_resume_task.delay(
    resume_url='https://example.com/resume.pdf',
    application_id='507f1f77bcf86cd799439011'
)
```

**Batch Parse:**
```python
from backend.tasks.resume_tasks import batch_parse_resumes

application_ids = ['id1', 'id2', 'id3']
batch_parse_resumes.delay(application_ids)
```

**Analyze Candidate Fit:**
```python
from backend.tasks.resume_tasks import analyze_candidate_fit

analyze_candidate_fit.delay(
    application_id='507f1f77bcf86cd799439011',
    job_id='507f191e810c19729de860ea'
)
```

### Notification Tasks (`backend/tasks/notification_tasks.py`)

**Send Notification:**
```python
from backend.tasks.notification_tasks import send_notification

send_notification.delay(
    user_id='507f1f77bcf86cd799439011',
    notification_type='job_match',
    message='New job match found!',
    data={'job_id': '...', 'match_score': 85}
)
```

## Retry Strategy

### Automatic Retries
Tasks automatically retry on failure with exponential backoff:
- **Max retries**: 3
- **Backoff**: 2^retries * 60 seconds
- **Jitter**: Random delay to avoid thundering herd

### Custom Retry
```python
@celery_app.task(bind=True)
def my_task(self, arg):
    try:
        # Task logic
        pass
    except Exception as exc:
        # Retry after 5 minutes
        raise self.retry(exc=exc, countdown=300, max_retries=5)
```

## Dead Letter Queue (DLQ)

### Overview
Failed tasks (after all retries) are stored in DLQ for manual review.

### Check DLQ
```python
from backend.tasks.dlq_handler import DeadLetterQueue
from backend.db import get_db

db = get_db()
dlq = DeadLetterQueue(db)

# Get statistics
stats = dlq.get_stats()
print(f"Pending entries: {stats['pending']}")

# Get pending entries
entries = dlq.get_pending(limit=10)
for entry in entries:
    print(f"Task: {entry['task_name']}, Failed: {entry['failed_at']}")
```

### Retry Failed Task
```python
# Retry task from DLQ
result = dlq.retry_task(dlq_id='...')

# Mark as reviewed
dlq.mark_reviewed(
    dlq_id='...',
    action='discarded',
    notes='Known issue, fixed in code'
)
```

## Periodic Tasks

Configured in `backend/celery_config.py`:

### Cleanup Expired Tokens
- **Schedule**: Every 1 hour
- **Task**: `cleanup_expired_tokens`

### Daily Digest Emails
- **Schedule**: Daily at 9 AM UTC
- **Task**: `send_daily_digest`

### Quiz Performance Analysis
- **Schedule**: Every 6 hours
- **Task**: `analyze_quiz_performance`

### Custom Periodic Task
```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'my-task': {
        'task': 'backend.tasks.my_tasks.my_function',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    }
}
```

## Monitoring

### Flower Dashboard
- **URL**: http://localhost:5555 (development)
- **Features**:
  - Real-time task monitoring
  - Task history and statistics
  - Worker management
  - Task filtering and search

### Task Events
```python
# Enable task events
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
```

### Check Task Status
```python
from backend.celery_config import celery_app

# Get task result
result = celery_app.AsyncResult(task_id)

print(f"Status: {result.state}")  # PENDING, STARTED, SUCCESS, FAILURE
print(f"Result: {result.result}")  # Task return value or exception
```

## Error Handling

### Task Failure Callback
```python
from backend.celery_config import SafeTask

@celery_app.task(base=SafeTask)
def my_task():
    # Automatic logging on failure
    pass
```

### Custom Error Handler
```python
class MyTask(celery_app.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Send alert
        print(f"Task failed: {exc}")
        
        # Add to DLQ
        from backend.tasks.dlq_handler import DeadLetterQueue
        dlq = DeadLetterQueue(get_db())
        dlq.add(self.name, task_id, args, kwargs, exc, self.request.retries)
```

## Best Practices

### 1. Keep Tasks Idempotent
```python
# Good: Can run multiple times safely
@celery_app.task
def update_user_score(user_id, score):
    db.users.update_one(
        {'_id': user_id},
        {'$set': {'score': score}}  # Idempotent
    )

# Bad: Not idempotent
@celery_app.task
def increment_score(user_id):
    db.users.update_one(
        {'_id': user_id},
        {'$inc': {'score': 1}}  # Running twice increments twice
    )
```

### 2. Task Timeouts
```python
@celery_app.task(soft_time_limit=300, time_limit=600)
def long_running_task():
    # Will be interrupted after 5 minutes (soft)
    # Will be killed after 10 minutes (hard)
    pass
```

### 3. Avoid Passing Large Objects
```python
# Bad: Passing large object
@celery_app.task
def process_data(large_dataframe):
    pass

# Good: Pass identifier
@celery_app.task
def process_data(data_id):
    # Load data inside task
    data = db.data.find_one({'_id': data_id})
    pass
```

### 4. Use ETA for Scheduled Tasks
```python
from datetime import datetime, timedelta

# Schedule task for future
send_email_task.apply_async(
    args=['user@example.com', 'Reminder', 'Your reminder'],
    eta=datetime.utcnow() + timedelta(hours=1)
)
```

## Troubleshooting

### Worker Not Processing Tasks
1. Check Redis connection: `redis-cli ping`
2. Check worker logs: `celery -A backend.celery_config.celery_app inspect active`
3. Restart worker

### Tasks Stuck in Pending
1. Check if worker is running
2. Check queue routing: `celery -A backend.celery_config.celery_app inspect registered`
3. Check Redis memory: `redis-cli INFO memory`

### High Memory Usage
1. Reduce `worker_prefetch_multiplier` (default: 4, set to 1 for long tasks)
2. Set task result expiration: `result_expires=3600`
3. Clear old results: `celery -A backend.celery_config.celery_app purge`

## Production Checklist

- [ ] Configure SMTP credentials in environment
- [ ] Set up Redis persistence (AOF or RDB)
- [ ] Enable Celery worker autoscaling
- [ ] Configure Flower authentication
- [ ] Set up monitoring alerts (Sentry)
- [ ] Configure task rate limits
- [ ] Test DLQ review process
- [ ] Set up worker health checks
- [ ] Configure result backend cleanup
- [ ] Test failover scenarios

## Environment Variables

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@smarthiring.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERYD_CONCURRENCY=4
CELERY_TASK_TIME_LIMIT=600
```

## Additional Resources

- **Celery Documentation**: https://docs.celeryq.dev
- **Flower Documentation**: https://flower.readthedocs.io
- **Redis Documentation**: https://redis.io/documentation
