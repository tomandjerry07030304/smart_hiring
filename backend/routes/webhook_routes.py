"""
Webhook API routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.webhooks import WebhookManager, WebhookEvent
from backend.db import get_db
from backend.utils.responses import (
    success_response,
    error_response,
    created_response,
    no_content_response,
    forbidden
)

webhooks_bp = Blueprint('webhooks', __name__)


@webhooks_bp.route('/subscriptions', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create new webhook subscription"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('url'):
        return error_response("URL is required", status_code=422)
    
    if not data.get('events'):
        return error_response("Events list is required", status_code=422)
    
    # Validate URL
    url = data['url']
    if not url.startswith('https://') and not url.startswith('http://'):
        return error_response("URL must start with http:// or https://", status_code=422)
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    try:
        subscription_id = webhook_manager.create_subscription(
            user_id=current_user_id,
            url=url,
            events=data['events'],
            secret=data.get('secret'),
            description=data.get('description')
        )
        
        subscription = webhook_manager.get_subscription(subscription_id)
        
        # Don't expose secret in response
        subscription_data = {
            'id': str(subscription['_id']),
            'url': subscription['url'],
            'events': subscription['events'],
            'description': subscription.get('description'),
            'active': subscription['active'],
            'created_at': subscription['created_at'].isoformat()
        }
        
        return created_response(subscription_data, "Webhook subscription created successfully")
        
    except ValueError as e:
        return error_response(str(e), status_code=422)


@webhooks_bp.route('/subscriptions', methods=['GET'])
@jwt_required()
def list_subscriptions():
    """List user's webhook subscriptions"""
    current_user_id = get_jwt_identity()
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    subscriptions = webhook_manager.list_subscriptions(current_user_id)
    
    # Format response (exclude secrets)
    subscriptions_data = [
        {
            'id': str(sub['_id']),
            'url': sub['url'],
            'events': sub['events'],
            'description': sub.get('description'),
            'active': sub['active'],
            'created_at': sub['created_at'].isoformat(),
            'delivery_count': sub.get('delivery_count', 0),
            'failure_count': sub.get('failure_count', 0)
        }
        for sub in subscriptions
    ]
    
    return success_response(subscriptions_data)


@webhooks_bp.route('/subscriptions/<subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    """Get webhook subscription details"""
    current_user_id = get_jwt_identity()
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    subscription = webhook_manager.get_subscription(subscription_id)
    
    if not subscription:
        return error_response("Subscription not found", status_code=404)
    
    # Check ownership
    if subscription['user_id'] != current_user_id:
        return forbidden("You don't have access to this subscription")
    
    # Include statistics
    stats = webhook_manager.get_subscription_stats(subscription_id)
    
    subscription_data = {
        'id': str(subscription['_id']),
        'url': subscription['url'],
        'events': subscription['events'],
        'description': subscription.get('description'),
        'active': subscription['active'],
        'created_at': subscription['created_at'].isoformat(),
        'statistics': stats
    }
    
    return success_response(subscription_data)


@webhooks_bp.route('/subscriptions/<subscription_id>', methods=['PUT'])
@jwt_required()
def update_subscription(subscription_id):
    """Update webhook subscription"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    subscription = webhook_manager.get_subscription(subscription_id)
    
    if not subscription:
        return error_response("Subscription not found", status_code=404)
    
    # Check ownership
    if subscription['user_id'] != current_user_id:
        return forbidden("You don't have access to this subscription")
    
    try:
        updated = webhook_manager.update_subscription(
            subscription_id=subscription_id,
            url=data.get('url'),
            events=data.get('events'),
            active=data.get('active')
        )
        
        if updated:
            return success_response({}, "Subscription updated successfully")
        else:
            return error_response("No changes made", status_code=400)
            
    except ValueError as e:
        return error_response(str(e), status_code=422)


@webhooks_bp.route('/subscriptions/<subscription_id>', methods=['DELETE'])
@jwt_required()
def delete_subscription(subscription_id):
    """Delete webhook subscription"""
    current_user_id = get_jwt_identity()
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    subscription = webhook_manager.get_subscription(subscription_id)
    
    if not subscription:
        return error_response("Subscription not found", status_code=404)
    
    # Check ownership
    if subscription['user_id'] != current_user_id:
        return forbidden("You don't have access to this subscription")
    
    deleted = webhook_manager.delete_subscription(subscription_id)
    
    if deleted:
        return no_content_response()
    else:
        return error_response("Failed to delete subscription", status_code=500)


@webhooks_bp.route('/subscriptions/<subscription_id>/deliveries', methods=['GET'])
@jwt_required()
def get_delivery_history(subscription_id):
    """Get webhook delivery history"""
    current_user_id = get_jwt_identity()
    
    db = get_db()
    webhook_manager = WebhookManager(db)
    
    subscription = webhook_manager.get_subscription(subscription_id)
    
    if not subscription:
        return error_response("Subscription not found", status_code=404)
    
    # Check ownership
    if subscription['user_id'] != current_user_id:
        return forbidden("You don't have access to this subscription")
    
    limit = request.args.get('limit', 50, type=int)
    deliveries = webhook_manager.get_delivery_history(subscription_id, limit=limit)
    
    # Format deliveries
    deliveries_data = [
        {
            'id': str(delivery['_id']),
            'event_type': delivery['event_type'],
            'attempt': delivery['attempt'],
            'status': delivery['status'],
            'delivered_at': delivery['delivered_at'].isoformat(),
            'response_code': delivery.get('response_code'),
            'error': delivery.get('error')
        }
        for delivery in deliveries
    ]
    
    return success_response(deliveries_data)


@webhooks_bp.route('/events', methods=['GET'])
@jwt_required()
def list_event_types():
    """List available webhook event types"""
    events = [
        {
            'type': event,
            'description': _get_event_description(event)
        }
        for event in WebhookEvent.all_events()
    ]
    
    return success_response(events)


def _get_event_description(event_type):
    """Get human-readable description for event type"""
    descriptions = {
        WebhookEvent.APPLICATION_CREATED: "Triggered when a new job application is submitted",
        WebhookEvent.APPLICATION_STATUS_CHANGED: "Triggered when an application status is updated",
        WebhookEvent.QUIZ_COMPLETED: "Triggered when a candidate completes an assessment",
        WebhookEvent.QUIZ_STARTED: "Triggered when a candidate starts an assessment",
        WebhookEvent.JOB_CREATED: "Triggered when a new job is posted",
        WebhookEvent.JOB_UPDATED: "Triggered when a job posting is updated",
        WebhookEvent.JOB_CLOSED: "Triggered when a job posting is closed",
        WebhookEvent.CANDIDATE_REGISTERED: "Triggered when a new candidate registers",
    }
    
    return descriptions.get(event_type, "Unknown event")


# Export
__all__ = ['webhooks_bp']
