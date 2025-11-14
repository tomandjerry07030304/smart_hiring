"""
PyTest configuration and fixtures for Smart Hiring System tests
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app import app as flask_app
from backend.models.database import Database
from backend.backend_config import config


@pytest.fixture
def app():
    """Create application fixture"""
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = False
    flask_app.config['WTF_CSRF_ENABLED'] = False
    return flask_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def db():
    """Create database fixture"""
    db = Database()
    db.connect('testing')
    yield db
    # Cleanup after tests


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """
    John Doe
    john.doe@email.com
    (555) 123-4567
    123 Main St, City, State 12345
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5 years of experience in Python and web development.
    
    SKILLS
    - Python, JavaScript, React
    - Flask, Django, FastAPI
    - MongoDB, PostgreSQL
    - Docker, Kubernetes
    
    EXPERIENCE
    Senior Software Engineer - Tech Company (2020-Present)
    - Developed RESTful APIs using Flask
    - Implemented ML models for recommendation system
    - Led team of 5 developers
    
    EDUCATION
    BS in Computer Science - University Name (2018)
    """


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        "title": "Senior Python Developer",
        "description": "Looking for experienced Python developer",
        "requirements": "5+ years Python, Flask, MongoDB, Docker",
        "skills": ["python", "flask", "mongodb", "docker", "api development"],
        "location": "Remote",
        "salary_range": "$100k-$150k",
        "job_type": "Full-time"
    }


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing"""
    return {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567890",
        "skills": ["python", "django", "postgresql", "react"],
        "experience_years": 4,
        "education": "BS Computer Science"
    }


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing"""
    # Login and get token
    response = client.post('/api/auth/login', json={
        'email': 'admin@smarthiring.com',
        'password': config.ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.get_json()
        token = data.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    
    return {}
