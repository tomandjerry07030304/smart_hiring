"""
Admin Routes
=============
Handles admin-specific endpoints for system management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from backend.models.database import get_db

bp = Blueprint('admin', __name__)


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """Get platform-wide statistics for admin dashboard"""
    try:
        current_user = get_jwt_identity()
        
        # Get user details to verify admin role
        db = get_db()
        users_collection = db['users']
        
        if isinstance(current_user, str):
            user = users_collection.find_one({'_id': ObjectId(current_user)})
        else:
            user = users_collection.find_one({'_id': ObjectId(current_user.get('user_id'))})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Count statistics
        total_users = users_collection.count_documents({})
        total_candidates = users_collection.count_documents({'role': 'candidate'})
        total_recruiters = users_collection.count_documents({'role': {'$in': ['recruiter', 'company']}})
        total_admins = users_collection.count_documents({'role': 'admin'})
        
        # Jobs stats
        active_jobs = jobs_collection.count_documents({'status': {'$in': ['active', 'open', None]}})
        total_jobs = jobs_collection.count_documents({})
        
        # Applications stats
        total_applications = applications_collection.count_documents({})
        pending_applications = applications_collection.count_documents({'status': {'$in': ['submitted', 'pending', None]}})
        
        return jsonify({
            'success': True,
            'total_users': total_users,
            'users_breakdown': {
                'candidates': total_candidates,
                'recruiters': total_recruiters,
                'admins': total_admins
            },
            'active_jobs': active_jobs,
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching admin stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    try:
        current_user = get_jwt_identity()
        db = get_db()
        users_collection = db['users']
        
        if isinstance(current_user, str):
            user = users_collection.find_one({'_id': ObjectId(current_user)})
        else:
            user = users_collection.find_one({'_id': ObjectId(current_user.get('user_id'))})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        
        # Build query
        query = {}
        if role_filter:
            query['role'] = role_filter
        
        # Get users with pagination
        skip = (page - 1) * per_page
        users = list(users_collection.find(query)
                     .skip(skip)
                     .limit(per_page)
                     .sort('created_at', -1))
        
        total = users_collection.count_documents(query)
        
        # Sanitize user data (remove password hashes)
        sanitized_users = []
        for u in users:
            sanitized_users.append({
                'user_id': str(u['_id']),
                'email': u.get('email'),
                'full_name': u.get('full_name'),
                'role': u.get('role'),
                'is_active': u.get('is_active', True),
                'created_at': u.get('created_at', '').isoformat() if u.get('created_at') else None
            })
        
        return jsonify({
            'success': True,
            'users': sanitized_users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching users: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    """Activate or deactivate a user (admin only)"""
    try:
        current_user = get_jwt_identity()
        db = get_db()
        users_collection = db['users']
        
        if isinstance(current_user, str):
            admin_user = users_collection.find_one({'_id': ObjectId(current_user)})
        else:
            admin_user = users_collection.find_one({'_id': ObjectId(current_user.get('user_id'))})
        
        if not admin_user or admin_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'is_active field required'}), 400
        
        # Update user status
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': is_active, 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'User not found'}), 404
        
        action = 'activated' if is_active else 'deactivated'
        return jsonify({
            'success': True,
            'message': f'User {action} successfully'
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating user status: {str(e)}")
        return jsonify({'error': str(e)}), 500
