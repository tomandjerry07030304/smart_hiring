"""
Integration tests for assessment/quiz workflows
"""

import pytest
import json
from bson import ObjectId


class TestAssessmentWorkflow:
    """Test complete assessment workflow"""
    
    @pytest.fixture
    def company_token(self, client):
        """Get company/recruiter auth token"""
        register_data = {
            'email': 'recruiter_test@example.com',
            'password': 'RecruiterPass123!',
            'name': 'Test Recruiter',
            'role': 'company'
        }
        client.post('/api/auth/register', json=register_data)
        
        login_response = client.post('/api/auth/login', json={
            'email': 'recruiter_test@example.com',
            'password': 'RecruiterPass123!'
        })
        
        if login_response.status_code == 200:
            data = json.loads(login_response.data)
            return data.get('access_token') or data.get('token')
        return None
    
    @pytest.fixture
    def candidate_token(self, client):
        """Get candidate auth token"""
        register_data = {
            'email': 'candidate_quiz@example.com',
            'password': 'CandidatePass123!',
            'name': 'Test Candidate',
            'role': 'candidate'
        }
        client.post('/api/auth/register', json=register_data)
        
        login_response = client.post('/api/auth/login', json={
            'email': 'candidate_quiz@example.com',
            'password': 'CandidatePass123!'
        })
        
        if login_response.status_code == 200:
            data = json.loads(login_response.data)
            return data.get('access_token') or data.get('token')
        return None
    
    def test_create_question_as_recruiter(self, client, company_token):
        """Test creating a question as recruiter"""
        if not company_token:
            pytest.skip("Could not obtain company token")
        
        question_data = {
            'question_text': 'What is Python?',
            'question_type': 'multiple_choice',
            'options': ['A language', 'A snake', 'Both', 'Neither'],
            'correct_answer': 'Both',
            'points': 10,
            'category': 'general'
        }
        
        headers = {'Authorization': f'Bearer {company_token}'}
        response = client.post('/api/assessments/questions',
                             json=question_data,
                             headers=headers)
        
        assert response.status_code in (200, 201)
    
    def test_candidate_cannot_create_question(self, client, candidate_token):
        """Test that candidates cannot create questions"""
        if not candidate_token:
            pytest.skip("Could not obtain candidate token")
        
        question_data = {
            'question_text': 'Test Question?',
            'question_type': 'multiple_choice',
            'options': ['A', 'B'],
            'correct_answer': 'A'
        }
        
        headers = {'Authorization': f'Bearer {candidate_token}'}
        response = client.post('/api/assessments/questions',
                             json=question_data,
                             headers=headers)
        
        assert response.status_code == 403
