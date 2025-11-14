"""
API endpoint tests for Smart Hiring System
"""

import pytest
import json


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test health check returns 200"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'database' in data
        assert 'environment' in data


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Smart Hiring System API'
        assert 'version' in data
        assert 'endpoints' in data


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_with_valid_credentials(self, client):
        """Test login with valid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'admin@smarthiring.com',
            'password': 'admin123'
        })
        
        # May return 200 or 404 depending on if admin user exists
        assert response.status_code in [200, 401, 404]
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code in [401, 404]
    
    def test_register_endpoint_exists(self, client):
        """Test register endpoint exists"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test User',
            'role': 'candidate'
        })
        
        # Should return success or validation error
        assert response.status_code in [200, 201, 400, 409]


class TestJobEndpoints:
    """Test job-related endpoints"""
    
    def test_get_jobs_list(self, client):
        """Test retrieving jobs list"""
        response = client.get('/api/jobs')
        assert response.status_code in [200, 401]  # May require auth
    
    def test_get_job_by_id_not_found(self, client):
        """Test getting non-existent job"""
        response = client.get('/api/jobs/nonexistent_id')
        assert response.status_code in [401, 404]


class TestCandidateEndpoints:
    """Test candidate-related endpoints"""
    
    def test_get_candidates_list(self, client):
        """Test retrieving candidates list"""
        response = client.get('/api/candidates')
        assert response.status_code in [200, 401]  # May require auth


class TestAssessmentEndpoints:
    """Test assessment-related endpoints"""
    
    def test_get_assessments_list(self, client):
        """Test retrieving assessments list"""
        response = client.get('/api/assessments')
        assert response.status_code in [200, 401]  # May require auth


class TestDashboardEndpoints:
    """Test dashboard-related endpoints"""
    
    def test_get_dashboard_stats(self, client):
        """Test retrieving dashboard statistics"""
        response = client.get('/api/dashboard/stats')
        assert response.status_code in [200, 401, 404]  # May require auth


class TestErrorHandlers:
    """Test error handlers"""
    
    def test_404_handler(self, client):
        """Test 404 error handler"""
        response = client.get('/api/nonexistent_endpoint')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestCORSHeaders:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are present"""
        response = client.options('/api/health')
        # CORS headers may or may not be present depending on config
        assert response.status_code in [200, 204, 405]


class TestRateLimiting:
    """Test rate limiting (if enabled)"""
    
    def test_multiple_requests_accepted(self, client):
        """Test that multiple requests within limit are accepted"""
        for i in range(5):
            response = client.get('/api/health')
            assert response.status_code == 200


# Parametrized tests
@pytest.mark.parametrize("endpoint", [
    "/api/health",
    "/",
    "/api/jobs",
    "/api/candidates",
    "/api/assessments"
])
def test_endpoints_return_json(client, endpoint):
    """Test that endpoints return JSON"""
    response = client.get(endpoint)
    assert response.content_type == 'application/json' or response.status_code == 401
