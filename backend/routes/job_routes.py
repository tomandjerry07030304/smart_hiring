from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db
from backend.models.job import Job, Application
from backend.utils.matching import extract_skills

bp = Blueprint('jobs', __name__)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job posting (recruiter only)"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is recruiter
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can create job postings'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract skills from job description
        job_skills = data.get('required_skills', [])
        if not job_skills:
            job_skills = extract_skills(data['description'])
        
        # Create job
        job = Job(
            title=data['title'],
            description=data['description'],
            recruiter_id=current_user['user_id'],
            company_name=data.get('company_name', ''),
            location=data.get('location', ''),
            job_type=data.get('job_type', 'Full-time'),
            required_skills=job_skills,
            experience_required=data.get('experience_required', 0),
            salary_range=data.get('salary_range', {}),
            deadline=data.get('deadline', None)
        )
        
        db = get_db()
        jobs_collection = db['jobs']
        result = jobs_collection.insert_one(job.to_dict())
        
        return jsonify({
            'message': 'Job created successfully',
            'job_id': str(result.inserted_id),
            'required_skills': job_skills
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_jobs():
    """Get list of all active job postings"""
    try:
        db = get_db()
        jobs_collection = db['jobs']
        
        # Get query parameters
        status = request.args.get('status', 'open')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Query jobs
        query = {'status': status}
        jobs = list(jobs_collection.find(query).sort('posted_date', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['recruiter_id'] = str(job['recruiter_id'])
        
        return jsonify({
            'jobs': jobs,
            'count': len(jobs),
            'total': jobs_collection.count_documents(query)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details by ID"""
    try:
        db = get_db()
        jobs_collection = db['jobs']
        
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        job['_id'] = str(job['_id'])
        job['recruiter_id'] = str(job['recruiter_id'])
        
        return jsonify(job), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job posting (recruiter only, own jobs)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can update jobs'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        
        # Check if job exists and user owns it
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Not authorized to update this job'}), 403
        
        data = request.get_json()
        
        # Fields that can be updated
        allowed_fields = ['title', 'description', 'company_name', 'location', 'job_type', 
                         'required_skills', 'experience_required', 'salary_range', 'status', 'deadline']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['updated_at'] = datetime.utcnow()
        
        result = jobs_collection.update_one(
            {'_id': ObjectId(job_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Job updated successfully'}), 200
        else:
            return jsonify({'message': 'No changes made'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>/applications', methods=['GET'])
@jwt_required()
def get_job_applications(job_id):
    """Get all applications for a job (recruiter only)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can view applications'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Verify job ownership
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Not authorized'}), 403
        
        # Get applications
        applications = list(applications_collection.find({'job_id': job_id}).sort('overall_score', -1))
        
        # Convert ObjectId to string
        for app in applications:
            app['_id'] = str(app['_id'])
        
        return jsonify({
            'job_id': job_id,
            'applications': applications,
            'count': len(applications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
