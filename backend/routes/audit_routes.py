"""
Fairness Audit Logging Routes
Track all hiring decisions for compliance and bias detection
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db

bp = Blueprint('audit', __name__)


def log_audit_event(event_type, user_id, job_id=None, candidate_id=None, 
                   application_id=None, details=None, scores=None):
    """
    Log an audit event for fairness tracking
    
    Args:
        event_type: Type of event (application_submitted, status_changed, ranked, etc.)
        user_id: ID of user performing the action
        job_id: ID of job (optional)
        candidate_id: ID of candidate (optional)
        application_id: ID of application (optional)
        details: Additional details about the event
        scores: Scoring information if applicable
    """
    try:
        db = get_db()
        audit_log = {
            'event_type': event_type,
            'user_id': user_id,
            'job_id': job_id,
            'candidate_id': candidate_id,
            'application_id': application_id,
            'details': details or {},
            'scores': scores or {},
            'timestamp': datetime.utcnow(),
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        db['audit_logs'].insert_one(audit_log)
        print(f"✅ Audit log created: {event_type}")
        return True
    except Exception as e:
        print(f"❌ Audit log error: {e}")
        return False


@bp.route('/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get audit logs (admin only)"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            db = get_db()
            user = db['users'].find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
        
        if role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        db = get_db()
        
        # Get filters from query params
        event_type = request.args.get('event_type')
        job_id = request.args.get('job_id')
        candidate_id = request.args.get('candidate_id')
        limit = int(request.args.get('limit', 100))
        
        # Build query
        query = {}
        if event_type:
            query['event_type'] = event_type
        if job_id:
            query['job_id'] = job_id
        if candidate_id:
            query['candidate_id'] = candidate_id
        
        # Get logs
        logs = list(db['audit_logs'].find(query).sort('timestamp', -1).limit(limit))
        
        # Convert ObjectId to string and format dates
        for log in logs:
            log['_id'] = str(log['_id'])
            if 'timestamp' in log:
                log['timestamp'] = log['timestamp'].isoformat()
        
        return jsonify({
            'total': len(logs),
            'logs': logs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/report', methods=['GET'])
@jwt_required()
def generate_audit_report():
    """Generate comprehensive fairness audit report"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            db = get_db()
            user = db['users'].find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
        
        if role not in ['admin', 'company']:
            return jsonify({'error': 'Admin or company access required'}), 403
        
        db = get_db()
        
        # Get date range
        days = int(request.args.get('days', 30))
        from_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter by company for recruiters
        query = {'timestamp': {'$gte': from_date}}
        if role == 'company':
            # Only show logs for this company's jobs
            jobs = list(db['jobs'].find({'recruiter_id': user_id}))
            job_ids = [str(job['_id']) for job in jobs]
            query['job_id'] = {'$in': job_ids}
        
        # Get all relevant logs
        logs = list(db['audit_logs'].find(query))
        
        # Generate statistics
        report = {
            'period': f'Last {days} days',
            'generated_at': datetime.utcnow().isoformat(),
            'total_events': len(logs),
            'events_by_type': {},
            'applications_processed': 0,
            'status_changes': 0,
            'rankings_performed': 0,
            'average_score': 0,
            'score_distribution': {
                'excellent': 0,  # 75%+
                'good': 0,       # 50-74%
                'poor': 0        # <50%
            },
            'decisions': {
                'hired': 0,
                'rejected': 0,
                'pending': 0,
                'shortlisted': 0
            }
        }
        
        total_scores = []
        
        for log in logs:
            event_type = log.get('event_type', 'unknown')
            report['events_by_type'][event_type] = report['events_by_type'].get(event_type, 0) + 1
            
            if event_type == 'application_submitted':
                report['applications_processed'] += 1
            elif event_type == 'status_changed':
                report['status_changes'] += 1
                status = log.get('details', {}).get('new_status')
                if status in report['decisions']:
                    report['decisions'][status] += 1
            elif event_type == 'ranked':
                report['rankings_performed'] += 1
                score = log.get('scores', {}).get('overall_score')
                if score:
                    total_scores.append(score)
                    if score >= 75:
                        report['score_distribution']['excellent'] += 1
                    elif score >= 50:
                        report['score_distribution']['good'] += 1
                    else:
                        report['score_distribution']['poor'] += 1
        
        # Calculate average score
        if total_scores:
            report['average_score'] = round(sum(total_scores) / len(total_scores), 2)
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/job/<job_id>/report', methods=['GET'])
@jwt_required()
def get_job_audit_report(job_id):
    """Get audit report for a specific job"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            db = get_db()
            user = db['users'].find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
        
        if role not in ['admin', 'company']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db = get_db()
        
        # Verify job access for companies
        if role == 'company':
            job = db['jobs'].find_one({'_id': ObjectId(job_id), 'recruiter_id': user_id})
            if not job:
                return jsonify({'error': 'Job not found or unauthorized'}), 404
        
        # Get all logs for this job
        logs = list(db['audit_logs'].find({'job_id': job_id}))
        
        report = {
            'job_id': job_id,
            'total_logs': len(logs),
            'applications': 0,
            'rankings': 0,
            'status_changes': 0,
            'timeline': []
        }
        
        for log in logs:
            event = {
                'type': log.get('event_type'),
                'timestamp': log.get('timestamp').isoformat() if log.get('timestamp') else None,
                'details': log.get('details', {})
            }
            report['timeline'].append(event)
            
            event_type = log.get('event_type')
            if event_type == 'application_submitted':
                report['applications'] += 1
            elif event_type == 'ranked':
                report['rankings'] += 1
            elif event_type == 'status_changed':
                report['status_changes'] += 1
        
        # Sort timeline by date (newest first)
        report['timeline'].sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Import at module level to avoid circular imports
from datetime import timedelta
