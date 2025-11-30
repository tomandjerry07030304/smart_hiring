"""
Integration tests for authentication flows
"""

import pytest
import json
from backend.models.database import get_db


class TestAuthIntegration:
    """Test authentication and authorization flows"""
    
    def test_register_and_login_candidate(self, client):
        """Test complete registration and login flow for candidate"""
        # Register
        register_data = {
            'email': 'test_candidate@example.com',
            'password': 'TestPass123!',
            'name': 'Test Candidate',
            'role': 'candidate'
        }
        
        response = client.post('/api/auth/register', 
                             json=register_data,
                             content_type='application/json')
        
        assert response.status_code in (200, 201)
        
        # Login
        login_data = {
            'email': 'test_candidate@example.com',
            'password': 'TestPass123!'
        }
        
        response = client.post('/api/auth/login',
                             json=login_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data or 'token' in data
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails"""
        register_data = {
            'email': 'duplicate@example.com',
            'password': 'TestPass123!',
            'name': 'User One',
            'role': 'candidate'
        }
        
        # First registration
        client.post('/api/auth/register', json=register_data)
        
        # Second registration with same email
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code in (400, 409)
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials fails"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        
        assert response.status_code in (401, 400)
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get('/api/jobs/list')
        
        assert response.status_code in (401, 422)
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {'Authorization': 'Bearer invalid_token_here'}
        response = client.get('/api/jobs/list', headers=headers)
        
        assert response.status_code in (401, 422)


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_candidate_cannot_create_job(self, client):
        """Test that candidates cannot create jobs"""
        # Register and login as candidate
        register_data = {
            'email': 'candidate_rbac@example.com',
            'password': 'TestPass123!',
            'name': 'Candidate User',
            'role': 'candidate'
        }
        client.post('/api/auth/register', json=register_data)
        
        login_response = client.post('/api/auth/login', json={
            'email': 'candidate_rbac@example.com',
            'password': 'TestPass123!'
        })
        
        if login_response.status_code == 200:
            token_data = json.loads(login_response.data)
            token = token_data.get('access_token') or token_data.get('token')
            
            # Try to create job
            job_data = {
                'title': 'Test Job',
                'description': 'Test Description',
                'required_skills': ['Python']
            }
            
            headers = {'Authorization': f'Bearer {token}'}
            response = client.post('/api/jobs/create', 
                                 json=job_data,
                                 headers=headers)
            
            assert response.status_code in (403, 401)
