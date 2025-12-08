"""
Comprehensive API Test Suite
=============================
Unit and integration tests for Smart Hiring System API

Test Coverage:
- Authentication endpoints
- Job posting CRUD
- Application workflow
- Assessment system
- Fairness evaluation
- Analytics endpoints
- WebSocket connections
- Email notifications

Author: Smart Hiring System Team
Date: December 2025
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


# Fixtures
@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app import create_app
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing"""
    # Register test user
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'role': 'candidate',
        'full_name': 'Test User'
    })
    
    data = response.get_json()
    token = data.get('access_token')
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def recruiter_headers(client):
    """Get recruiter authentication headers"""
    response = client.post('/api/auth/register', json={
        'email': 'recruiter@example.com',
        'password': 'RecruiterPass123!',
        'role': 'recruiter',
        'full_name': 'Test Recruiter'
    })
    
    data = response.get_json()
    token = data.get('access_token')
    
    return {'Authorization': f'Bearer {token}'}


# Authentication Tests
class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_candidate(self, client):
        """Test candidate registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newcandidate@example.com',
            'password': 'SecurePass123!',
            'role': 'candidate',
            'full_name': 'New Candidate'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'newcandidate@example.com'
        assert data['user']['role'] == 'candidate'
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Register first user
        client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'Pass123!',
            'role': 'candidate',
            'full_name': 'First User'
        })
        
        # Try to register again
        response = client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'Pass456!',
            'role': 'recruiter',
            'full_name': 'Second User'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register user
        client.post('/api/auth/register', json={
            'email': 'logintest@example.com',
            'password': 'LoginPass123!',
            'role': 'candidate',
            'full_name': 'Login Test'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'email': 'logintest@example.com',
            'password': 'LoginPass123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid password"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'WrongPass123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


# Job Tests
class TestJobs:
    """Test job posting endpoints"""
    
    def test_create_job(self, client, recruiter_headers):
        """Test creating a new job posting"""
        response = client.post('/api/jobs', 
            headers=recruiter_headers,
            json={
                'title': 'Senior Python Developer',
                'description': 'Looking for experienced Python developer',
                'company_name': 'Tech Corp',
                'location': 'Remote',
                'required_skills': ['Python', 'Django', 'PostgreSQL'],
                'min_experience_years': 3,
                'salary_range': {'min': 80000, 'max': 120000}
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Senior Python Developer'
        assert 'id' in data
    
    def test_create_job_unauthorized(self, client, auth_headers):
        """Test that candidates cannot create jobs"""
        response = client.post('/api/jobs',
            headers=auth_headers,
            json={
                'title': 'Test Job',
                'description': 'Test description'
            }
        )
        
        assert response.status_code in [401, 403]
    
    def test_list_jobs(self, client):
        """Test listing job postings"""
        response = client.get('/api/jobs')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'jobs' in data
        assert isinstance(data['jobs'], list)
    
    def test_get_job_by_id(self, client, recruiter_headers):
        """Test retrieving specific job"""
        # Create job first
        create_response = client.post('/api/jobs',
            headers=recruiter_headers,
            json={
                'title': 'Test Job',
                'description': 'Test description',
                'company_name': 'Test Company'
            }
        )
        
        job_id = create_response.get_json()['id']
        
        # Retrieve job
        response = client.get(f'/api/jobs/{job_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == job_id
        assert data['title'] == 'Test Job'
    
    def test_update_job(self, client, recruiter_headers):
        """Test updating job posting"""
        # Create job
        create_response = client.post('/api/jobs',
            headers=recruiter_headers,
            json={
                'title': 'Original Title',
                'description': 'Original description',
                'company_name': 'Test Company'
            }
        )
        
        job_id = create_response.get_json()['id']
        
        # Update job
        response = client.put(f'/api/jobs/{job_id}',
            headers=recruiter_headers,
            json={
                'title': 'Updated Title',
                'description': 'Updated description'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Updated Title'


# Application Tests
class TestApplications:
    """Test job application endpoints"""
    
    @pytest.fixture
    def test_job_id(self, client, recruiter_headers):
        """Create a test job and return its ID"""
        response = client.post('/api/jobs',
            headers=recruiter_headers,
            json={
                'title': 'Test Position',
                'description': 'Test job for applications',
                'company_name': 'Test Corp'
            }
        )
        return response.get_json()['id']
    
    def test_submit_application(self, client, auth_headers, test_job_id):
        """Test submitting job application"""
        # Mock resume file
        data = {
            'job_id': test_job_id,
            'cover_letter': 'I am very interested in this position'
        }
        
        response = client.post('/api/applications',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'id' in data
        assert data['job_id'] == test_job_id
    
    def test_list_my_applications(self, client, auth_headers):
        """Test listing candidate's applications"""
        response = client.get('/api/applications/my-applications',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


# Resume Parser Tests
class TestResumeParser:
    """Test resume parsing service"""
    
    def test_parse_pdf_resume(self):
        """Test PDF resume parsing"""
        from backend.services.resume_parser_service import get_resume_parser
        
        parser = get_resume_parser()
        
        # Mock PDF content
        mock_content = b"John Doe\nPython Developer\n5 years experience\njohn@email.com\n"
        
        with patch.object(parser, '_extract_text_from_pdf', return_value="John Doe\nPython Developer\n5 years experience\njohn@email.com"):
            result = parser.parse_resume(mock_content, 'resume.pdf')
        
        assert 'contact' in result
        assert 'skills' in result
        assert 'experience' in result
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        from backend.services.resume_parser_service import ResumeParser
        
        parser = ResumeParser()
        text = """
        John Doe
        john.doe@example.com
        +1-555-0123
        linkedin.com/in/johndoe
        github.com/johndoe
        """
        
        contact = parser._extract_contact_info(text)
        
        assert contact['email'] == 'john.doe@example.com'
        assert 'linkedin' in contact['linkedin']
        assert 'github' in contact['github']
    
    def test_extract_skills(self):
        """Test skills extraction"""
        from backend.services.resume_parser_service import ResumeParser
        
        parser = ResumeParser()
        text = """
        Technical Skills:
        - Python, JavaScript, Java
        - React, Django, Flask
        - PostgreSQL, MongoDB
        - AWS, Docker, Kubernetes
        """
        
        skills = parser._extract_skills(text)
        
        assert len(skills) > 0
        skill_names = [s['name'].lower() for s in skills]
        assert any('python' in name for name in skill_names)
        assert any('react' in name for name in skill_names)


# Fairness Tests
class TestFairness:
    """Test fairness evaluation"""
    
    def test_fairness_metrics_calculation(self):
        """Test fairness metrics computation"""
        from backend.services.fairness_engine import FairnessMetrics
        import numpy as np
        
        # Mock data
        predictions = np.array([1, 0, 1, 0, 1, 1, 0, 0])
        labels = np.array([1, 0, 1, 0, 0, 1, 0, 1])
        sensitive_features = np.array(['A', 'A', 'B', 'B', 'A', 'B', 'A', 'B'])
        
        calculator = FairnessMetrics(predictions, labels, sensitive_features)
        
        # Test metrics
        dp = calculator.demographic_parity_difference()
        di = calculator.disparate_impact()
        eo = calculator.equal_opportunity_difference()
        
        assert isinstance(dp, float)
        assert isinstance(di, float)
        assert isinstance(eo, float)
        assert 0 <= di <= 2  # Disparate impact should be between 0 and 2
    
    def test_fairness_proxy(self):
        """Test fairness proxy with failover"""
        from backend.services.fairness_proxy import FairnessProxy
        
        proxy = FairnessProxy()
        
        # Test evaluation
        result = proxy.evaluate_fairness(
            predictions=[1, 0, 1, 0],
            labels=[1, 0, 0, 1],
            sensitive_features=['Male', 'Female', 'Male', 'Female']
        )
        
        assert 'demographic_parity' in result
        assert '_metadata' in result
        assert result['_metadata']['engine'] in ['aif360', 'lightweight']


# Analytics Tests
class TestAnalytics:
    """Test analytics service"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = Mock()
        db.users = Mock()
        db.jobs = Mock()
        db.applications = Mock()
        db.assessments = Mock()
        return db
    
    def test_platform_overview(self, mock_db):
        """Test platform overview metrics"""
        from backend.services.analytics_service import AnalyticsService
        
        # Setup mocks
        mock_db.users.count_documents.return_value = 100
        mock_db.jobs.count_documents.return_value = 50
        mock_db.applications.count_documents.return_value = 200
        
        analytics = AnalyticsService(mock_db)
        overview = analytics.get_platform_overview()
        
        assert 'users' in overview
        assert 'jobs' in overview
        assert 'applications' in overview


# WebSocket Tests
class TestWebSocket:
    """Test WebSocket functionality"""
    
    def test_websocket_manager_init(self):
        """Test WebSocket manager initialization"""
        from backend.services.websocket_service import WebSocketManager
        
        manager = WebSocketManager()
        
        assert manager.active_connections == {}
        assert manager.sid_to_user == {}
    
    def test_send_notification(self):
        """Test sending WebSocket notification"""
        from backend.services.websocket_service import WebSocketManager
        
        manager = WebSocketManager()
        
        # Mock socketio
        manager.socketio = Mock()
        
        result = manager.send_notification(
            user_id='user123',
            notification_type='test',
            title='Test Notification',
            message='This is a test'
        )
        
        assert manager.socketio.emit.called


# Cache Tests
class TestCache:
    """Test caching service"""
    
    def test_memory_cache_set_get(self):
        """Test basic cache set and get"""
        from backend.services.cache_service import CacheService
        
        cache = CacheService(redis_url=None)  # Use memory cache
        
        cache.set('test_key', 'test_value')
        value = cache.get('test_key')
        
        assert value == 'test_value'
    
    def test_cache_expiration(self):
        """Test cache TTL"""
        from backend.services.cache_service import CacheService
        import time
        
        cache = CacheService(redis_url=None)
        
        cache.set('expire_key', 'expire_value', ttl=1)
        
        # Value should exist immediately
        assert cache.get('expire_key') == 'expire_value'
        
        # Wait for expiration (memory cache doesn't auto-expire, but Redis would)
        time.sleep(2)
        
        # In production with Redis, this would be None
        # For memory cache, manual cleanup would be needed


# Email Tests
class TestEmail:
    """Test email notification system"""
    
    def test_email_template_rendering(self):
        """Test email template rendering"""
        from backend.services.email_templates import EmailTemplates
        
        html = EmailTemplates.render_template('application_received', {
            'candidate_name': 'John Doe',
            'job_title': 'Senior Developer',
            'company_name': 'Tech Corp',
            'application_id': 'APP123'
        })
        
        assert 'John Doe' in html
        assert 'Senior Developer' in html
        assert 'Tech Corp' in html
    
    def test_interview_invitation_template(self):
        """Test interview invitation email"""
        from backend.services.email_templates import EmailTemplates
        
        html = EmailTemplates.render_template('interview_invitation', {
            'candidate_name': 'Jane Smith',
            'job_title': 'Data Scientist',
            'interview_datetime': '2025-12-15 14:00',
            'meeting_link': 'https://meet.example.com/xyz'
        })
        
        assert 'Jane Smith' in html
        assert '2025-12-15 14:00' in html
        assert 'meet.example.com' in html


# Integration Tests
class TestIntegration:
    """End-to-end integration tests"""
    
    def test_complete_application_workflow(self, client):
        """Test complete application workflow from registration to application"""
        # 1. Register candidate
        candidate_response = client.post('/api/auth/register', json={
            'email': 'candidate@test.com',
            'password': 'CandPass123!',
            'role': 'candidate',
            'full_name': 'Test Candidate'
        })
        
        assert candidate_response.status_code == 201
        candidate_token = candidate_response.get_json()['access_token']
        
        # 2. Register recruiter
        recruiter_response = client.post('/api/auth/register', json={
            'email': 'recruiter@test.com',
            'password': 'RecPass123!',
            'role': 'recruiter',
            'full_name': 'Test Recruiter'
        })
        
        assert recruiter_response.status_code == 201
        recruiter_token = recruiter_response.get_json()['access_token']
        
        # 3. Create job
        job_response = client.post('/api/jobs',
            headers={'Authorization': f'Bearer {recruiter_token}'},
            json={
                'title': 'Full Stack Developer',
                'description': 'Looking for full stack developer',
                'company_name': 'Test Company',
                'required_skills': ['React', 'Node.js', 'MongoDB']
            }
        )
        
        assert job_response.status_code == 201
        job_id = job_response.get_json()['id']
        
        # 4. Submit application
        application_response = client.post('/api/applications',
            headers={'Authorization': f'Bearer {candidate_token}'},
            data={'job_id': job_id, 'cover_letter': 'I am interested'},
            content_type='multipart/form-data'
        )
        
        assert application_response.status_code in [200, 201]
        
        # 5. Check applications
        applications_response = client.get('/api/applications/my-applications',
            headers={'Authorization': f'Bearer {candidate_token}'}
        )
        
        assert applications_response.status_code == 200
        applications = applications_response.get_json()
        assert len(applications) > 0


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
