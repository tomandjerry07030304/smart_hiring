from datetime import datetime
from bson import ObjectId
from backend.security.encryption import encrypt_pii_fields, decrypt_pii_fields, is_encrypted


class User:
    """User model for candidates and recruiters"""
    
    collection_name = 'users'
    
    # PII fields that get encrypted before storage
    _pii_fields = ['email', 'full_name', 'phone']
    
    def __init__(self, email, password_hash, role, full_name, **kwargs):
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'candidate' or 'recruiter' or 'admin'
        self.full_name = full_name
        self.phone = kwargs.get('phone', '')
        self.profile_completed = kwargs.get('profile_completed', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_active = kwargs.get('is_active', True)
        self.linkedin_url = kwargs.get('linkedin_url', '')
        self.github_url = kwargs.get('github_url', '')
        
    def to_dict(self):
        """Convert to dictionary for MongoDB — encrypts PII fields"""
        data = {
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'profile_completed': self.profile_completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url
        }
        # Encrypt PII before storage
        return encrypt_pii_fields(data)
    
    def to_safe_dict(self):
        """Convert to dictionary WITHOUT encryption (for API responses after decryption)"""
        return {
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'profile_completed': self.profile_completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url
        }
    
    @staticmethod
    def from_dict(data):
        """Create User from dictionary — decrypts PII fields"""
        # Decrypt PII fields if they were encrypted
        decrypted = decrypt_pii_fields(data)
        return User(
            email=decrypted.get('email', ''),
            password_hash=decrypted.get('password_hash', ''),
            role=decrypted.get('role', ''),
            full_name=decrypted.get('full_name', ''),
            phone=decrypted.get('phone', ''),
            profile_completed=decrypted.get('profile_completed', False),
            created_at=decrypted.get('created_at', datetime.utcnow()),
            updated_at=decrypted.get('updated_at', datetime.utcnow()),
            is_active=decrypted.get('is_active', True),
            linkedin_url=decrypted.get('linkedin_url', ''),
            github_url=decrypted.get('github_url', '')
        )


class Candidate:
    """Extended profile for candidates"""
    
    collection_name = 'candidates'
    
    # PII fields that get encrypted before storage
    _pii_fields = ['phone_number', 'address', 'date_of_birth', 'ssn', 
                    'aadhaar_number', 'pan_number', 'passport_number']
    
    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.resume_file = kwargs.get('resume_file', '')
        self.resume_text = kwargs.get('resume_text', '')
        self.anonymized_resume = kwargs.get('anonymized_resume', '')
        self.skills = kwargs.get('skills', [])
        self.education = kwargs.get('education', [])
        self.experience = kwargs.get('experience', [])
        self.total_experience_years = kwargs.get('total_experience_years', 0)
        self.cci_score = kwargs.get('cci_score', None)  # Career Consistency Index
        self.applications = kwargs.get('applications', [])
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        
    def to_dict(self):
        """Convert to dictionary for MongoDB — encrypts PII fields"""
        data = {
            'user_id': self.user_id,
            'resume_file': self.resume_file,
            'resume_text': self.resume_text,
            'anonymized_resume': self.anonymized_resume,
            'skills': self.skills,
            'education': self.education,
            'experience': self.experience,
            'total_experience_years': self.total_experience_years,
            'cci_score': self.cci_score,
            'applications': self.applications,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        # Encrypt PII before storage
        return encrypt_pii_fields(data)
    
    @staticmethod
    def from_dict(data):
        """Create Candidate from dictionary — decrypts PII fields"""
        decrypted = decrypt_pii_fields(data)
        return Candidate(
            user_id=decrypted.get('user_id', ''),
            resume_file=decrypted.get('resume_file', ''),
            resume_text=decrypted.get('resume_text', ''),
            anonymized_resume=decrypted.get('anonymized_resume', ''),
            skills=decrypted.get('skills', []),
            education=decrypted.get('education', []),
            experience=decrypted.get('experience', []),
            total_experience_years=decrypted.get('total_experience_years', 0),
            cci_score=decrypted.get('cci_score', None),
            applications=decrypted.get('applications', []),
            created_at=decrypted.get('created_at', datetime.utcnow()),
            updated_at=decrypted.get('updated_at', datetime.utcnow())
        )
