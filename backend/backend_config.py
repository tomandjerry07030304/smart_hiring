"""
Backend Configuration Loader
Loads configuration from environment variables with validation and defaults
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try .env.template as fallback
    template_path = Path(__file__).parent.parent / '.env.template'
    if template_path.exists():
        load_dotenv(template_path)


class Config:
    """Base configuration class"""
    
    # Application Settings
    APP_ENV = os.getenv('APP_ENV', 'development')
    APP_NAME = os.getenv('APP_NAME', 'SmartHiringSystem')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 8000))
    
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/smart_hiring_db')
    DB_NAME = 'smart_hiring_db'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10 MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # ML Models
    MODEL_PATH = os.getenv('MODEL_PATH', './ml_models/')
    ENABLE_ML_FEATURES = os.getenv('ENABLE_ML_FEATURES', 'true').lower() == 'true'
    
    # Security
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    # Set token expiry to 24 hours (86400 seconds) to prevent frequent expiration
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    
    # File Upload Settings
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10485760))  # 10 MB
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,doc,txt').split(',')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'smart_hiring_resumes')
    
    # Features
    ENABLE_AUTO_UPDATE = os.getenv('ENABLE_AUTO_UPDATE', 'false').lower() == 'true'
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    ENABLE_FAIRNESS_AUDIT = os.getenv('ENABLE_FAIRNESS_AUDIT', 'true').lower() == 'true'
    ENABLE_RESUME_ANONYMIZATION = os.getenv('ENABLE_RESUME_ANONYMIZATION', 'true').lower() == 'true'
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', 'noreply@smarthiring.com')
    
    # API Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # Development/Debug
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    TESTING = os.getenv('TESTING', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)"""
        errors = []
        
        # Check required settings
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production' and cls.APP_ENV == 'production':
            errors.append("SECRET_KEY must be changed in production environment")
        
        if cls.ADMIN_PASSWORD == 'changeme' and cls.APP_ENV == 'production':
            errors.append("ADMIN_PASSWORD must be changed in production environment")
        
        if not cls.MONGODB_URI:
            errors.append("MONGODB_URI is required")
        
        if cls.ENABLE_EMAIL_NOTIFICATIONS and (not cls.SMTP_USERNAME or not cls.SMTP_PASSWORD):
            errors.append("Email notifications enabled but SMTP credentials not configured")
        
        # Create necessary directories
        try:
            Path(cls.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
            Path(cls.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
            Path(cls.MODEL_PATH).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Failed to create necessary directories: {str(e)}")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def setup_logging(cls):
        """Setup logging configuration"""
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_dir = Path(cls.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=cls.LOG_MAX_SIZE,
            backupCount=cls.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, cls.LOG_LEVEL))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, cls.LOG_LEVEL))
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, cls.LOG_LEVEL))
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        return root_logger
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """Get configuration summary (safe for logging - no secrets)"""
        return {
            'APP_ENV': cls.APP_ENV,
            'APP_NAME': cls.APP_NAME,
            'APP_VERSION': cls.APP_VERSION,
            'PORT': cls.PORT,
            'DB_NAME': cls.DB_NAME,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'ENABLE_ML_FEATURES': cls.ENABLE_ML_FEATURES,
            'ENABLE_EMAIL_NOTIFICATIONS': cls.ENABLE_EMAIL_NOTIFICATIONS,
            'ENABLE_FAIRNESS_AUDIT': cls.ENABLE_FAIRNESS_AUDIT,
            'ENABLE_RESUME_ANONYMIZATION': cls.ENABLE_RESUME_ANONYMIZATION,
            'RATE_LIMIT_ENABLED': cls.RATE_LIMIT_ENABLED,
        }


# Create singleton instance
config = Config()

# Validate on import
is_valid, errors = config.validate()
if not is_valid:
    print("⚠️  Configuration validation warnings:")
    for error in errors:
        print(f"   - {error}")
