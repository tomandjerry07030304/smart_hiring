from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db
from backend.utils.email_service import email_service

bp = Blueprint('company', __name__)

@bp.route('/applications/<application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(application_id):
    """Update application status with history tracking"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            db = get_db()
            users_collection = db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
            recruiter_email = user.get('email')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
            db = get_db()
            users_collection = db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            recruiter_email = user.get('email') if user else 'Unknown'
        
        if role not in ['company', 'admin']:
            return jsonify({'error': 'Only recruiters can update application status'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        note = data.get('note', '')
        
        # Validate status
        valid_statuses = ['pending', 'shortlisted', 'interviewed', 'hired', 'rejected']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        db = get_db()
        applications_collection = db['applications']
        
        # Get application
        application = applications_collection.find_one({'_id': ObjectId(application_id)})
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        old_status = application.get('status', 'pending')
        
        # Create status history entry
        status_history = application.get('status_history', [])
        status_history.append({
            'status': new_status,
            'changed_by': user_id,
            'changed_by_email': recruiter_email,
            'changed_at': datetime.utcnow(),
            'note': note,
            'previous_status': old_status
        })
        
        # Update application
        result = applications_collection.update_one(
            {'_id': ObjectId(application_id)},
            {
                '$set': {
                    'status': new_status,
                    'status_updated_at': datetime.utcnow(),
                    'status_updated_by': user_id,
                    'status_history': status_history
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update status'}), 500
        
        # Send email notification to candidate
        try:
            candidates_collection = db['candidates']
            users_collection = db['users']
            jobs_collection = db['jobs']
            
            candidate_id = application.get('candidate_id')
            candidate_user = users_collection.find_one({'_id': ObjectId(candidate_id)})
            job = jobs_collection.find_one({'_id': ObjectId(application.get('job_id'))})
            
            if candidate_user and job:
                email_service.send_status_update_email(
                    to_email=candidate_user.get('email'),
                    candidate_name=candidate_user.get('full_name'),
                    job_title=job.get('title'),
                    new_status=new_status,
                    note=note if note else None
                )
        except Exception as email_error:
            print(f"⚠️ Status update email failed: {email_error}")
        
        return jsonify({
            'message': 'Status updated successfully',
            'new_status': new_status,
            'application_id': application_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/applications/<application_id>/history', methods=['GET'])
@jwt_required()
def get_application_history(application_id):
    """Get status change history for an application"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            db = get_db()
            users_collection = db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
        
        if role not in ['company', 'admin', 'candidate']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db = get_db()
        applications_collection = db['applications']
        
        application = applications_collection.find_one({'_id': ObjectId(application_id)})
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # If candidate, verify they own this application
        if role == 'candidate' and application.get('candidate_id') != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        status_history = application.get('status_history', [])
        
        # Convert datetime objects to strings
        for entry in status_history:
            if 'changed_at' in entry:
                entry['changed_at'] = entry['changed_at'].isoformat()
        
        return jsonify({
            'application_id': application_id,
            'current_status': application.get('status', 'pending'),
            'history': status_history
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/applications/stats', methods=['GET'])
@jwt_required()
def get_application_stats():
    """Get application statistics for recruiter"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            db = get_db()
            users_collection = db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
        
        if role != 'company':
            return jsonify({'error': 'Only recruiters can view stats'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Get all jobs for this recruiter
        recruiter_jobs = list(jobs_collection.find(
            {'recruiter_id': user_id}
        ))
        job_ids = [str(job['_id']) for job in recruiter_jobs]
        
        # Get all applications for these jobs
        applications = list(applications_collection.find(
            {'job_id': {'$in': job_ids}}
        ))
        
        # Calculate statistics
        stats = {
            'total': len(applications),
            'pending': len([a for a in applications if a.get('status') == 'pending']),
            'shortlisted': len([a for a in applications if a.get('status') == 'shortlisted']),
            'interviewed': len([a for a in applications if a.get('status') == 'interviewed']),
            'hired': len([a for a in applications if a.get('status') == 'hired']),
            'rejected': len([a for a in applications if a.get('status') == 'rejected']),
            'conversion_rate': 0
        }
        
        # Calculate conversion rate (hired / total)
        if stats['total'] > 0:
            stats['conversion_rate'] = round((stats['hired'] / stats['total']) * 100, 2)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
