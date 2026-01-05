import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # SECURITY: Generate strong secrets using: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Validate secrets are set
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        raise ValueError('SECRET_KEY must be set and at least 32 characters long')
    if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
        raise ValueError('JWT_SECRET_KEY must be set and at least 32 characters long')
    
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Database
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'smart_hiring_db')
    
    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # LinkedIn
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
    
    # Fairness thresholds
    DEMOGRAPHIC_PARITY_THRESHOLD = float(os.getenv('DEMOGRAPHIC_PARITY_THRESHOLD', 0.1))
    EQUAL_OPPORTUNITY_THRESHOLD = float(os.getenv('EQUAL_OPPORTUNITY_THRESHOLD', 0.1))
    
    # File upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/resumes')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
    
    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DB_NAME = 'smart_hiring_test_db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
