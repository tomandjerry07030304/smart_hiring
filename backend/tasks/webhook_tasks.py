"""
Webhook delivery background tasks
"""

from backend.celery_config import celery_app, SafeTask
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    base=SafeTask,
    bind=True,
    name='deliver_webhook',
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def deliver_webhook(self, subscription_id, event_type, data):
    """
    Deliver webhook to subscriber with automatic retries
    
    Args:
        subscription_id: Webhook subscription ID
        event_type: Event type
        data: Event payload
    """
    from backend.db import get_db
    from backend.utils.webhooks import WebhookManager
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    attempt = self.request.retries + 1
    
    try:
        result = webhook_manager.deliver_webhook(
            subscription_id=subscription_id,
            event_type=event_type,
            data=data,
            attempt=attempt
        )
        
        if result['status'] == 'failed':
            # Retry on HTTP failure (4xx/5xx)
            raise Exception(f"Webhook delivery failed with status {result.get('status_code')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Webhook delivery failed (attempt {attempt}): {e}")
        
        # If max retries reached, add to dead letter queue
        if attempt >= 3:
            from backend.tasks.dlq_handler import DeadLetterQueue
            
            dlq = DeadLetterQueue(db)
            dlq.add(
                task_name=self.name,
                task_id=self.request.id,
                args=[subscription_id, event_type, data],
                kwargs={},
                exception=e,
                retries=attempt
            )
        
        raise


@celery_app.task(base=SafeTask, name='cleanup_old_deliveries')
def cleanup_old_deliveries(days=30):
    """
    Clean up old webhook delivery records
    
    Args:
        days: Delete records older than this many days
    """
    from backend.db import get_db
    from datetime import datetime, timedelta
    
    db = get_db()
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = db.webhook_deliveries.delete_many({
        'delivered_at': {'$lt': cutoff_date}
    })
    
    logger.info(f"Cleaned up {result.deleted_count} old webhook delivery records")
    
    return {'deleted_count': result.deleted_count}


@celery_app.task(base=SafeTask, name='disable_failing_webhooks')
def disable_failing_webhooks(failure_threshold=10):
    """
    Disable webhooks with high failure rate
    
    Args:
        failure_threshold: Disable after this many consecutive failures
    """
    from backend.db import get_db
    
    db = get_db()
    
    # Find subscriptions with high failure count
    failing_subscriptions = db.webhook_subscriptions.find({
        'active': True,
        'failure_count': {'$gte': failure_threshold}
    })
    
    disabled_count = 0
    
    for subscription in failing_subscriptions:
        # Disable subscription
        db.webhook_subscriptions.update_one(
            {'_id': subscription['_id']},
            {
                '$set': {
                    'active': False,
                    'disabled_reason': f'Exceeded failure threshold ({failure_threshold})',
                    'disabled_at': datetime.utcnow()
                }
            }
        )
        
        disabled_count += 1
        
        # Notify subscription owner
        from backend.tasks.notification_tasks import send_notification
        
        owner_id = subscription.get('owner_id') or subscription.get('created_by')
        if owner_id:
            send_notification.delay(
                user_id=owner_id,
                notification_type='webhook_disabled',
                message=f"Webhook '{subscription.get('name', 'Unknown')}' was disabled due to high failure rate ({failure_threshold} consecutive failures)",
                data={
                    'subscription_id': str(subscription['_id']),
                    'failure_count': subscription['failure_count']
                }
            )
        
        logger.warning(f"Disabled webhook subscription {subscription['_id']} due to high failure rate")
    
    return {'disabled_count': disabled_count}


# Export
__all__ = ['deliver_webhook', 'cleanup_old_deliveries', 'disable_failing_webhooks']
