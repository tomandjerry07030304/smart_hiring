"""
AI Interview Routes
Endpoints for AI-powered interview question generation and management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db
from backend.services.ai_interviewer_service import (
    generate_interview_questions,
    evaluate_answer,
    create_interview_schedule
)
from backend.services.ranking_service import rank_candidates_for_job, get_candidate_insights

bp = Blueprint('ai_interview', __name__)


def get_user_info(current_user):
    """Helper to extract user_id and role from JWT identity"""
    if isinstance(current_user, str):
        user_id = current_user
        db = get_db()
        user = db['users'].find_one({'_id': ObjectId(user_id)})
        return user_id, user.get('role') if user else None
    return current_user.get('user_id'), current_user.get('role')


@bp.route('/generate-questions', methods=['POST'])
@jwt_required()
def generate_questions():
    """
    Generate AI interview questions for a job
    
    POST /api/ai-interview/generate-questions
    Body: {
        "job_id": "job123",
        "num_questions": 10,
        "include_behavioral": true
    }
    """
    try:
        user_id, role = get_user_info(get_jwt_identity())
        
        if role not in ['company', 'recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can generate interview questions'}), 403
        
        data = request.get_json()
        job_id = data.get('job_id')
        num_questions = data.get('num_questions', 10)
        include_behavioral = data.get('include_behavioral', True)
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        # Get job details
        db = get_db()
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Verify ownership
        if str(job['recruiter_id']) != user_id and role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate questions
        questions = generate_interview_questions(
            job=job,
            num_questions=num_questions,
            include_behavioral=include_behavioral
        )
        
        # Save to database
        interview_set = {
            'job_id': job_id,
            'job_title': job.get('title'),
            'recruiter_id': user_id,
            'questions': questions,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        result = db['interview_questions'].insert_one(interview_set)
        
        return jsonify({
            'message': 'Interview questions generated successfully',
            'interview_set_id': str(result.inserted_id),
            'questions': questions,
            'total_questions': len(questions)
        }), 201
        
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/questions/<job_id>', methods=['GET'])
@jwt_required()
def get_job_interview_questions(job_id):
    """Get interview questions for a job"""
    try:
        user_id, role = get_user_info(get_jwt_identity())
        
        db = get_db()
        
        # Get latest question set for this job
        question_set = db['interview_questions'].find_one(
            {'job_id': job_id, 'is_active': True},
            sort=[('created_at', -1)]
        )
        
        if not question_set:
            return jsonify({'message': 'No questions generated yet', 'questions': []}), 200
        
        # Convert ObjectId to string
        question_set['_id'] = str(question_set['_id'])
        question_set['created_at'] = question_set['created_at'].isoformat()
        
        return jsonify(question_set), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/evaluate-answer', methods=['POST'])
@jwt_required()
def evaluate_candidate_answer():
    """
    Evaluate a candidate's answer to an interview question
    
    POST /api/ai-interview/evaluate-answer
    Body: {
        "question_id": "Q1",
        "question": {...},
        "answer": "candidate's answer text"
    }
    """
    try:
        data = request.get_json()
        
        question = data.get('question')
        answer = data.get('answer', '')
        
        if not question or not answer:
            return jsonify({'error': 'question and answer are required'}), 400
        
        # Evaluate the answer
        evaluation = evaluate_answer(question, answer)
        
        return jsonify(evaluation), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/schedule', methods=['POST'])
@jwt_required()
def create_schedule():
    """
    Create an interview schedule
    
    POST /api/ai-interview/schedule
    Body: {
        "interview_type": "mixed",  // technical, behavioral, or mixed
        "duration_minutes": 60,
        "application_id": "app123"
    }
    """
    try:
        user_id, role = get_user_info(get_jwt_identity())
        
        if role not in ['company', 'recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can schedule interviews'}), 403
        
        data = request.get_json()
        interview_type = data.get('interview_type', 'mixed')
        duration = data.get('duration_minutes', 60)
        application_id = data.get('application_id')
        
        # Generate schedule
        schedule = create_interview_schedule(interview_type, duration)
        
        # Save to database
        if application_id:
            db = get_db()
            interview_record = {
                'application_id': application_id,
                'recruiter_id': user_id,
                'schedule': schedule,
                'status': 'scheduled',
                'created_at': datetime.utcnow()
            }
            
            result = db['interviews'].insert_one(interview_record)
            schedule['interview_id'] = str(result.inserted_id)
        
        return jsonify(schedule), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/rank-candidates', methods=['POST'])
@jwt_required()
def rank_candidates():
    """
    Rank candidates for a job using ML
    
    POST /api/ai-interview/rank-candidates
    Body: {
        "job_id": "job123"
    }
    """
    try:
        user_id, role = get_user_info(get_jwt_identity())
        
        if role not in ['company', 'recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can rank candidates'}), 403
        
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        db = get_db()
        
        # Get job
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Verify ownership
        if str(job['recruiter_id']) != user_id and role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get applications for this job
        applications = list(db['applications'].find({'job_id': job_id}))
        
        if not applications:
            return jsonify({'message': 'No applications found', 'ranked_candidates': []}), 200
        
        # Get candidate profiles
        candidate_profiles = []
        for app in applications:
            candidate = db['candidates'].find_one({'user_id': app['candidate_id']})
            if candidate:
                candidate['application_id'] = str(app['_id'])
                candidate['application_status'] = app.get('status')
                candidate_profiles.append(candidate)
        
        # Rank candidates
        ranked = rank_candidates_for_job(candidate_profiles, job)
        
        # Format response
        for candidate in ranked:
            candidate['_id'] = str(candidate.get('_id'))
            if 'user_id' in candidate:
                user = db['users'].find_one({'_id': ObjectId(candidate['user_id'])})
                if user:
                    candidate['name'] = user.get('full_name', 'Unknown')
                    candidate['email'] = user.get('email')
        
        return jsonify({
            'job_id': job_id,
            'job_title': job.get('title'),
            'total_candidates': len(ranked),
            'ranked_candidates': ranked
        }), 200
        
    except Exception as e:
        print(f"Error ranking candidates: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/candidate-insights/<candidate_id>/<job_id>', methods=['GET'])
@jwt_required()
def get_insights(candidate_id, job_id):
    """Get ML-powered insights for a candidate"""
    try:
        user_id, role = get_user_info(get_jwt_identity())
        
        if role not in ['company', 'recruiter', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db = get_db()
        
        # Get candidate and job
        candidate = db['candidates'].find_one({'user_id': candidate_id})
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        
        if not candidate or not job:
            return jsonify({'error': 'Candidate or job not found'}), 404
        
        # Get insights
        insights = get_candidate_insights(candidate, job)
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
