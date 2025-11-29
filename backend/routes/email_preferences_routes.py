"""
Email Preferences Management Routes
Allows users to control their email notification settings
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db

bp = Blueprint('email_preferences', __name__)

@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_email_preferences():
    """Get user's email preferences"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id')
        
        db = get_db()
        users_collection = db['users']
        
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get email preferences or return defaults
        email_prefs = user.get('email_preferences', {
            'welcome_emails': True,
            'application_confirmations': True,
            'status_updates': True,
            'new_job_alerts': True,
            'newsletter': True,
            'marketing': False
        })
        
        return jsonify({
            'preferences': email_prefs,
            'email': user.get('email')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_email_preferences():
    """Update user's email preferences"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id')
        
        data = request.get_json()
        
        # Validate preferences
        valid_keys = [
            'welcome_emails',
            'application_confirmations',
            'status_updates',
            'new_job_alerts',
            'newsletter',
            'marketing'
        ]
        
        preferences = {}
        for key in valid_keys:
            if key in data:
                if not isinstance(data[key], bool):
                    return jsonify({'error': f'{key} must be a boolean'}), 400
                preferences[key] = data[key]
        
        if not preferences:
            return jsonify({'error': 'No valid preferences provided'}), 400
        
        db = get_db()
        users_collection = db['users']
        
        # Update preferences
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    f'email_preferences.{key}': value 
                    for key, value in preferences.items()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'Email preferences updated successfully',
            'preferences': preferences
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe from all marketing emails (no auth required, uses token)"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        unsubscribe_token = data.get('token')
        
        if not email or not unsubscribe_token:
            return jsonify({'error': 'Email and token required'}), 400
        
        db = get_db()
        users_collection = db['users']
        
        # Find user with matching email and token
        user = users_collection.find_one({
            'email': email,
            'unsubscribe_token': unsubscribe_token
        })
        
        if not user:
            return jsonify({'error': 'Invalid unsubscribe link'}), 400
        
        # Disable all non-essential emails
        result = users_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'email_preferences.newsletter': False,
                    'email_preferences.marketing': False,
                    'email_preferences.new_job_alerts': False,
                    'unsubscribed_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'message': 'Successfully unsubscribed from marketing emails',
            'note': 'You will still receive important transactional emails'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/resubscribe', methods=['POST'])
@jwt_required()
def resubscribe():
    """Re-enable marketing emails"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id')
        
        db = get_db()
        users_collection = db['users']
        
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'email_preferences.newsletter': True,
                    'email_preferences.marketing': True,
                    'email_preferences.new_job_alerts': True
                },
                '$unset': {
                    'unsubscribed_at': ''
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'Successfully resubscribed to email notifications'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
