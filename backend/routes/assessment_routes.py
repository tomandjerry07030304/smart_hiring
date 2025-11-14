from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db
from backend.models.assessment import Assessment, AssessmentResponse, Interview

bp = Blueprint('assessments', __name__)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_assessment():
    """Create assessment for a job (recruiter only)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can create assessments'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['job_id', 'title', 'assessment_type', 'questions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create assessment
        assessment = Assessment(
            job_id=data['job_id'],
            title=data['title'],
            assessment_type=data['assessment_type'],
            duration_minutes=data.get('duration_minutes', 60),
            questions=data['questions'],
            passing_score=data.get('passing_score', 60)
        )
        
        db = get_db()
        assessments_collection = db['assessments']
        result = assessments_collection.insert_one(assessment.to_dict())
        
        return jsonify({
            'message': 'Assessment created successfully',
            'assessment_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/job/<job_id>', methods=['GET'])
def get_job_assessments(job_id):
    """Get assessments for a job"""
    try:
        db = get_db()
        assessments_collection = db['assessments']
        
        assessments = list(assessments_collection.find({
            'job_id': job_id,
            'is_active': True
        }))
        
        for assessment in assessments:
            assessment['_id'] = str(assessment['_id'])
        
        return jsonify({
            'assessments': assessments,
            'count': len(assessments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<assessment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assessment(assessment_id):
    """Submit assessment responses"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'candidate':
            return jsonify({'error': 'Only candidates can submit assessments'}), 403
        
        data = request.get_json()
        
        if 'answers' not in data or 'application_id' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        db = get_db()
        assessments_collection = db['assessments']
        responses_collection = db['assessment_responses']
        
        # Get assessment
        assessment = assessments_collection.find_one({'_id': ObjectId(assessment_id)})
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        # Calculate score (simple scoring for MCQ)
        answers = data['answers']
        questions = assessment['questions']
        
        correct_count = 0
        for i, answer in enumerate(answers):
            if i < len(questions):
                correct_answer = questions[i].get('correct_answer')
                if answer == correct_answer:
                    correct_count += 1
        
        score = correct_count
        percentage = (correct_count / len(questions)) * 100 if questions else 0
        passed = percentage >= assessment['passing_score']
        
        # Create response
        response = AssessmentResponse(
            assessment_id=assessment_id,
            candidate_id=current_user['user_id'],
            application_id=data['application_id'],
            answers=answers,
            score=score,
            percentage=round(percentage, 2),
            started_at=data.get('started_at'),
            completed_at=datetime.utcnow(),
            time_taken_minutes=data.get('time_taken_minutes', 0),
            passed=passed
        )
        
        result = responses_collection.insert_one(response.to_dict())
        
        # Update application with assessment score
        applications_collection = db['applications']
        applications_collection.update_one(
            {'_id': ObjectId(data['application_id'])},
            {'$set': {
                f'assessment_scores.{assessment_id}': percentage,
                'updated_at': datetime.utcnow()
            }}
        )
        
        return jsonify({
            'message': 'Assessment submitted successfully',
            'response_id': str(result.inserted_id),
            'score': score,
            'percentage': round(percentage, 2),
            'passed': passed
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/schedule-interview', methods=['POST'])
@jwt_required()
def schedule_interview():
    """Schedule interview (recruiter only)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can schedule interviews'}), 403
        
        data = request.get_json()
        
        required_fields = ['application_id', 'job_id', 'candidate_id', 'scheduled_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create interview
        interview = Interview(
            application_id=data['application_id'],
            job_id=data['job_id'],
            candidate_id=data['candidate_id'],
            recruiter_id=current_user['user_id'],
            interview_type=data.get('interview_type', 'technical'),
            scheduled_time=datetime.fromisoformat(data['scheduled_time']),
            duration_minutes=data.get('duration_minutes', 60),
            meeting_link=data.get('meeting_link', '')
        )
        
        db = get_db()
        interviews_collection = db['interviews']
        result = interviews_collection.insert_one(interview.to_dict())
        
        # Update application
        applications_collection = db['applications']
        applications_collection.update_one(
            {'_id': ObjectId(data['application_id'])},
            {'$set': {
                'interview_scheduled': data['scheduled_time'],
                'status': 'interview_scheduled',
                'updated_at': datetime.utcnow()
            }}
        )
        
        return jsonify({
            'message': 'Interview scheduled successfully',
            'interview_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
