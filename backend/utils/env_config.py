"""
Environment Configuration Manager
Handles environment-specific settings and validates configuration
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Manages environment configuration"""
    
    def __init__(self):
        """Initialize configuration"""
        self.env = os.getenv('FLASK_ENV', 'development')
        self._validate_config()
    
    def _validate_config(self):
        """Validate critical configuration"""
        issues = []
        
        # Check JWT secret
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        if not jwt_secret or jwt_secret == 'your-super-secret-jwt-key-change-this-in-production':
            if self.env == 'production':
                issues.append("⚠️ JWT_SECRET_KEY must be set to a secure value in production")
        
        # Check encryption key
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key and self.env == 'production':
            issues.append("⚠️ ENCRYPTION_KEY should be set for PII encryption in production")
        
        # Check MongoDB URI
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            issues.append("⚠️ MONGODB_URI is not set")
        
        # Check Redis for production
        redis_url = os.getenv('REDIS_URL')
        if not redis_url and self.env == 'production':
            issues.append("⚠️ REDIS_URL recommended for production (queuing & caching)")
        
        # Log issues
        if issues:
            logger.warning("Configuration issues detected:")
            for issue in issues:
                logger.warning(f"  {issue}")
            
            if self.env == 'production':
                logger.error("❌ Critical configuration issues in production!")
    
    # Application settings
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.env == 'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.env == 'development'
    
    @property
    def debug(self) -> bool:
        """Get debug mode"""
        return os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Security settings
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key"""
        return os.getenv('JWT_SECRET_KEY', 'default-dev-secret')
    
    @property
    def encryption_key(self) -> Optional[str]:
        """Get encryption key"""
        return os.getenv('ENCRYPTION_KEY')
    
    @property
    def enable_2fa(self) -> bool:
        """Check if 2FA is enabled"""
        return os.getenv('ENABLE_2FA', 'false').lower() == 'true'
    
    # Database settings
    @property
    def mongodb_uri(self) -> str:
        """Get MongoDB URI"""
        return os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    
    @property
    def db_name(self) -> str:
        """Get database name"""
        return os.getenv('DB_NAME', 'smart_hiring')
    
    # Redis settings
    @property
    def redis_url(self) -> Optional[str]:
        """Get Redis URL"""
        return os.getenv('REDIS_URL')
    
    @property
    def enable_redis(self) -> bool:
        """Check if Redis is enabled"""
        return bool(self.redis_url)
    
    # Worker settings
    @property
    def enable_background_workers(self) -> bool:
        """Check if background workers are enabled"""
        return os.getenv('ENABLE_BACKGROUND_WORKERS', 'true').lower() == 'true'
    
    @property
    def num_workers(self) -> int:
        """Get number of worker threads"""
        return int(os.getenv('NUM_WORKERS', '2'))
    
    # File upload settings
    @property
    def upload_folder(self) -> str:
        """Get upload folder path"""
        return os.getenv('UPLOAD_FOLDER', 'backend/uploads')
    
    @property
    def max_file_size(self) -> int:
        """Get max file size in bytes"""
        return int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10 MB default
    
    @property
    def enable_virus_scan(self) -> bool:
        """Check if virus scanning is enabled"""
        return os.getenv('ENABLE_VIRUS_SCAN', 'false').lower() == 'true'
    
    # Feature flags
    @property
    def enable_analytics(self) -> bool:
        """Check if analytics is enabled"""
        return os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
    
    @property
    def enable_audit_logging(self) -> bool:
        """Check if audit logging is enabled"""
        return os.getenv('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    
    # Compliance settings
    @property
    def gdpr_mode(self) -> bool:
        """Check if GDPR mode is enabled"""
        return os.getenv('GDPR_MODE', 'true').lower() == 'true'
    
    @property
    def data_retention_days(self) -> int:
        """Get data retention period in days"""
        return int(os.getenv('DATA_RETENTION_DAYS', '2555'))  # 7 years default
    
    # External services
    @property
    def sentry_dsn(self) -> Optional[str]:
        """Get Sentry DSN"""
        return os.getenv('SENTRY_DSN')
    
    @property
    def sendgrid_api_key(self) -> Optional[str]:
        """Get SendGrid API key"""
        return os.getenv('SENDGRID_API_KEY')
    
    # Monitoring
    @property
    def log_level(self) -> str:
        """Get log level"""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    def get_config_summary(self) -> dict:
        """Get configuration summary (safe for logging)"""
        return {
            'environment': self.env,
            'debug': self.debug,
            'database': 'MongoDB (connected)' if self.mongodb_uri else 'Not configured',
            'redis': 'Enabled' if self.enable_redis else 'Disabled',
            'background_workers': 'Enabled' if self.enable_background_workers else 'Disabled',
            '2fa': 'Enabled' if self.enable_2fa else 'Disabled',
            'virus_scan': 'Enabled' if self.enable_virus_scan else 'Disabled',
            'gdpr_mode': 'Enabled' if self.gdpr_mode else 'Disabled',
            'analytics': 'Enabled' if self.enable_analytics else 'Disabled',
            'audit_logging': 'Enabled' if self.enable_audit_logging else 'Disabled'
        }


# Global configuration instance
env_config = EnvironmentConfig()


def print_startup_banner():
    """Print startup banner with configuration"""
    config = env_config.get_config_summary()
    
    print("\n" + "="*70)
    print("🚀 Smart Hiring System - Enterprise Edition")
    print("="*70)
    print(f"📍 Environment: {config['environment']}")
    print(f"🔧 Debug Mode: {config['debug']}")
    print(f"🗄️  Database: {config['database']}")
    print(f"⚡ Redis: {config['redis']}")
    print(f"👷 Background Workers: {config['background_workers']}")
    print(f"🔐 Two-Factor Auth: {config['2fa']}")
    print(f"🦠 Virus Scanning: {config['virus_scan']}")
    print(f"📊 Analytics: {config['analytics']}")
    print(f"📝 Audit Logging: {config['audit_logging']}")
    print(f"🌍 GDPR Mode: {config['gdpr_mode']}")
    print("="*70 + "\n")
