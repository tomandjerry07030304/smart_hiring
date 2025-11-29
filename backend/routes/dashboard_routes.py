from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
import pandas as pd

from backend.models.database import get_db
from backend.services.fairness_service import generate_fairness_report, get_fairness_badge

bp = Blueprint('dashboard', __name__)

@bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get recruitment analytics (recruiter only)"""
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
        
        if role not in ['recruiter', 'admin', 'candidate']:
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Get recruiter's jobs or candidate's applications
        if role == 'candidate':
            # For candidates, show their application analytics
            applications = list(applications_collection.find({'candidate_id': user_id}))
            jobs = []
            for app in applications:
                job = jobs_collection.find_one({'_id': ObjectId(app['job_id'])})
                if job:
                    jobs.append(job)
            recruiter_id = None
        else:
            # For recruiters/admins
            recruiter_id = user_id
            jobs = list(jobs_collection.find({'recruiter_id': recruiter_id}))
            job_ids = [str(job['_id']) for job in jobs]
            
            # Get all applications for these jobs
            applications = list(applications_collection.find({'job_id': {'$in': job_ids}}))
        
        # Calculate statistics
        total_jobs = len(jobs)
        total_applications = len(applications)
        
        # Applications by status
        status_counts = {}
        for app in applications:
            status = app.get('status', 'submitted')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Average scores
        scores = [app['overall_score'] for app in applications if 'overall_score' in app]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Applications over time (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_apps = [app for app in applications if app.get('applied_date', datetime.min) > thirty_days_ago]
        
        # Top skills in demand
        all_skills = []
        for job in jobs:
            all_skills.extend(job.get('required_skills', []))
        
        from collections import Counter
        skill_counts = Counter(all_skills)
        top_skills = [{'skill': k, 'count': v} for k, v in skill_counts.most_common(10)]
        
        return jsonify({
            'summary': {
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'avg_score': round(avg_score, 2),
                'applications_last_30_days': len(recent_apps)
            },
            'applications_by_status': status_counts,
            'top_skills': top_skills
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/fairness/<job_id>', methods=['GET'])
@jwt_required()
def get_fairness_audit(job_id):
    """Get fairness audit report for a job"""
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
        
        if role not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can view fairness audits'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        candidates_collection = db['candidates']
        
        # Verify job ownership
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != user_id and role != 'admin':
            return jsonify({'error': 'Not authorized'}), 403
        
        # Get applications
        applications = list(applications_collection.find({'job_id': job_id}))
        
        if not applications:
            return jsonify({
                'message': 'No applications yet',
                'job_id': job_id
            }), 200
        
        # For demo purposes, simulate demographic data
        # In production, this would come from opt-in candidate data
        import random
        applications_data = []
        for app in applications:
            # Simulate protected attributes (for demo only)
            app_data = {
                'application_id': str(app['_id']),
                'decision': 1 if app.get('decision') == 'Hire' else 0,
                'score': app.get('overall_score', 0),
                'gender': random.choice(['male', 'female', 'other']),
                'age_group': random.choice(['18-25', '26-35', '36-45', '46+']),
                'ethnicity': random.choice(['group_a', 'group_b', 'group_c'])
            }
            applications_data.append(app_data)
        
        # Generate fairness report
        report = generate_fairness_report(
            job_id=job_id,
            applications_data=applications_data,
            protected_attributes=['gender', 'age_group', 'ethnicity']
        )
        
        # Calculate overall fairness score
        bias_count = sum(1 for analysis in report['analyses'].values() if analysis.get('bias_detected'))
        fairness_score = max(0, 100 - (bias_count * 20))
        
        badge = get_fairness_badge(fairness_score)
        
        report['fairness_score'] = fairness_score
        report['fairness_badge'] = badge
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transparency/<application_id>', methods=['GET'])
@jwt_required()
def get_transparency_report(application_id):
    """Get transparency report for an application"""
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
        
        db = get_db()
        applications_collection = db['applications']
        jobs_collection = db['jobs']
        
        # Get application
        application = applications_collection.find_one({'_id': ObjectId(application_id)})
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check authorization
        if role == 'candidate' and application['candidate_id'] != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        if role == 'recruiter':
            job = jobs_collection.find_one({'_id': ObjectId(application['job_id'])})
            if str(job['recruiter_id']) != user_id:
                return jsonify({'error': 'Not authorized'}), 403
        
        # Generate transparency report
        job = jobs_collection.find_one({'_id': ObjectId(application['job_id'])})
        
        report = {
            'application_id': application_id,
            'job_title': job['title'] if job else '',
            'applied_date': application.get('applied_date'),
            'status': application.get('status'),
            'decision': application.get('decision'),
            
            'scoring_breakdown': {
                'resume_match': application.get('resume_match_score', 0),
                'skill_match': application.get('skill_match_score', 0),
                'cci_score': application.get('cci_score', 0),
                'overall_score': application.get('overall_score', 0)
            },
            
            'matched_skills': application.get('matched_skills', []),
            'missing_skills': list(set(job.get('required_skills', [])) - set(application.get('matched_skills', []))),
            
            'decision_rationale': get_decision_rationale(application),
            'improvement_suggestions': get_improvement_suggestions(application, job)
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_decision_rationale(application):
    """Generate decision rationale"""
    decision = application.get('decision')
    score = application.get('overall_score', 0)
    
    if decision == 'Hire':
        return f"Strong match with overall score of {score:.1f}%. Candidate demonstrates required skills and experience."
    elif decision == 'Review':
        return f"Moderate match with score of {score:.1f}%. Candidate shows potential but may need further evaluation."
    else:
        return f"Limited match with score of {score:.1f}%. Candidate does not meet minimum requirements at this time."

def get_improvement_suggestions(application, job):
    """Generate improvement suggestions"""
    suggestions = []
    
    skill_match = application.get('skill_match_score', 0)
    if skill_match < 0.5:
        missing = set(job.get('required_skills', [])) - set(application.get('matched_skills', []))
        suggestions.append(f"Develop skills in: {', '.join(list(missing)[:5])}")
    
    cci_score = application.get('cci_score')
    if cci_score and cci_score < 60:
        suggestions.append("Build more consistent career progression with longer tenures")
    
    resume_score = application.get('resume_match_score', 0)
    if resume_score < 0.4:
        suggestions.append("Tailor resume to better highlight relevant experience for this role")
    
    return suggestions
