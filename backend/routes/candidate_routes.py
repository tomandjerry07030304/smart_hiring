from flask import Blueprint, request, jsonify, Response, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import os
import io
import logging

from backend.models.database import get_db
from backend.models.job import Application
from backend.models.user import Candidate
from backend.services.resume_parser_service import extract_text_from_file
from backend.utils.cci_calculator import calculate_career_consistency_index
from backend.utils.email_service import email_service
from backend.tasks.email_tasks import send_new_application_alert, send_application_confirmation
from backend.routes.audit_routes import log_audit_event
from backend.security.rbac import require_role

# P0 ML: Import new ML services
try:
    from backend.services.ml_matching_service import get_ml_matching_service, analyze_candidate
    from backend.services.anonymization_service import anonymize_text, get_anonymizer
    ML_SERVICES_AVAILABLE = True
except ImportError:
    from backend.utils.matching import extract_skills, analyze_candidate
    from backend.services.resume_parser_service import anonymize_text
    ML_SERVICES_AVAILABLE = False
    logging.warning("⚠️ ML services not available - using basic matching")

logger = logging.getLogger(__name__)

# Gap 8: Allowed values for voluntary self-identification
VALID_GENDERS = {'male', 'female', 'non-binary', 'other', 'prefer_not_to_say'}
VALID_AGE_GROUPS = {'18-25', '26-35', '36-45', '46-55', '56+', 'prefer_not_to_say'}
VALID_ETHNICITIES = {
    'group_a', 'group_b', 'group_c', 'group_d', 'group_e', 'prefer_not_to_say'
}

bp = Blueprint('candidates', __name__)

@bp.route('/upload-resume', methods=['POST'])
@jwt_required()
@require_role(['candidate', 'admin'])
def upload_resume():
    """
    Upload and parse candidate resume with automatic score invalidation.
    
    CRITICAL: When resume changes, ALL existing application scores are
    automatically re-calculated to prevent stale match scores.
    """
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
        
        # Use production-grade upload service with score invalidation
        try:
            from backend.services.resume_upload_service import upload_resume as process_resume
            db = get_db()
            result = process_resume(user_id, file, db)
            
            if not result.success:
                return jsonify({'error': result.error}), 400
            
            response = {
                'message': 'Resume uploaded successfully',
                'skills_found': result.skills_extracted,
                'skills_count': len(result.skills_extracted),
                'was_duplicate': result.was_duplicate,
                'applications_rescored': result.applications_rescored,
                'resume_hash': result.resume_hash[:16] if result.resume_hash else None
            }
            
            if result.was_duplicate:
                response['message'] = 'Resume unchanged - no re-processing needed'
            elif result.applications_rescored > 0:
                response['message'] = f'Resume uploaded and {result.applications_rescored} application(s) re-scored'
            
            logger.info(f"✅ Resume processed: {response}")
            return jsonify(response), 200
            
        except ImportError as ie:
            logger.warning(f"Resume upload service not available, using legacy: {ie}")
            # Fallback to legacy implementation if service unavailable
            return _legacy_upload_resume(user_id, file)
        
    except Exception as e:
        logger.exception(f"Resume upload error: {e}")
        return jsonify({'error': str(e)}), 500


def _legacy_upload_resume(user_id: str, file):
    """Legacy upload handler - used only if new service unavailable"""
    from backend.services.resume_parser_service import extract_text_from_file
    
    file_data = file.read()
    resume_text = extract_text_from_file(file_data, file.filename)
    
    if not resume_text:
        return jsonify({'error': 'Could not extract text from resume'}), 400
    
    # Basic anonymization
    if ML_SERVICES_AVAILABLE:
        try:
            anonymizer = get_anonymizer()
            anonymization_result = anonymizer.anonymize(resume_text)
            anonymized_text = anonymization_result['anonymized_text']
        except Exception:
            from backend.services.resume_parser_service import anonymize_text
            anonymized_text = anonymize_text(resume_text)
    else:
        from backend.services.resume_parser_service import anonymize_text
        anonymized_text = anonymize_text(resume_text)
    
    # Basic skill extraction
    if ML_SERVICES_AVAILABLE:
        try:
            ml_service = get_ml_matching_service()
            skills = ml_service.extract_skills(resume_text)
        except Exception:
            from backend.utils.matching import extract_skills
            skills = extract_skills(resume_text)
    else:
        from backend.utils.matching import extract_skills
        skills = extract_skills(resume_text)
    
    # Update candidate
    db = get_db()
    db['candidates'].update_one(
        {'user_id': user_id},
        {'$set': {
            'resume_file': file.filename,
            'resume_text': resume_text,
            'anonymized_resume': anonymized_text,
            'skills': skills,
            'updated_at': datetime.utcnow()
        }},
        upsert=True
    )
    
    db['users'].update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'profile_completed': True}}
    )
    
    return jsonify({
        'message': 'Resume uploaded (legacy mode)',
        'skills_found': skills,
        'skills_count': len(skills),
        'warning': 'Existing applications NOT re-scored in legacy mode'
    }), 200


@bp.route('/resume/<application_id>', methods=['GET'])
@jwt_required()
def download_resume(application_id):
    """Download resume for an application - accessible by recruiters and the candidate themselves"""
    try:
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id')

        db = get_db()
        users_collection = db['users']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        role = user.get('role', '')

        # Look up the application
        application = db['applications'].find_one({'_id': ObjectId(application_id)})
        if not application:
            return jsonify({'error': 'Application not found'}), 404

        candidate_id = application.get('candidate_id')

        # Authorization: only the candidate themselves, company, recruiter, or admin
        if role == 'candidate' and str(user_id) != str(candidate_id):
            return jsonify({'error': 'Unauthorized'}), 403

        # Get candidate's resume data
        candidate = db['candidates'].find_one({'user_id': str(candidate_id)})
        if not candidate:
            return jsonify({'error': 'Candidate profile not found'}), 404

        resume_text = candidate.get('resume_text', '')
        resume_file = candidate.get('resume_file', 'resume.txt')

        if not resume_text:
            return jsonify({'error': 'No resume uploaded for this candidate'}), 404

        # Check if the original uploaded file exists on disk
        uploads_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
        candidate_upload_dir = os.path.join(uploads_folder, str(candidate_id))
        disk_file_path = os.path.join(candidate_upload_dir, resume_file) if resume_file else None

        if disk_file_path and os.path.exists(disk_file_path):
            # Serve actual file from disk
            ext = resume_file.rsplit('.', 1)[-1].lower() if '.' in resume_file else 'txt'
            mime_types = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'doc': 'application/msword',
                'txt': 'text/plain'
            }
            mime = mime_types.get(ext, 'application/octet-stream')
            with open(disk_file_path, 'rb') as f:
                file_data = f.read()
            response = make_response(file_data)
            response.headers['Content-Type'] = mime
            response.headers['Content-Disposition'] = f'attachment; filename="{resume_file}"'
            return response

        # Fallback: generate a plain-text resume from stored text
        # Get candidate user info for a nice header
        candidate_user = users_collection.find_one({'_id': ObjectId(candidate_id)})
        candidate_name = candidate_user.get('full_name', 'Candidate') if candidate_user else 'Candidate'
        candidate_email = candidate_user.get('email', '') if candidate_user else ''
        skills = candidate.get('skills', [])

        # Build text resume
        lines = []
        lines.append("=" * 60)
        lines.append(f"  RESUME - {candidate_name}")
        lines.append("=" * 60)
        if candidate_email:
            lines.append(f"  Email: {candidate_email}")
        if skills:
            lines.append(f"  Skills: {', '.join(skills[:20])}")
        lines.append("-" * 60)
        lines.append("")
        lines.append(resume_text)
        content = "\n".join(lines)

        response = make_response(content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        safe_name = resume_file if resume_file else f'resume_{candidate_name.replace(" ", "_")}.txt'
        if not safe_name.endswith('.txt') and not safe_name.endswith('.pdf'):
            safe_name = safe_name.rsplit('.', 1)[0] + '.txt'
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_name}"'
        return response

    except Exception as e:
        logger.error(f"Resume download error: {e}")
        return jsonify({'error': 'Failed to download resume'}), 500


@bp.route('/apply/<job_id>', methods=['POST'])
@jwt_required()
@require_role(['candidate', 'admin'])
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
        
        # Get candidate profile first (needed for resume hash check)
        candidate = candidates_collection.find_one({'user_id': user_id})
        if not candidate:
            return jsonify({'error': 'Complete your profile first'}), 400
        
        if not candidate.get('resume_text'):
            return jsonify({'error': 'Upload your resume first'}), 400
        
        current_resume_hash = candidate.get('resume_hash', '')
        
        # Check if already applied - but allow re-apply if resume has been updated
        existing_app = applications_collection.find_one({
            'job_id': job_id,
            'candidate_id': user_id
        })
        
        is_reapplication = False
        if existing_app:
            # Check if resume has changed since last application
            previous_resume_hash = existing_app.get('resume_hash_at_application', '')
            
            if current_resume_hash and current_resume_hash == previous_resume_hash:
                # Resume unchanged - don't allow re-apply
                return jsonify({
                    'error': 'Already applied to this job',
                    'hint': 'Upload an updated resume to re-apply with improved qualifications'
                }), 409
            else:
                # Resume has changed - allow re-application by updating existing
                is_reapplication = True
                logger.info(f"🔄 Re-application allowed: resume hash changed from {previous_resume_hash[:8]}... to {current_resume_hash[:8]}...")
        
        # Analyze candidate fit
        analysis = analyze_candidate(
            job_description=job['description'],
            job_skills=job.get('required_skills', []),
            resume_text=candidate.get('anonymized_resume', ''),
            resume_skills=candidate.get('skills', []),
            cci_score=candidate.get('cci_score')
        )
        
        # Prepare application data
        application_data = {
            'job_id': job_id,
            'candidate_id': user_id,
            'resume_match_score': analysis['tfidf_score'],
            'skill_match_score': analysis['skill_match'],
            'overall_score': analysis['overall_score'],
            'cci_score': analysis['cci_score'],
            'matched_skills': analysis['matched_skills'],
            'decision': analysis['decision'],
            'resume_hash_at_application': current_resume_hash,  # Track which resume version
            # AUTO-SHORTLIST: Score >= 70 → shortlisted, else pending
            'status': 'shortlisted' if analysis['overall_score'] >= 70 else 'pending',
            'auto_status_reason': f"Auto-shortlisted (score: {analysis['overall_score']:.0f}%)" if analysis['overall_score'] >= 70 else None
        }
        
        if is_reapplication:
            # UPDATE existing application with new scores
            application_data['reapplied_at'] = datetime.utcnow()
            application_data['application_version'] = existing_app.get('application_version', 1) + 1
            
            applications_collection.update_one(
                {'_id': existing_app['_id']},
                {'$set': application_data}
            )
            application_id = str(existing_app['_id'])
            logger.info(f"✅ Re-application updated: {application_id} (version {application_data['application_version']})")
        else:
            # CREATE new application
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
            
            app_dict = application.to_dict()
            app_dict['resume_hash_at_application'] = current_resume_hash
            app_dict['application_version'] = 1
            
            result = applications_collection.insert_one(app_dict)
            application_id = str(result.inserted_id)
        
        # Log audit event for application submission
        log_audit_event(
            event_type='application_resubmitted' if is_reapplication else 'application_submitted',
            user_id=user_id,
            job_id=job_id,
            candidate_id=user_id,
            application_id=application_id,
            details={
                'job_title': job.get('title'),
                'anonymized': True,
                'is_reapplication': is_reapplication,
                'resume_hash': current_resume_hash[:16] if current_resume_hash else None
            },
            scores={
                'overall_score': analysis['overall_score'],
                'tfidf_score': analysis['tfidf_score'],
                'skill_match': analysis['skill_match'],
                'cci_score': analysis.get('cci_score'),
                'decision': analysis['decision']
            }
        )
        
        # Update job application count (ONLY for new applications, not re-applications)
        if not is_reapplication:
            jobs_collection.update_one(
                {'_id': ObjectId(job_id)},
                {'$inc': {'applications_count': 1}}
            )
            
            # Update candidate applications list (only for new)
            candidates_collection.update_one(
                {'user_id': user_id},
                {'$addToSet': {'applications': job_id}}  # Use addToSet to avoid duplicates
            )
        
        # Send email notifications
        try:
            users_collection = db['users']
            candidate_user = users_collection.find_one({'_id': ObjectId(user_id)})
            
            # Send confirmation email to candidate (Async)
            if candidate_user:
                send_application_confirmation.delay(
                    candidate_user.get('email'),
                    candidate_user.get('full_name'),
                    job.get('title'),
                    job.get('company_name', 'the company')
                )
            
            # Send alert email to recruiter (Async)
            recruiter_id = job.get('recruiter_id')
            if recruiter_id:
                recruiter_user = users_collection.find_one({'_id': ObjectId(recruiter_id)})
                if recruiter_user:
                    send_new_application_alert.delay(
                        recruiter_user.get('email'),
                        recruiter_user.get('full_name'),
                        candidate_user.get('full_name'),
                        job.get('title'),
                        analysis['overall_score']
                    )
        except Exception as email_error:
            print(f"⚠️ Application emails failed: {email_error}")
        
        # Return appropriate response
        if is_reapplication:
            return jsonify({
                'message': 'Application re-submitted with updated resume!',
                'application_id': application_id,
                'score': analysis['overall_score'],
                'score_improved': True,  # Could compare old vs new score
                'decision': analysis['decision'],
                'matched_skills': analysis['matched_skills'],
                'recommendations': analysis['recommendations']
            }), 200  # 200 for update, not 201
        else:
            return jsonify({
                'message': 'Application submitted successfully',
                'application_id': application_id,
                'score': analysis['overall_score'],
                'decision': analysis['decision'],
                'matched_skills': analysis['matched_skills'],
                'recommendations': analysis['recommendations']
            }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/applications', methods=['GET'])
@jwt_required()
@require_role(['candidate', 'admin'])
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
@require_role(['candidate', 'admin'])
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
@require_role(['candidate', 'admin'])
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


# ── Gap 8: Voluntary self-identification for fairness auditing ────────────────

@bp.route('/self-identification', methods=['PUT'])
@jwt_required()
@require_role(['candidate', 'admin'])
def update_self_identification():
    """
    Opt-in endpoint for candidates to voluntarily provide demographic data
    used *only* for aggregate fairness auditing.  Data is stored in the
    candidate profile and never exposed to individual recruiters.
    All fields are optional; sending ``{}`` clears stored demographics.
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, str) else current_user.get('user_id')

        data = request.get_json() or {}

        demographics: dict = {}

        # Validate each optional field against allowed value sets
        if 'gender' in data:
            val = str(data['gender']).lower().strip()
            if val not in VALID_GENDERS:
                return jsonify({
                    'error': f"Invalid gender value. Allowed: {sorted(VALID_GENDERS)}"
                }), 400
            demographics['gender'] = val

        if 'age_group' in data:
            val = str(data['age_group']).strip()
            if val not in VALID_AGE_GROUPS:
                return jsonify({
                    'error': f"Invalid age_group value. Allowed: {sorted(VALID_AGE_GROUPS)}"
                }), 400
            demographics['age_group'] = val

        if 'ethnicity' in data:
            val = str(data['ethnicity']).lower().strip()
            if val not in VALID_ETHNICITIES:
                return jsonify({
                    'error': f"Invalid ethnicity value. Allowed: {sorted(VALID_ETHNICITIES)}"
                }), 400
            demographics['ethnicity'] = val

        # Store consent timestamp
        demographics['consent_given_at'] = datetime.utcnow()
        demographics['updated_at'] = datetime.utcnow()

        db = get_db()
        db['candidates'].update_one(
            {'user_id': user_id},
            {'$set': {'demographics': demographics}},
            upsert=True,
        )

        return jsonify({
            'message': 'Self-identification data saved. This data is used only for aggregate fairness auditing.',
            'demographics': {k: v for k, v in demographics.items()
                             if k not in ('consent_given_at', 'updated_at')},
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/self-identification', methods=['DELETE'])
@jwt_required()
@require_role(['candidate', 'admin'])
def delete_self_identification():
    """Allow candidates to withdraw their self-identification data entirely."""
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, str) else current_user.get('user_id')

        db = get_db()
        db['candidates'].update_one(
            {'user_id': user_id},
            {'$unset': {'demographics': 1}},
        )

        return jsonify({'message': 'Self-identification data removed.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
