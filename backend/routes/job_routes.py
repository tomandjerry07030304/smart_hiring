from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
        print("🎯 Job creation attempt")
        user_id = get_jwt_identity()  # This is now a string (user_id)
        claims = get_jwt()  # This contains additional claims like 'role'
        role = claims.get('role', 'candidate')
        
        print(f"👤 Current user ID: {user_id}, Role: {role}")
        
        # Check if user is recruiter/company/admin
        if role not in ['recruiter', 'company', 'admin']:
            print(f"❌ Access denied - role: {role}")
            return jsonify({'error': 'Only recruiters/companies can create job postings'}), 403
        
        data = request.get_json()
        print(f"📦 Received job data: {list(data.keys())}")
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print(f"✅ Validation passed - Title: {data['title'][:50]}...")
        
        # Extract skills from job description
        job_skills = data.get('required_skills', [])
        if not job_skills:
            job_skills = extract_skills(data['description'])
        
        print(f"🔧 Skills: {job_skills}")
        
        # Create job
        job = Job(
            title=data['title'],
            description=data['description'],
            recruiter_id=user_id,  # Use the user_id from JWT identity
            company_name=data.get('company_name', ''),
            location=data.get('location', ''),
            job_type=data.get('job_type', 'Full-time'),
            required_skills=job_skills,
            experience_required=data.get('experience_required', 0),
            salary_range=data.get('salary_range', {}),
            deadline=data.get('deadline', None)
        )
        
        print("💾 Inserting job into database...")
        db = get_db()
        jobs_collection = db['jobs']
        result = jobs_collection.insert_one(job.to_dict())
        
        print(f"✅ Job created with ID: {result.inserted_id}")
        return jsonify({
            'message': 'Job created successfully',
            'job_id': str(result.inserted_id),
            'required_skills': job_skills
        }), 201
        
    except Exception as e:
        print(f"❌ Job creation error: {str(e)}")
        import traceback
        traceback.print_exc()
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

@bp.route('/company', methods=['GET'])
@jwt_required()
def get_company_jobs():
    """Get jobs posted by the logged-in recruiter/company"""
    try:
        user_id = get_jwt_identity()
        print(f"📋 Fetching jobs for recruiter: {user_id}")
        
        db = get_db()
        jobs_collection = db['jobs']
        
        # Get query parameters
        status = request.args.get('status', 'open')
        
        # Query jobs for this recruiter
        query = {'recruiter_id': user_id}
        if status:
            query['status'] = status
            
        jobs = list(jobs_collection.find(query).sort('posted_date', -1))
        
        print(f"✅ Found {len(jobs)} jobs for recruiter {user_id}")
        
        # Convert ObjectId to string
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['recruiter_id'] = str(job['recruiter_id'])
            # Convert datetime to ISO format string if present
            if 'posted_date' in job:
                job['posted_date'] = job['posted_date'].isoformat() if hasattr(job['posted_date'], 'isoformat') else str(job['posted_date'])
            if 'created_at' in job:
                job['created_at'] = job['created_at'].isoformat() if hasattr(job['created_at'], 'isoformat') else str(job['created_at'])
            if 'updated_at' in job:
                job['updated_at'] = job['updated_at'].isoformat() if hasattr(job['updated_at'], 'isoformat') else str(job['updated_at'])
        
        return jsonify({
            'jobs': jobs,
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching company jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/company/stats', methods=['GET'])
@jwt_required()
def get_company_stats():
    """Get dashboard statistics for the logged-in recruiter/company"""
    try:
        user_id = get_jwt_identity()
        print(f"📊 Fetching stats for recruiter: {user_id}")
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Count active jobs
        active_jobs = jobs_collection.count_documents({
            'recruiter_id': user_id,
            'status': 'open'
        })
        
        # Get all job IDs for this recruiter
        recruiter_jobs = list(jobs_collection.find(
            {'recruiter_id': user_id},
            {'_id': 1}
        ))
        job_ids = [str(job['_id']) for job in recruiter_jobs]
        
        # Count total applications
        total_applications = applications_collection.count_documents({
            'job_id': {'$in': job_ids}
        }) if job_ids else 0
        
        # Count applications by status
        applications_by_status = {}
        if job_ids:
            pipeline = [
                {'$match': {'job_id': {'$in': job_ids}}},
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ]
            for doc in applications_collection.aggregate(pipeline):
                applications_by_status[doc['_id']] = doc['count']
        
        print(f"✅ Stats: {active_jobs} jobs, {total_applications} applications")
        
        return jsonify({
            'active_jobs': active_jobs,
            'total_jobs': len(recruiter_jobs),
            'total_applications': total_applications,
            'shortlisted': applications_by_status.get('shortlisted', 0),
            'interviewed': applications_by_status.get('screening', 0),
            'hired': applications_by_status.get('hired', 0)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/company/applications', methods=['GET'])
@jwt_required()
def get_company_applications():
    """Get all applications for jobs posted by the logged-in recruiter"""
    try:
        user_id = get_jwt_identity()
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        users_collection = db['users']
        
        # Get all job IDs for this recruiter
        recruiter_jobs = list(jobs_collection.find(
            {'recruiter_id': user_id},
            {'_id': 1, 'title': 1, 'company_name': 1}
        ))
        
        if not recruiter_jobs:
            return jsonify({'applications': [], 'count': 0}), 200
            
        # Create a map of job_id to job info for enrichment
        job_map = {str(job['_id']): {'title': job['title'], 'company_name': job.get('company_name', '')} for job in recruiter_jobs}
        job_ids = list(job_map.keys())
        
        # Get applications for these jobs
        applications = list(applications_collection.find(
            {'job_id': {'$in': job_ids}}
        ).sort('applied_date', -1))
        
        # Enrich applications with job and candidate information
        for app in applications:
            app['_id'] = str(app['_id'])
            job_info = job_map.get(app['job_id'], {})
            app['job_title'] = job_info.get('title', 'Unknown Job')
            app['company_name'] = job_info.get('company_name', '')
            
            # Get candidate information
            candidate_id = app.get('candidate_id')
            if candidate_id:
                candidate_user = users_collection.find_one({'_id': ObjectId(candidate_id)})
                if candidate_user:
                    app['candidate_name'] = candidate_user.get('full_name', 'Unknown')
                    app['candidate_email'] = candidate_user.get('email', '')
                else:
                    app['candidate_name'] = 'Unknown'
                    app['candidate_email'] = ''
            else:
                app['candidate_name'] = 'Unknown'
                app['candidate_email'] = ''
            
            # Ensure dates are properly formatted
            if 'applied_date' in app:
                app['applied_at'] = app['applied_date'].isoformat() if hasattr(app['applied_date'], 'isoformat') else str(app['applied_date'])
            elif 'applied_at' in app:
                app['applied_at'] = app['applied_at'].isoformat() if hasattr(app['applied_at'], 'isoformat') else str(app['applied_at'])
            else:
                app['applied_at'] = datetime.utcnow().isoformat()
            
            # Ensure score fields exist
            if 'overall_score' not in app:
                app['overall_score'] = 0
        
        return jsonify({
            'applications': applications,
            'count': len(applications)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching company applications: {str(e)}")
        import traceback
        traceback.print_exc()
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
