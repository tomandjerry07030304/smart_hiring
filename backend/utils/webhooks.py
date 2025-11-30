"""
Webhook event system for external integrations
"""

from datetime import datetime, timedelta
from bson import ObjectId
import hmac
import hashlib
import json
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WebhookEvent:
    """Webhook event types"""
    
    APPLICATION_CREATED = 'application.created'
    APPLICATION_STATUS_CHANGED = 'application.status_changed'
    QUIZ_COMPLETED = 'quiz.completed'
    QUIZ_STARTED = 'quiz.started'
    JOB_CREATED = 'job.created'
    JOB_UPDATED = 'job.updated'
    JOB_CLOSED = 'job.closed'
    CANDIDATE_REGISTERED = 'candidate.registered'
    
    @classmethod
    def all_events(cls):
        """Return all available event types"""
        return [
            cls.APPLICATION_CREATED,
            cls.APPLICATION_STATUS_CHANGED,
            cls.QUIZ_COMPLETED,
            cls.QUIZ_STARTED,
            cls.JOB_CREATED,
            cls.JOB_UPDATED,
            cls.JOB_CLOSED,
            cls.CANDIDATE_REGISTERED,
        ]


class WebhookManager:
    """Manage webhook subscriptions and delivery"""
    
    def __init__(self, db):
        self.db = db
        self.subscriptions = db.webhook_subscriptions
        self.deliveries = db.webhook_deliveries
    
    def create_subscription(
        self,
        user_id: str,
        url: str,
        events: list,
        secret: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Create webhook subscription
        
        Args:
            user_id: User/company ID creating subscription
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            secret: Optional secret for HMAC signing (generated if not provided)
            description: Optional description
            
        Returns:
            Subscription ID
        """
        # Generate secret if not provided
        if not secret:
            import secrets
            secret = secrets.token_urlsafe(32)
        
        # Validate events
        invalid_events = [e for e in events if e not in WebhookEvent.all_events()]
        if invalid_events:
            raise ValueError(f"Invalid events: {invalid_events}")
        
        subscription = {
            'user_id': user_id,
            'url': url,
            'events': events,
            'secret': secret,
            'description': description,
            'active': True,
            'created_at': datetime.utcnow(),
            'last_delivery_at': None,
            'delivery_count': 0,
            'failure_count': 0
        }
        
        result = self.subscriptions.insert_one(subscription)
        
        logger.info(f"Created webhook subscription {result.inserted_id} for user {user_id}")
        
        return str(result.inserted_id)
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription by ID"""
        return self.subscriptions.find_one({'_id': ObjectId(subscription_id)})
    
    def list_subscriptions(self, user_id: str, active_only: bool = True) -> list:
        """List user's webhook subscriptions"""
        query = {'user_id': user_id}
        if active_only:
            query['active'] = True
        
        return list(self.subscriptions.find(query))
    
    def update_subscription(
        self,
        subscription_id: str,
        url: Optional[str] = None,
        events: Optional[list] = None,
        active: Optional[bool] = None
    ) -> bool:
        """Update webhook subscription"""
        update_fields = {}
        
        if url is not None:
            update_fields['url'] = url
        
        if events is not None:
            # Validate events
            invalid_events = [e for e in events if e not in WebhookEvent.all_events()]
            if invalid_events:
                raise ValueError(f"Invalid events: {invalid_events}")
            update_fields['events'] = events
        
        if active is not None:
            update_fields['active'] = active
        
        if not update_fields:
            return False
        
        update_fields['updated_at'] = datetime.utcnow()
        
        result = self.subscriptions.update_one(
            {'_id': ObjectId(subscription_id)},
            {'$set': update_fields}
        )
        
        return result.modified_count > 0
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete webhook subscription"""
        result = self.subscriptions.delete_one({'_id': ObjectId(subscription_id)})
        return result.deleted_count > 0
    
    def trigger_event(
        self,
        event_type: str,
        data: Dict[Any, Any],
        user_id: Optional[str] = None
    ):
        """
        Trigger webhook event
        
        Args:
            event_type: Type of event (e.g., 'application.created')
            data: Event payload data
            user_id: Optional user ID (used for filtering subscriptions)
        """
        # Find matching subscriptions
        query = {
            'active': True,
            'events': event_type
        }
        
        if user_id:
            query['user_id'] = user_id
        
        subscriptions = list(self.subscriptions.find(query))
        
        if not subscriptions:
            logger.debug(f"No active subscriptions for event {event_type}")
            return
        
        # Queue delivery for each subscription
        from backend.tasks.webhook_tasks import deliver_webhook
        
        for subscription in subscriptions:
            deliver_webhook.delay(
                subscription_id=str(subscription['_id']),
                event_type=event_type,
                data=data
            )
        
        logger.info(f"Queued webhook delivery for event {event_type} to {len(subscriptions)} subscribers")
    
    def deliver_webhook(
        self,
        subscription_id: str,
        event_type: str,
        data: Dict[Any, Any],
        attempt: int = 1
    ) -> Dict:
        """
        Deliver webhook to subscriber
        
        Args:
            subscription_id: Subscription ID
            event_type: Event type
            data: Event payload
            attempt: Delivery attempt number
            
        Returns:
            Delivery result
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription or not subscription['active']:
            return {'status': 'cancelled', 'reason': 'Subscription inactive'}
        
        # Build payload
        payload = {
            'event': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'subscription_id': subscription_id
        }
        
        # Generate HMAC signature
        signature = self._generate_signature(payload, subscription['secret'])
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Event': event_type,
            'X-Webhook-Delivery-ID': str(ObjectId()),
            'User-Agent': 'SmartHiring-Webhook/1.0'
        }
        
        # Record delivery attempt
        delivery_record = {
            'subscription_id': ObjectId(subscription_id),
            'event_type': event_type,
            'payload': payload,
            'attempt': attempt,
            'delivered_at': datetime.utcnow(),
            'status': 'pending',
            'response_code': None,
            'response_body': None,
            'error': None
        }
        
        delivery_id = self.deliveries.insert_one(delivery_record).inserted_id
        
        # Send webhook
        try:
            response = requests.post(
                subscription['url'],
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Update delivery record
            self.deliveries.update_one(
                {'_id': delivery_id},
                {
                    '$set': {
                        'status': 'success' if response.ok else 'failed',
                        'response_code': response.status_code,
                        'response_body': response.text[:1000]  # Truncate
                    }
                }
            )
            
            # Update subscription stats
            self.subscriptions.update_one(
                {'_id': ObjectId(subscription_id)},
                {
                    '$set': {'last_delivery_at': datetime.utcnow()},
                    '$inc': {
                        'delivery_count': 1,
                        'failure_count': 0 if response.ok else 1
                    }
                }
            )
            
            if response.ok:
                logger.info(f"Webhook delivered successfully: {subscription_id} (attempt {attempt})")
                return {'status': 'success', 'delivery_id': str(delivery_id)}
            else:
                logger.warning(f"Webhook delivery failed: {subscription_id} - {response.status_code}")
                return {
                    'status': 'failed',
                    'delivery_id': str(delivery_id),
                    'status_code': response.status_code
                }
        
        except Exception as e:
            logger.error(f"Webhook delivery error: {subscription_id} - {e}")
            
            # Update delivery record
            self.deliveries.update_one(
                {'_id': delivery_id},
                {
                    '$set': {
                        'status': 'error',
                        'error': str(e)
                    }
                }
            )
            
            # Update subscription stats
            self.subscriptions.update_one(
                {'_id': ObjectId(subscription_id)},
                {'$inc': {'failure_count': 1}}
            )
            
            return {'status': 'error', 'delivery_id': str(delivery_id), 'error': str(e)}
    
    def _generate_signature(self, payload: Dict, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_signature(self, payload: Dict, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = self._generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def get_delivery_history(
        self,
        subscription_id: str,
        limit: int = 50
    ) -> list:
        """Get delivery history for subscription"""
        return list(
            self.deliveries
            .find({'subscription_id': ObjectId(subscription_id)})
            .sort('delivered_at', -1)
            .limit(limit)
        )
    
    def get_subscription_stats(self, subscription_id: str) -> Dict:
        """Get statistics for subscription"""
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return {}
        
        # Aggregate delivery stats
        pipeline = [
            {'$match': {'subscription_id': ObjectId(subscription_id)}},
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]
        
        delivery_stats = {item['_id']: item['count'] for item in self.deliveries.aggregate(pipeline)}
        
        return {
            'subscription_id': subscription_id,
            'active': subscription['active'],
            'created_at': subscription['created_at'],
            'total_deliveries': subscription.get('delivery_count', 0),
            'failed_deliveries': subscription.get('failure_count', 0),
            'last_delivery_at': subscription.get('last_delivery_at'),
            'delivery_breakdown': delivery_stats,
            'success_rate': (
                (delivery_stats.get('success', 0) / sum(delivery_stats.values()) * 100)
                if delivery_stats else 0
            )
        }


# Export
__all__ = ['WebhookEvent', 'WebhookManager']
