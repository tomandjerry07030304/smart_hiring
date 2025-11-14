from datetime import datetime
from bson import ObjectId

class Job:
    """Job posting model"""
    
    collection_name = 'jobs'
    
    def __init__(self, title, description, recruiter_id, **kwargs):
        self.title = title
        self.description = description
        self.recruiter_id = recruiter_id
        self.company_name = kwargs.get('company_name', '')
        self.location = kwargs.get('location', '')
        self.job_type = kwargs.get('job_type', 'Full-time')  # Full-time, Part-time, Contract
        self.required_skills = kwargs.get('required_skills', [])
        self.experience_required = kwargs.get('experience_required', 0)
        self.salary_range = kwargs.get('salary_range', {})
        self.status = kwargs.get('status', 'open')  # open, closed, on_hold
        self.posted_date = kwargs.get('posted_date', datetime.utcnow())
        self.deadline = kwargs.get('deadline', None)
        self.applications_count = kwargs.get('applications_count', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'recruiter_id': self.recruiter_id,
            'company_name': self.company_name,
            'location': self.location,
            'job_type': self.job_type,
            'required_skills': self.required_skills,
            'experience_required': self.experience_required,
            'salary_range': self.salary_range,
            'status': self.status,
            'posted_date': self.posted_date,
            'deadline': self.deadline,
            'applications_count': self.applications_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Application:
    """Job application model"""
    
    collection_name = 'applications'
    
    def __init__(self, job_id, candidate_id, **kwargs):
        self.job_id = job_id
        self.candidate_id = candidate_id
        self.status = kwargs.get('status', 'submitted')  # submitted, screening, shortlisted, rejected, hired
        self.resume_match_score = kwargs.get('resume_match_score', 0.0)
        self.skill_match_score = kwargs.get('skill_match_score', 0.0)
        self.overall_score = kwargs.get('overall_score', 0.0)
        self.cci_score = kwargs.get('cci_score', None)
        self.matched_skills = kwargs.get('matched_skills', [])
        self.assessment_scores = kwargs.get('assessment_scores', {})
        self.interview_scheduled = kwargs.get('interview_scheduled', None)
        self.decision = kwargs.get('decision', None)  # Hire, Review, Reject
        self.feedback = kwargs.get('feedback', '')
        self.transparency_report = kwargs.get('transparency_report', {})
        self.applied_date = kwargs.get('applied_date', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'candidate_id': self.candidate_id,
            'status': self.status,
            'resume_match_score': self.resume_match_score,
            'skill_match_score': self.skill_match_score,
            'overall_score': self.overall_score,
            'cci_score': self.cci_score,
            'matched_skills': self.matched_skills,
            'assessment_scores': self.assessment_scores,
            'interview_scheduled': self.interview_scheduled,
            'decision': self.decision,
            'feedback': self.feedback,
            'transparency_report': self.transparency_report,
            'applied_date': self.applied_date,
            'updated_at': self.updated_at
        }
