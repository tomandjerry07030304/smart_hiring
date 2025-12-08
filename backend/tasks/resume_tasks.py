"""
Resume parsing background tasks
"""

from backend.celery_config import celery_app, SafeTask
from datetime import datetime
import os


@celery_app.task(base=SafeTask, bind=True, name='parse_resume')
def parse_resume_task(self, resume_url, application_id, filename='resume.pdf'):
    """
    Parse resume in background with advanced NLP
    
    Args:
        resume_url: URL or path to resume file
        application_id: Application ID to update with parsed data
        filename: Original filename for format detection
    """
    try:
        from backend.db import get_db
        from backend.services.resume_parser_service import get_resume_parser
        import requests
        
        # Download resume file
        if resume_url.startswith('http'):
            response = requests.get(resume_url, timeout=30)
            file_content = response.content
        else:
            # Local file path
            with open(resume_url, 'rb') as f:
                file_content = f.read()
        
        # Parse resume using advanced NLP parser
        parser = get_resume_parser()
        parsed_data = parser.parse_resume(file_content, filename)
        
        # Update application with parsed data
        db = get_db()
        db.applications.update_one(
            {'_id': application_id},
            {
                '$set': {
                    'parsed_resume': parsed_data,
                    'parsing_status': 'completed',
                    'parsed_at': datetime.utcnow()
                }
            }
        )
        
        # Calculate job match if job_id is available
        application = db.applications.find_one({'_id': application_id})
        if application and 'job_id' in application:
            job = db.jobs.find_one({'_id': application['job_id']})
            if job:
                match_result = parser.calculate_job_match(parsed_data, {
                    'required_skills': job.get('required_skills', []),
                    'min_experience_years': job.get('min_experience_years', 0),
                    'min_education_level': job.get('min_education_level', 0)
                })
                
                db.applications.update_one(
                    {'_id': application_id},
                    {'$set': {'job_match_score': match_result}}
                )
        
        return {'status': 'success', 'application_id': str(application_id), 'skills_found': len(parsed_data.get('skills', []))}
        
    except Exception as e:
        # Update parsing status
        db = get_db()
        db.applications.update_one(
            {'_id': application_id},
            {'$set': {'parsing_status': 'failed', 'parsing_error': str(e)}}
        )
        
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)


@celery_app.task(base=SafeTask, name='batch_parse_resumes')
def batch_parse_resumes(application_ids):
    """
    Parse multiple resumes in batch
    
    Args:
        application_ids: List of application IDs
    """
    from backend.db import get_db
    
    db = get_db()
    results = []
    
    for app_id in application_ids:
        application = db.applications.find_one({'_id': app_id})
        if application and application.get('resume_url'):
            # Queue individual parsing task
            task = parse_resume_task.delay(application['resume_url'], app_id)
            results.append({'application_id': str(app_id), 'task_id': task.id})
    
    return {'status': 'queued', 'total': len(results), 'tasks': results}


@celery_app.task(base=SafeTask, name='analyze_candidate_fit')
def analyze_candidate_fit(application_id, job_id):
    """
    Analyze candidate-job fit based on parsed resume
    
    Args:
        application_id: Application ID
        job_id: Job ID
    """
    from backend.db import get_db
    
    db = get_db()
    application = db.applications.find_one({'_id': application_id})
    job = db.jobs.find_one({'_id': job_id})
    
    if not application or not job:
        return {'status': 'failed', 'error': 'Application or job not found'}
    
    parsed_resume = application.get('parsed_resume', {})
    required_skills = set(job.get('required_skills', []))
    candidate_skills = set(parsed_resume.get('skills', []))
    
    # Calculate skill match percentage
    if required_skills:
        skill_match = len(required_skills & candidate_skills) / len(required_skills) * 100
    else:
        skill_match = 0
    
    # Calculate experience match
    required_exp = job.get('required_experience', 0)
    candidate_exp = parsed_resume.get('experience_years', 0)
    exp_match = min(candidate_exp / required_exp * 100, 100) if required_exp > 0 else 100
    
    # Overall fit score (weighted average)
    fit_score = (skill_match * 0.7) + (exp_match * 0.3)
    
    # Update application with fit analysis
    db.applications.update_one(
        {'_id': application_id},
        {
            '$set': {
                'fit_analysis': {
                    'skill_match': skill_match,
                    'experience_match': exp_match,
                    'overall_score': fit_score,
                    'analyzed_at': datetime.utcnow()
                }
            }
        }
    )
    
    return {
        'status': 'success',
        'application_id': str(application_id),
        'fit_score': fit_score
    }


# Export
__all__ = ['parse_resume_task', 'batch_parse_resumes', 'analyze_candidate_fit']
