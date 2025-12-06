from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import os
import logging

from backend.models.database import get_db
from backend.models.job import Application
from backend.models.user import Candidate
from backend.utils.resume_parser import extract_text_from_file, anonymize_text
from backend.utils.matching import extract_skills, analyze_candidate
from backend.utils.cci_calculator import calculate_career_consistency_index
from backend.utils.email_service import email_service
from backend.routes.audit_routes import log_audit_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('candidates', __name__)

@bp.route('/upload-resume', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload and parse candidate resume"""
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
        
        if role != 'candidate':
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
        
        print(f"\n{'='*60}")
        print(f"📄 RESUME PROCESSING")
        print(f"File: {file.filename}")
        print(f"Size: {len(file_data)} bytes")
        print(f"Text length: {len(resume_text)} characters")
        print(f"Text preview: {resume_text[:200]}...")
        print(f"{'='*60}\n")
        
        # Anonymize resume
        anonymized_text = anonymize_text(resume_text)
        
        # Extract skills
        print(f"🔍 Extracting skills from resume text...")
        skills = extract_skills(resume_text)
        print(f"✅ Skills extracted: {len(skills)} skills found")
        print(f"📋 Skills list: {skills[:10]}..." if len(skills) > 10 else f"📋 Skills list: {skills}")
        print(f"{'='*60}\n")
        
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
            {'user_id': user_id},
            {'$set': update_data},
            upsert=True
        )
        
        # Mark profile as completed
        users_collection = db['users']
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
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
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
            # Fetch user role from database
            db = get_db()
            users_collection = db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user.get('role')
        else:
            user_id = current_user.get('user_id')
            role = current_user.get('role')
        
        if role != 'candidate':
            return jsonify({'error': 'Only candidates can apply to jobs'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        candidates_collection = db['candidates']
        applications_collection = db['applications']
        
        # Check if job exists
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.get('status', 'open') != 'open':
            return jsonify({'error': 'Job is not accepting applications'}), 400
        
        # Check if already applied
        existing_app = applications_collection.find_one({
            'job_id': job_id,
            'candidate_id': user_id
        })
        if existing_app:
            return jsonify({'error': 'Already applied to this job'}), 409
        
        # Get candidate profile
        candidate = candidates_collection.find_one({'user_id': user_id})
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
            candidate_id=user_id,
            resume_match_score=analysis['tfidf_score'],
            skill_match_score=analysis['skill_match'],
            overall_score=analysis['overall_score'],
            cci_score=analysis['cci_score'],
            matched_skills=analysis['matched_skills'],
            decision=analysis['decision']
        )
        
        result = applications_collection.insert_one(application.to_dict())
        application_id = str(result.inserted_id)
        
        # Log audit event for application submission
        log_audit_event(
            event_type='application_submitted',
            user_id=user_id,
            job_id=job_id,
            candidate_id=user_id,
            application_id=application_id,
            details={
                'job_title': job.get('title'),
                'anonymized': True
            },
            scores={
                'overall_score': analysis['overall_score'],
                'tfidf_score': analysis['tfidf_score'],
                'skill_match': analysis['skill_match'],
                'cci_score': analysis.get('cci_score'),
                'decision': analysis['decision']
            }
        )
        
        # Update job application count
        jobs_collection.update_one(
            {'_id': ObjectId(job_id)},
            {'$inc': {'applications_count': 1}}
        )
        
        # Update candidate applications list
        candidates_collection.update_one(
            {'user_id': user_id},
            {'$push': {'applications': job_id}}
        )
        
        # Send email notifications
        try:
            users_collection = db['users']
            candidate_user = users_collection.find_one({'_id': ObjectId(user_id)})
            
            # Send confirmation email to candidate
            if candidate_user:
                email_service.send_application_confirmation(
                    to_email=candidate_user.get('email'),
                    candidate_name=candidate_user.get('full_name'),
                    job_title=job.get('title'),
                    company_name=job.get('company_name', 'the company')
                )
            
            # Send alert email to recruiter
            recruiter_id = job.get('recruiter_id')
            if recruiter_id:
                recruiter_user = users_collection.find_one({'_id': ObjectId(recruiter_id)})
                if recruiter_user:
                    email_service.send_new_application_alert(
                        to_email=recruiter_user.get('email'),
                        recruiter_name=recruiter_user.get('full_name'),
                        candidate_name=candidate_user.get('full_name'),
                        job_title=job.get('title'),
                        match_score=analysis['overall_score']
                    )
        except Exception as email_error:
            print(f"⚠️ Application emails failed: {email_error}")
        
        # === NEW: AUTOMATIC FAIRNESS CHECK ===
        # Check if this job has multiple applications for potential bias
        logger.info(f"✅ Application {application_id} created - checking fairness...")
        
        try:
            # Count total applications for this job
            total_apps = applications_collection.count_documents({'job_id': job_id})
            
            if total_apps >= 5:  # Minimum threshold for fairness analysis
                logger.info(f"🔍 Job {job_id} now has {total_apps} applications - fairness analysis recommended")
                
                # Mark for recruiter review
                applications_collection.update_one(
                    {'_id': result.inserted_id},
                    {'$set': {'fairness_check_pending': True}}
                )
                
                # If >= 10 applications, run automatic preliminary fairness check
                if total_apps >= 10:
                    logger.info(f"⚖️ Running preliminary fairness check for job {job_id}...")
                    
                    # This will be used by recruiter when they shortlist
                    jobs_collection.update_one(
                        {'_id': ObjectId(job_id)},
                        {'$set': {
                            'fairness_analysis_ready': True,
                            'last_fairness_check': datetime.utcnow()
                        }}
                    )
        except Exception as fairness_error:
            logger.warning(f"⚠️ Fairness check failed: {fairness_error}")
        
        # === NEW: STATUS PROGRESSION TRACKING ===
        # Set up next steps in the hiring pipeline
        next_steps = {
            'current_status': 'screening',
            'next_status': 'assignment_pending',  # Will be triggered when test module is ready
            'pipeline_stages': [
                {'stage': 'screening', 'completed': True, 'completed_at': datetime.utcnow()},
                {'stage': 'assignment', 'completed': False, 'scheduled': False},
                {'stage': 'interview', 'completed': False, 'scheduled': False},
                {'stage': 'shortlisting', 'completed': False, 'decision': None}
            ]
        }
        
        # Update application with pipeline tracking
        applications_collection.update_one(
            {'_id': result.inserted_id},
            {'$set': {
                'pipeline_status': next_steps,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        
        logger.info(f"✅ Application {application_id} successfully created with score: {analysis['overall_score']:.2f}")
        
        return jsonify({
            'message': 'Application submitted successfully! You will receive updates via email.',
            'application_id': str(result.inserted_id),
            'score': analysis['overall_score'],
            'decision': analysis['decision'],
            'matched_skills': analysis['matched_skills'],
            'recommendations': analysis['recommendations'],
            'next_steps': 'Your application is being reviewed. You may be invited to take an assessment next.'
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Application submission failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Get candidate's own applications"""
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
        
        if role != 'candidate':
            return jsonify({'error': 'Only candidates can view their applications'}), 403
        
        db = get_db()
        applications_collection = db['applications']
        jobs_collection = db['jobs']
        
        # Get applications
        applications = list(applications_collection.find(
            {'candidate_id': user_id}
        ).sort('applied_date', -1))
        
        # Enrich with job details
        for app in applications:
            app['_id'] = str(app['_id'])
            job = jobs_collection.find_one({'_id': ObjectId(app['job_id'])})
            if job:
                app['job_title'] = job['title']
                app['company_name'] = job.get('company_name', 'Company')
                app['location'] = job.get('location', 'Remote')
            
            # Convert applied_date to applied_at for frontend compatibility
            if 'applied_date' in app:
                app['applied_at'] = app['applied_date']
        
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
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id')
        
        db = get_db()
        candidates_collection = db['candidates']
        users_collection = db['users']
        
        # Get or create candidate profile
        candidate = candidates_collection.find_one({'user_id': user_id})
        
        if not candidate:
            # Create default candidate profile
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            
            default_profile = {
                'user_id': user_id,
                'email': user.get('email', ''),
                'first_name': user.get('full_name', '').split()[0] if user.get('full_name') else '',
                'last_name': ' '.join(user.get('full_name', '').split()[1:]) if user.get('full_name') else '',
                'phone': '',
                'skills': [],
                'experience_years': 0,
                'education': '',
                'resume_file': None,
                'resume_uploaded': False,
                'applications': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = candidates_collection.insert_one(default_profile)
            default_profile['_id'] = str(result.inserted_id)
            
            return jsonify(default_profile), 200
        
        candidate['_id'] = str(candidate['_id'])
        # Don't send full resume text, just metadata
        if 'resume_text' in candidate:
            candidate['resume_uploaded'] = True
            del candidate['resume_text']
        if 'anonymized_resume' in candidate:
            del candidate['anonymized_resume']
        
        return jsonify(candidate), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_candidate_profile():
    """Update candidate profile details"""
    try:
        current_user = get_jwt_identity()
        
        # Handle both string and dict JWT identity formats
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id')
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('first_name') or not data.get('last_name'):
            return jsonify({'error': 'First name and last name are required'}), 400
        
        db = get_db()
        candidates_collection = db['candidates']
        users_collection = db['users']
        
        # Prepare update data
        update_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone': data.get('phone', ''),
            'skills': data.get('skills', []),
            'experience_years': float(data.get('experience', 0)),
            'education': data.get('education', ''),
            'bio': data.get('bio', ''),
            'location': data.get('location', ''),
            'linkedin': data.get('linkedin', ''),
            'portfolio': data.get('portfolio', ''),
            'updated_at': datetime.utcnow()
        }
        
        # Update candidate profile
        result = candidates_collection.update_one(
            {'user_id': user_id},
            {'$set': update_data},
            upsert=True
        )
        
        # Update user full_name in users collection
        full_name = f"{data.get('first_name')} {data.get('last_name')}"
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'full_name': full_name}}
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': update_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
