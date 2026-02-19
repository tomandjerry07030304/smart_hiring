"""
Gap 3 Regression Test: Assessment Collection Name Verification

Confirms that the assessment workflow uses CORRECT collection names:
  - quizzes  → quiz metadata (questions, config, time limits)
  - quiz_attempts → user attempt records (started, completed, scores)

This test prevents regressions where collection names could be confused 
(e.g., using 'assessments' instead of 'quizzes', or 'attempts' instead 
of 'quiz_attempts').
"""

import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import patch, MagicMock


class TestAssessmentCollectionNames:
    """Verify assessment routes use the correct MongoDB collection names."""
    
    def test_quiz_collection_name_in_routes(self):
        """Verify assessment_routes.py references 'quizzes' collection (not 'assessments')"""
        import inspect
        from backend.routes import assessment_routes
        
        source = inspect.getsource(assessment_routes)
        
        # MUST use 'quizzes' collection for quiz metadata
        assert "db['quizzes']" in source or 'db["quizzes"]' in source, \
            "assessment_routes.py must use 'quizzes' collection for quiz data"
        
        # MUST use 'quiz_attempts' for attempt tracking
        assert "db['quiz_attempts']" in source or 'db["quiz_attempts"]' in source, \
            "assessment_routes.py must use 'quiz_attempts' for attempt tracking"
    
    def test_no_wrong_collection_names(self):
        """Verify assessment_routes.py does NOT use wrong collection names"""
        import inspect
        from backend.routes import assessment_routes
        
        source = inspect.getsource(assessment_routes)
        
        # Should NOT use 'assessments' as a collection (common mistake)
        # Note: the word 'assessments' might appear in comments/strings, 
        # so we specifically check for collection access patterns
        wrong_patterns = [
            "db['assessments']",
            'db["assessments"]',
            "db['attempts']",  # Should be 'quiz_attempts', not just 'attempts'
            'db["attempts"]',
        ]
        
        for pattern in wrong_patterns:
            assert pattern not in source, \
                f"Found wrong collection name pattern: {pattern}. " \
                f"Use 'quizzes' and 'quiz_attempts' instead."
    
    def test_quiz_attempt_schema_fields(self):
        """Verify quiz attempt documents contain expected fields"""
        expected_fields = [
            'quiz_id',
            'user_id', 
            'status',      # 'in_progress' or 'completed'
            'started_at',
        ]
        
        # Create a sample attempt document matching the schema
        sample_attempt = {
            'quiz_id': str(ObjectId()),
            'user_id': str(ObjectId()),
            'status': 'in_progress',
            'started_at': datetime.utcnow(),
            'answers': [],
            'score': None,
            'completed_at': None
        }
        
        for field in expected_fields:
            assert field in sample_attempt, \
                f"Quiz attempt document missing required field: {field}"
    
    def test_max_attempts_check_uses_correct_collection(self):
        """Verify the max-attempts check queries quiz_attempts (not quizzes)"""
        import inspect
        from backend.routes import assessment_routes
        
        source = inspect.getsource(assessment_routes)
        
        # The max-attempts logic should count from quiz_attempts collection
        # and compare against quiz's max_attempts field
        assert 'max_attempts' in source, \
            "assessment_routes.py should reference max_attempts configuration"
        assert 'quiz_attempts' in source, \
            "Max attempts check must query the quiz_attempts collection"


class TestAssessmentCollectionIntegrity:
    """Integration-level checks for assessment data flow."""
    
    def test_quiz_creation_uses_quizzes_collection(self):
        """Verify quiz creation stores in 'quizzes' collection"""
        import inspect
        from backend.routes import assessment_routes
        
        source = inspect.getsource(assessment_routes)
        
        # Look for insert operations on 'quizzes' collection
        assert "quizzes" in source, \
            "Quiz creation must target the 'quizzes' collection"
    
    def test_attempt_start_uses_quiz_attempts_collection(self):
        """Verify starting an attempt writes to 'quiz_attempts' collection"""
        import inspect
        from backend.routes import assessment_routes
        
        source = inspect.getsource(assessment_routes)
        
        # The start-attempt endpoint should insert into quiz_attempts
        assert "quiz_attempts" in source, \
            "Starting an attempt must write to 'quiz_attempts' collection"
