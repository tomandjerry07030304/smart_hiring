"""
ML Service Client
=================
Connects main backend to ML microservice for heavy operations.
Provides fallback to local processing when microservice is unavailable.
"""

import os
import requests
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Configuration
ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://localhost:5001')
ML_SERVICE_SECRET = os.getenv('ML_SERVICE_SECRET', 'your-secret-key')
ML_SERVICE_TIMEOUT = int(os.getenv('ML_SERVICE_TIMEOUT', 30))

class MLServiceClient:
    """Client for communicating with ML microservice"""
    
    def __init__(self):
        self.base_url = ML_SERVICE_URL
        self.secret = ML_SERVICE_SECRET
        self.timeout = ML_SERVICE_TIMEOUT
        self._available = None
    
    @property
    def headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Service-Token': self.secret
        }
    
    def is_available(self):
        """Check if ML service is available"""
        if self._available is not None:
            return self._available
        
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            self._available = response.status_code == 200
        except:
            self._available = False
        
        return self._available
    
    def parse_resume(self, file_data, filename):
        """Parse resume file through ML service"""
        if not self.is_available():
            return {'error': 'ML service unavailable', 'fallback': True}
        
        try:
            files = {'file': (filename, file_data)}
            response = requests.post(
                f"{self.base_url}/api/parse-resume",
                files=files,
                headers={'X-Service-Token': self.secret},
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            logger.error(f"ML service error: {e}")
            return {'error': str(e), 'fallback': True}
    
    def extract_skills(self, text):
        """Extract skills from text"""
        if not self.is_available():
            # Fallback to simple extraction
            return self._fallback_extract_skills(text)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/extract-skills",
                json={'text': text},
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            logger.error(f"ML service error: {e}")
            return self._fallback_extract_skills(text)
    
    def calculate_match(self, job_description, resume_text, job_skills, candidate_skills):
        """Calculate job-candidate match score"""
        if not self.is_available():
            return self._fallback_match(job_skills, candidate_skills)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/calculate-match",
                json={
                    'job_description': job_description,
                    'resume_text': resume_text,
                    'job_skills': job_skills,
                    'candidate_skills': candidate_skills
                },
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            logger.error(f"ML service error: {e}")
            return self._fallback_match(job_skills, candidate_skills)
    
    def get_analytics(self, applications_data):
        """Get analytics from application data"""
        if not self.is_available():
            return {'error': 'ML service unavailable', 'fallback': True}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/analytics/stats",
                json={'applications': applications_data},
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            logger.error(f"ML service error: {e}")
            return {'error': str(e), 'fallback': True}
    
    def evaluate_fairness(self, applications_data, protected_attribute='gender'):
        """Evaluate fairness metrics"""
        if not self.is_available():
            return {'error': 'ML service unavailable', 'fallback': True}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/fairness/evaluate",
                json={
                    'applications': applications_data,
                    'protected_attribute': protected_attribute
                },
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            logger.error(f"ML service error: {e}")
            return {'error': str(e), 'fallback': True}
    
    # Fallback methods when ML service is unavailable
    def _fallback_extract_skills(self, text):
        """Simple keyword-based skill extraction"""
        skills_db = [
            'python', 'java', 'javascript', 'sql', 'react', 'angular', 'node.js',
            'docker', 'kubernetes', 'aws', 'azure', 'machine learning', 'git'
        ]
        text_lower = text.lower()
        found = [s for s in skills_db if s in text_lower]
        return {'success': True, 'skills': found, 'count': len(found), 'fallback': True}
    
    def _fallback_match(self, job_skills, candidate_skills):
        """Simple skill overlap calculation"""
        if not job_skills:
            return {'success': True, 'overall_score': 0, 'fallback': True}
        
        job_set = set([s.lower() for s in job_skills])
        candidate_set = set([s.lower() for s in candidate_skills])
        matched = job_set.intersection(candidate_set)
        score = len(matched) / len(job_set)
        
        return {
            'success': True,
            'overall_score': round(score, 3),
            'matched_skills': list(matched),
            'missing_skills': list(job_set - candidate_set),
            'fallback': True
        }


# Singleton instance
ml_client = MLServiceClient()


# Decorator for graceful degradation
def with_ml_fallback(fallback_func):
    """Decorator that provides fallback when ML service fails"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if ml_client.is_available():
                    return func(*args, **kwargs)
                else:
                    logger.warning(f"ML service unavailable, using fallback for {func.__name__}")
                    return fallback_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}, using fallback")
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator
