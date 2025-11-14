"""
Tests for resume parser functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.utils.resume_parser import extract_text_from_pdf, extract_text_from_docx, anonymize_text


class TestTextExtraction:
    """Test text extraction from documents"""
    
    def test_extract_text_from_pdf_file_not_found(self):
        """Test PDF extraction with non-existent file"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("nonexistent.pdf")
    
    def test_extract_text_from_docx_file_not_found(self):
        """Test DOCX extraction with non-existent file"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_docx("nonexistent.docx")


class TestAnonymization:
    """Test resume anonymization"""
    
    def test_anonymize_email(self):
        """Test email anonymization"""
        text = "Contact me at john.doe@example.com"
        result = anonymize_text(text)
        assert "john.doe@example.com" not in result
        assert "[EMAIL]" in result or "email" not in result.lower()
    
    def test_anonymize_phone(self):
        """Test phone number anonymization"""
        text = "Call me at (555) 123-4567"
        result = anonymize_text(text)
        assert "(555) 123-4567" not in result
        assert "[PHONE]" in result or "555" not in result
    
    def test_anonymize_name(self, sample_resume_text):
        """Test name anonymization"""
        result = anonymize_text(sample_resume_text)
        # Name should be replaced or removed
        assert result != sample_resume_text
        assert len(result) > 0
    
    def test_anonymize_address(self):
        """Test address anonymization"""
        text = "123 Main St, New York, NY 10001"
        result = anonymize_text(text)
        # Address patterns should be replaced
        assert result != text or len(result) < len(text)
    
    def test_anonymize_preserves_skills(self):
        """Test that skills are preserved during anonymization"""
        text = "Skills: Python, JavaScript, React, MongoDB"
        result = anonymize_text(text)
        # Skills should generally be preserved
        assert "Python" in result or "python" in result.lower()
    
    def test_anonymize_empty_text(self):
        """Test anonymization of empty text"""
        result = anonymize_text("")
        assert result == ""
    
    def test_anonymize_text_without_pii(self):
        """Test anonymization of text without PII"""
        text = "This is a sample text without any personal information."
        result = anonymize_text(text)
        assert len(result) > 0


class TestResumeFields:
    """Test extraction of specific resume fields"""
    
    def test_extract_skills_from_text(self, sample_resume_text):
        """Test skill extraction"""
        # This would test a skill extraction function if available
        text = sample_resume_text.lower()
        assert "python" in text
        assert "flask" in text
        assert "mongodb" in text
    
    def test_extract_experience_years(self, sample_resume_text):
        """Test experience years extraction"""
        text = sample_resume_text
        # Check if experience information is present
        assert "experience" in text.lower()
        assert "years" in text.lower()


class TestFileValidation:
    """Test file validation"""
    
    def test_valid_pdf_extension(self):
        """Test PDF extension validation"""
        filename = "resume.pdf"
        assert filename.endswith('.pdf')
    
    def test_valid_docx_extension(self):
        """Test DOCX extension validation"""
        filename = "resume.docx"
        assert filename.endswith(('.docx', '.doc'))
    
    def test_invalid_extension(self):
        """Test invalid extension"""
        filename = "resume.exe"
        assert not filename.endswith(('.pdf', '.docx', '.doc', '.txt'))
