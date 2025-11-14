from datetime import datetime
from bson import ObjectId

class Assessment:
    """Assessment model for tests/challenges"""
    
    collection_name = 'assessments'
    
    def __init__(self, job_id, title, assessment_type, **kwargs):
        self.job_id = job_id
        self.title = title
        self.assessment_type = assessment_type  # 'mcq', 'coding', 'behavioral'
        self.duration_minutes = kwargs.get('duration_minutes', 60)
        self.questions = kwargs.get('questions', [])
        self.passing_score = kwargs.get('passing_score', 60)
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'title': self.title,
            'assessment_type': self.assessment_type,
            'duration_minutes': self.duration_minutes,
            'questions': self.questions,
            'passing_score': self.passing_score,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class AssessmentResponse:
    """Candidate's assessment responses"""
    
    collection_name = 'assessment_responses'
    
    def __init__(self, assessment_id, candidate_id, application_id, **kwargs):
        self.assessment_id = assessment_id
        self.candidate_id = candidate_id
        self.application_id = application_id
        self.answers = kwargs.get('answers', [])
        self.score = kwargs.get('score', 0.0)
        self.percentage = kwargs.get('percentage', 0.0)
        self.started_at = kwargs.get('started_at', None)
        self.completed_at = kwargs.get('completed_at', None)
        self.time_taken_minutes = kwargs.get('time_taken_minutes', 0)
        self.passed = kwargs.get('passed', False)
        
    def to_dict(self):
        return {
            'assessment_id': self.assessment_id,
            'candidate_id': self.candidate_id,
            'application_id': self.application_id,
            'answers': self.answers,
            'score': self.score,
            'percentage': self.percentage,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'time_taken_minutes': self.time_taken_minutes,
            'passed': self.passed
        }

class Interview:
    """Interview scheduling model"""
    
    collection_name = 'interviews'
    
    def __init__(self, application_id, job_id, candidate_id, recruiter_id, **kwargs):
        self.application_id = application_id
        self.job_id = job_id
        self.candidate_id = candidate_id
        self.recruiter_id = recruiter_id
        self.interview_type = kwargs.get('interview_type', 'technical')  # technical, hr, behavioral
        self.scheduled_time = kwargs.get('scheduled_time', None)
        self.duration_minutes = kwargs.get('duration_minutes', 60)
        self.meeting_link = kwargs.get('meeting_link', '')
        self.status = kwargs.get('status', 'scheduled')  # scheduled, completed, cancelled, rescheduled
        self.notes = kwargs.get('notes', '')
        self.rating = kwargs.get('rating', None)
        self.feedback = kwargs.get('feedback', '')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'application_id': self.application_id,
            'job_id': self.job_id,
            'candidate_id': self.candidate_id,
            'recruiter_id': self.recruiter_id,
            'interview_type': self.interview_type,
            'scheduled_time': self.scheduled_time,
            'duration_minutes': self.duration_minutes,
            'meeting_link': self.meeting_link,
            'status': self.status,
            'notes': self.notes,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
