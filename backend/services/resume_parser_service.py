"""
Advanced Resume Parser with NLP
================================
Enterprise-grade resume parsing using spaCy, PyPDF2, and python-docx

Features:
- Multi-format support (PDF, DOCX, TXT)
- NLP-based information extraction
- Skills detection with taxonomy matching
- Experience calculation
- Education parsing
- Contact information extraction
- Certification detection

Author: Smart Hiring System Team
Date: December 2025
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import spacy
from PyPDF2 import PdfReader
from docx import Document
import io
import os

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Advanced resume parser with NLP capabilities
    
    Supports multiple formats and intelligent information extraction
    """
    
    # Comprehensive skills taxonomy
    SKILL_CATEGORIES = {
        'programming': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'nosql',
            'html', 'css', 'sass', 'less'
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'springboot',
            'express', 'nestjs', 'rails', 'laravel', '.net', 'asp.net', 'tensorflow',
            'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy'
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'dynamodb', 'oracle', 'sql server', 'sqlite', 'mariadb', 'neo4j'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'kubernetes',
            'docker', 'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible'
        ],
        'tools': [
            'git', 'jira', 'confluence', 'slack', 'trello', 'postman', 'swagger',
            'vscode', 'intellij', 'eclipse', 'jupyter', 'tableau', 'power bi'
        ],
        'methodologies': [
            'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd', 'microservices',
            'rest', 'graphql', 'soap', 'oauth', 'jwt', 'machine learning', 'deep learning',
            'data science', 'nlp', 'computer vision'
        ]
    }
    
    # Education degrees
    DEGREES = [
        'phd', 'ph.d', 'doctorate', 'masters', 'master', 'mba', 'ms', 'm.s', 
        'bachelors', 'bachelor', 'bs', 'b.s', 'ba', 'b.a', 'associate', 'diploma',
        'b.tech', 'btech', 'm.tech', 'mtech', 'be', 'b.e', 'me', 'm.e'
    ]
    
    # Certification patterns
    CERTIFICATIONS = [
        'aws certified', 'azure certified', 'google cloud certified', 'cisco',
        'comptia', 'pmp', 'scrum master', 'certified', 'professional', 'specialist',
        'expert', 'associate'
    ]
    
    def __init__(self):
        """Initialize resume parser with spaCy model"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("✅ spaCy model loaded successfully")
        except OSError:
            logger.warning("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def parse_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse resume from file content
        
        Args:
            file_content: Binary file content
            filename: Original filename
        
        Returns:
            Parsed resume data
        """
        try:
            # Extract text based on file type
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                text = self._extract_text_from_pdf(file_content)
            elif file_ext in ['docx', 'doc']:
                text = self._extract_text_from_docx(file_content)
            elif file_ext == 'txt':
                text = file_content.decode('utf-8', errors='ignore')
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            logger.info(f"📄 Extracted {len(text)} characters from resume")
            
            # Parse information
            parsed_data = {
                'raw_text': text,
                'contact': self._extract_contact_info(text),
                'skills': self._extract_skills(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education(text),
                'certifications': self._extract_certifications(text),
                'summary': self._generate_summary(text),
                'parsed_at': datetime.utcnow().isoformat(),
                'parser_version': '2.0'
            }
            
            # Calculate match scores
            parsed_data['metadata'] = {
                'total_skills': len(parsed_data['skills']),
                'experience_years': parsed_data['experience']['total_years'],
                'education_level': self._calculate_education_level(parsed_data['education']),
                'has_certifications': len(parsed_data['certifications']) > 0
            }
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"❌ Resume parsing failed: {e}")
            return {
                'error': str(e),
                'parsed_at': datetime.utcnow().isoformat(),
                'parser_version': '2.0'
            }
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc_file = io.BytesIO(content)
            document = Document(doc_file)
            
            text = ""
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""
    
    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
            'portfolio': None
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/([A-Za-z0-9_-]+)'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact['linkedin'] = f"https://linkedin.com/in/{linkedin_matches[0]}"
        
        # GitHub
        github_pattern = r'github\.com/([A-Za-z0-9_-]+)'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            contact['github'] = f"https://github.com/{github_matches[0]}"
        
        # Portfolio (generic URL)
        url_pattern = r'https?://(?:www\.)?([A-Za-z0-9_-]+\.[A-Za-z]{2,})'
        urls = re.findall(url_pattern, text)
        if urls:
            # Filter out common sites
            portfolio_urls = [url for url in urls if not any(x in url.lower() for x in ['linkedin', 'github', 'gmail', 'yahoo'])]
            if portfolio_urls:
                contact['portfolio'] = f"https://{portfolio_urls[0]}"
        
        return contact
    
    def _extract_skills(self, text: str) -> List[Dict[str, str]]:
        """Extract and categorize skills"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.SKILL_CATEGORIES.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append({
                        'name': skill.title(),
                        'category': category
                    })
        
        # Remove duplicates
        seen = set()
        unique_skills = []
        for skill in found_skills:
            key = skill['name'].lower()
            if key not in seen:
                seen.add(key)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract work experience"""
        experience = {
            'positions': [],
            'total_years': 0
        }
        
        # Extract years of experience using patterns
        years_patterns = [
            r'(\d+)\+?\s+years?\s+(?:of\s+)?experience',
            r'experience:?\s+(\d+)\+?\s+years?',
            r'(\d+)\+?\s+yrs?\s+(?:of\s+)?experience'
        ]
        
        max_years = 0
        for pattern in years_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                years = max([int(m) for m in matches])
                max_years = max(max_years, years)
        
        experience['total_years'] = max_years
        
        # Extract job titles using NLP
        if self.nlp:
            doc = self.nlp(text[:10000])  # Limit for performance
            
            # Common job title indicators
            job_indicators = ['developer', 'engineer', 'manager', 'analyst', 'designer', 
                            'architect', 'consultant', 'specialist', 'lead', 'senior',
                            'junior', 'intern', 'director', 'coordinator']
            
            for ent in doc.ents:
                if ent.label_ == 'ORG' or any(indicator in ent.text.lower() for indicator in job_indicators):
                    # Try to find associated dates
                    experience['positions'].append({
                        'title': ent.text,
                        'context': text[max(0, ent.start_char-50):ent.end_char+50]
                    })
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        text_lower = text.lower()
        
        for degree in self.DEGREES:
            pattern = r'\b' + re.escape(degree) + r'\b'
            if re.search(pattern, text_lower):
                # Find context around degree
                for match in re.finditer(pattern, text_lower):
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    education.append({
                        'degree': degree.upper(),
                        'context': context.strip()
                    })
        
        # Remove duplicates
        seen_degrees = set()
        unique_education = []
        for edu in education:
            if edu['degree'] not in seen_degrees:
                seen_degrees.add(edu['degree'])
                unique_education.append(edu)
        
        return unique_education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        text_lower = text.lower()
        
        for cert_pattern in self.CERTIFICATIONS:
            pattern = r'\b' + re.escape(cert_pattern)
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                cert_text = text[start:end].strip()
                
                if cert_text not in certifications:
                    certifications.append(cert_text)
        
        return certifications[:10]  # Limit to top 10
    
    def _generate_summary(self, text: str) -> str:
        """Generate a brief summary of the resume"""
        lines = text.split('\n')
        
        # Find summary/objective section
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords) and len(line_lower) < 50:
                # Get next few lines
                summary_lines = []
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip() and not any(kw in lines[j].lower() for kw in ['experience', 'education', 'skills']):
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                
                if summary_lines:
                    return ' '.join(summary_lines)
        
        # Fallback: first few non-empty lines
        non_empty_lines = [l.strip() for l in lines[:10] if l.strip() and len(l.strip()) > 20]
        return ' '.join(non_empty_lines[:3]) if non_empty_lines else "No summary available"
    
    def _calculate_education_level(self, education: List[Dict]) -> int:
        """Calculate numeric education level"""
        if not education:
            return 0
        
        level_map = {
            'phd': 4, 'ph.d': 4, 'doctorate': 4,
            'masters': 3, 'master': 3, 'mba': 3, 'ms': 3, 'm.s': 3, 'm.tech': 3, 'mtech': 3, 'me': 3, 'm.e': 3,
            'bachelors': 2, 'bachelor': 2, 'bs': 2, 'b.s': 2, 'ba': 2, 'b.a': 2, 'b.tech': 2, 'btech': 2, 'be': 2, 'b.e': 2,
            'associate': 1, 'diploma': 1
        }
        
        max_level = 0
        for edu in education:
            degree = edu['degree'].lower()
            max_level = max(max_level, level_map.get(degree, 0))
        
        return max_level
    
    def calculate_job_match(self, parsed_resume: Dict, job_requirements: Dict) -> Dict[str, Any]:
        """
        Calculate how well resume matches job requirements
        
        Args:
            parsed_resume: Parsed resume data
            job_requirements: Job requirements dict with skills, experience, education
        
        Returns:
            Match score and breakdown
        """
        match_result = {
            'overall_score': 0,
            'skills_match': 0,
            'experience_match': 0,
            'education_match': 0,
            'matched_skills': [],
            'missing_skills': []
        }
        
        # Skills matching
        if 'required_skills' in job_requirements:
            required_skills = [s.lower() for s in job_requirements['required_skills']]
            candidate_skills = [s['name'].lower() for s in parsed_resume.get('skills', [])]
            
            matched = [s for s in required_skills if s in candidate_skills]
            missing = [s for s in required_skills if s not in candidate_skills]
            
            match_result['matched_skills'] = matched
            match_result['missing_skills'] = missing
            match_result['skills_match'] = (len(matched) / len(required_skills) * 100) if required_skills else 100
        
        # Experience matching
        if 'min_experience_years' in job_requirements:
            required_years = job_requirements['min_experience_years']
            candidate_years = parsed_resume.get('experience', {}).get('total_years', 0)
            
            if candidate_years >= required_years:
                match_result['experience_match'] = 100
            else:
                match_result['experience_match'] = (candidate_years / required_years * 100) if required_years > 0 else 0
        
        # Education matching
        if 'min_education_level' in job_requirements:
            required_level = job_requirements['min_education_level']
            candidate_level = parsed_resume.get('metadata', {}).get('education_level', 0)
            
            if candidate_level >= required_level:
                match_result['education_match'] = 100
            else:
                match_result['education_match'] = (candidate_level / required_level * 100) if required_level > 0 else 0
        
        # Calculate overall score (weighted average)
        weights = {'skills': 0.5, 'experience': 0.3, 'education': 0.2}
        match_result['overall_score'] = (
            match_result['skills_match'] * weights['skills'] +
            match_result['experience_match'] * weights['experience'] +
            match_result['education_match'] * weights['education']
        )
        
        return match_result


# Global singleton
_resume_parser = None


def get_resume_parser() -> ResumeParser:
    """Get global resume parser instance"""
    global _resume_parser
    if _resume_parser is None:
        _resume_parser = ResumeParser()
    return _resume_parser
