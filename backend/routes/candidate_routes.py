from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import os

from backend.models.database import get_db
from backend.models.job import Application
from backend.models.user import Candidate
from backend.utils.resume_parser import extract_text_from_file, anonymize_text
from backend.utils.matching import extract_skills, analyze_candidate
from backend.utils.cci_calculator import calculate_career_consistency_index

bp = Blueprint('candidates', __name__)

@bp.route('/upload-resume', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload and parse candidate resume"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'candidate':
            return jsonify({'error': 'Only candidates can upload resumes'}), 403
        
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Extract text from file
        file_data = file.read()
        resume_text = extract_text_from_file(file_data, file.filename)
        
        if not resume_text:
            return jsonify({'error': 'Could not extract text from resume'}), 400
        
        # Anonymize resume
        anonymized_text = anonymize_text(resume_text)
        
        # Extract skills
        skills = extract_skills(resume_text)
        
        # Get experience data from request (optional)
        experience_data = request.form.get('experience', '[]')
        import json
        try:
            experience = json.loads(experience_data)
        except:
            experience = []
        
        # Calculate CCI if experience is provided
        cci_result = None
        if experience:
            cci_result = calculate_career_consistency_index(experience)
        
        # Update candidate profile
        db = get_db()
        candidates_collection = db['candidates']
        
        update_data = {
            'resume_file': file.filename,
            'resume_text': resume_text,
            'anonymized_resume': anonymized_text,
            'skills': skills,
            'experience': experience,
            'updated_at': datetime.utcnow()
        }
        
        if cci_result:
            update_data['cci_score'] = cci_result['cci_score']
        
        result = candidates_collection.update_one(
            {'user_id': current_user['user_id']},
            {'$set': update_data},
            upsert=True
        )
        
        # Mark profile as completed
        users_collection = db['users']
        users_collection.update_one(
            {'_id': ObjectId(current_user['user_id'])},
            {'$set': {'profile_completed': True}}
        )
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'skills_found': skills,
            'skills_count': len(skills),
            'cci': cci_result,
            'resume_length': len(resume_text)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/apply/<job_id>', methods=['POST'])
@jwt_required()
def apply_to_job(job_id):
    """Apply to a job posting"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'candidate':
            return jsonify({'error': 'Only candidates can apply to jobs'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        candidates_collection = db['candidates']
        applications_collection = db['applications']
        
        # Check if job exists
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job['status'] != 'open':
            return jsonify({'error': 'Job is not accepting applications'}), 400
        
        # Check if already applied
        existing_app = applications_collection.find_one({
            'job_id': job_id,
            'candidate_id': current_user['user_id']
        })
        if existing_app:
            return jsonify({'error': 'Already applied to this job'}), 409
        
        # Get candidate profile
        candidate = candidates_collection.find_one({'user_id': current_user['user_id']})
        if not candidate:
            return jsonify({'error': 'Complete your profile first'}), 400
        
        if not candidate.get('resume_text'):
            return jsonify({'error': 'Upload your resume first'}), 400
        
        # Analyze candidate fit
        analysis = analyze_candidate(
            job_description=job['description'],
            job_skills=job.get('required_skills', []),
            resume_text=candidate.get('anonymized_resume', ''),
            resume_skills=candidate.get('skills', []),
            cci_score=candidate.get('cci_score')
        )
        
        # Create application
        application = Application(
            job_id=job_id,
            candidate_id=current_user['user_id'],
            resume_match_score=analysis['tfidf_score'],
            skill_match_score=analysis['skill_match'],
            overall_score=analysis['overall_score'],
            cci_score=analysis['cci_score'],
            matched_skills=analysis['matched_skills'],
            decision=analysis['decision']
        )
        
        result = applications_collection.insert_one(application.to_dict())
        
        # Update job application count
        jobs_collection.update_one(
            {'_id': ObjectId(job_id)},
            {'$inc': {'applications_count': 1}}
        )
        
        # Update candidate applications list
        candidates_collection.update_one(
            {'user_id': current_user['user_id']},
            {'$push': {'applications': job_id}}
        )
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application_id': str(result.inserted_id),
            'score': analysis['overall_score'],
            'decision': analysis['decision'],
            'matched_skills': analysis['matched_skills'],
            'recommendations': analysis['recommendations']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Get candidate's own applications"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'candidate':
            return jsonify({'error': 'Only candidates can view their applications'}), 403
        
        db = get_db()
        applications_collection = db['applications']
        jobs_collection = db['jobs']
        
        # Get applications
        applications = list(applications_collection.find(
            {'candidate_id': current_user['user_id']}
        ).sort('applied_date', -1))
        
        # Enrich with job details
        for app in applications:
            app['_id'] = str(app['_id'])
            job = jobs_collection.find_one({'_id': ObjectId(app['job_id'])})
            if job:
                app['job_title'] = job['title']
                app['company_name'] = job.get('company_name', '')
        
        return jsonify({
            'applications': applications,
            'count': len(applications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_candidate_profile():
    """Get candidate profile details"""
    try:
        current_user = get_jwt_identity()
        
        db = get_db()
        candidates_collection = db['candidates']
        
        candidate = candidates_collection.find_one({'user_id': current_user['user_id']})
        if not candidate:
            return jsonify({'error': 'Profile not found'}), 404
        
        candidate['_id'] = str(candidate['_id'])
        # Don't send full resume text, just metadata
        if 'resume_text' in candidate:
            candidate['resume_uploaded'] = True
            del candidate['resume_text']
            del candidate['anonymized_resume']
        
        return jsonify(candidate), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
