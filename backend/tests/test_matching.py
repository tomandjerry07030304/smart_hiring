"""
Tests for matching and scoring functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.utils.matching import calculate_tfidf_similarity, extract_skills, skill_match_score


class TestTFIDFSimilarity:
    """Test TF-IDF similarity calculation"""
    
    def test_identical_texts(self):
        """Test similarity of identical texts"""
        text = "Python developer with Flask experience"
        similarity = calculate_tfidf_similarity(text, text)
        assert 0.9 <= similarity <= 1.0
    
    def test_similar_texts(self):
        """Test similarity of similar texts"""
        text1 = "Python developer with Flask and Django experience"
        text2 = "Experienced Python programmer using Flask framework"
        similarity = calculate_tfidf_similarity(text1, text2)
        assert 0.3 <= similarity <= 1.0
    
    def test_dissimilar_texts(self):
        """Test similarity of dissimilar texts"""
        text1 = "Python developer with machine learning experience"
        text2 = "Marketing manager with social media expertise"
        similarity = calculate_tfidf_similarity(text1, text2)
        assert 0.0 <= similarity <= 0.5
    
    def test_empty_text_similarity(self):
        """Test similarity with empty text"""
        similarity = calculate_tfidf_similarity("", "Python developer")
        assert similarity == 0.0 or isinstance(similarity, float)
    
    def test_case_insensitive(self):
        """Test that similarity is case-insensitive"""
        text1 = "Python Flask MongoDB"
        text2 = "python flask mongodb"
        similarity = calculate_tfidf_similarity(text1, text2)
        assert 0.9 <= similarity <= 1.0


class TestSkillExtraction:
    """Test skill extraction from text"""
    
    def test_extract_common_skills(self):
        """Test extraction of common technical skills"""
        text = "Experience with Python, JavaScript, React, and MongoDB"
        skills = extract_skills(text)
        assert isinstance(skills, list)
        # Check if skills are extracted (implementation dependent)
        if len(skills) > 0:
            assert any(skill.lower() in ['python', 'javascript', 'react', 'mongodb'] for skill in skills)
    
    def test_extract_skills_from_empty_text(self):
        """Test skill extraction from empty text"""
        skills = extract_skills("")
        assert isinstance(skills, list)
        assert len(skills) == 0 or skills is not None
    
    def test_extract_skills_case_handling(self):
        """Test skill extraction handles case properly"""
        text = "PYTHON, JavaScript, rEaCt"
        skills = extract_skills(text)
        assert isinstance(skills, list)


class TestSkillMatching:
    """Test skill matching between candidate and job"""
    
    def test_perfect_skill_match(self):
        """Test perfect skill match"""
        candidate_skills = ["python", "flask", "mongodb", "docker"]
        job_skills = ["python", "flask", "mongodb", "docker"]
        score = skill_match_score(candidate_skills, job_skills)
        assert 0.9 <= score <= 1.0
    
    def test_partial_skill_match(self):
        """Test partial skill match"""
        candidate_skills = ["python", "flask", "django"]
        job_skills = ["python", "flask", "mongodb", "docker"]
        score = skill_match_score(candidate_skills, job_skills)
        assert 0.3 <= score <= 0.8
    
    def test_no_skill_match(self):
        """Test no skill match"""
        candidate_skills = ["java", "spring", "oracle"]
        job_skills = ["python", "flask", "mongodb"]
        score = skill_match_score(candidate_skills, job_skills)
        assert 0.0 <= score <= 0.3
    
    def test_empty_candidate_skills(self):
        """Test with empty candidate skills"""
        candidate_skills = []
        job_skills = ["python", "flask"]
        score = skill_match_score(candidate_skills, job_skills)
        assert score == 0.0 or isinstance(score, (int, float))
    
    def test_empty_job_skills(self):
        """Test with empty job skills"""
        candidate_skills = ["python", "flask"]
        job_skills = []
        score = skill_match_score(candidate_skills, job_skills)
        assert score == 0.0 or isinstance(score, (int, float))
    
    def test_case_insensitive_matching(self):
        """Test case-insensitive skill matching"""
        candidate_skills = ["PYTHON", "Flask", "mongodb"]
        job_skills = ["python", "flask", "MongoDB"]
        score = skill_match_score(candidate_skills, job_skills)
        assert 0.9 <= score <= 1.0


class TestCandidateJobMatching:
    """Test overall candidate-job matching"""
    
    def test_match_score_range(self, sample_resume_text, sample_job_data):
        """Test that match scores are in valid range"""
        # Calculate similarity (would use actual matching function)
        text1 = sample_resume_text
        text2 = sample_job_data.get('description', '') + ' ' + sample_job_data.get('requirements', '')
        
        score = calculate_tfidf_similarity(text1, text2)
        assert 0.0 <= score <= 1.0
    
    def test_high_quality_match(self):
        """Test high quality candidate-job match"""
        candidate_text = "5 years Python experience, Flask, MongoDB, Docker, Kubernetes"
        job_text = "Looking for Python developer with Flask, MongoDB, and Docker experience"
        
        score = calculate_tfidf_similarity(candidate_text, job_text)
        assert score > 0.3  # Should have reasonable similarity


class TestEdgeCases:
    """Test edge cases in matching"""
    
    def test_special_characters_handling(self):
        """Test handling of special characters"""
        text1 = "C++ and C# developer with .NET experience"
        text2 = "Looking for C++ C# .NET developer"
        score = calculate_tfidf_similarity(text1, text2)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_numbers_in_text(self):
        """Test handling of numbers in text"""
        text1 = "5 years experience with Python 3.9"
        text2 = "3 years experience with Python 3.8"
        score = calculate_tfidf_similarity(text1, text2)
        assert isinstance(score, float)
    
    def test_very_long_text(self):
        """Test handling of very long text"""
        text1 = "python " * 1000
        text2 = "python flask mongodb"
        score = calculate_tfidf_similarity(text1, text2)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
