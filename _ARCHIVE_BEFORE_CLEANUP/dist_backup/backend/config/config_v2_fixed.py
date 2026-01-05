"""
Smart Hiring System - Enterprise Configuration Module
======================================================
Robust, production-grade configuration with:
- Pydantic BaseSettings for validation
- Lazy loading to prevent early import failures
- Docker-compatible environment variable loading
- Comprehensive validation with human-readable errors
- Support for .env files in multiple locations
- Zero caching issues

© 2025 Smart Hiring System
"""

import os
import sys
from pathlib import Path
from typing import Optional, Set, Dict, Any
from pydantic import BaseSettings, Field, validator, ValidationError
from pydantic import SecretStr
import logging

# Configure logging for config module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ENVIRONMENT FILE DISCOVERY
# ============================================================================
def find_env_file() -> Optional[Path]:
    """
    Locate .env file in multiple possible locations.
    Search order:
    1. Current working directory
    2. Script directory
    3. Parent of script directory (project root)
    4. /app (Docker container)
    5. Environment variable ENV_FILE
    """
    search_paths = [
        Path.cwd() / '.env',                                    # Current directory
        Path(__file__).parent.parent / '.env',                  # Project root
        Path(__file__).parent.parent / '.env.production',       # Production env
        Path('/app/.env'),                                      # Docker root
        Path('/app/.env.production'),                           # Docker production
    ]
    
    # Add custom path from environment variable
    custom_path = os.getenv('ENV_FILE')
    if custom_path:
        search_paths.insert(0, Path(custom_path))
    
    for path in search_paths:
        if path.exists() and path.is_file():
            logger.info(f"✅ Found .env file: {path}")
            return path
    
    logger.warning("⚠️  No .env file found in standard locations")
    return None


# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================
def load_environment():
    """
    Load environment variables from .env file if present.
    This function is called BEFORE config class initialization.
    """
    try:
        from dotenv import load_dotenv
        
        env_file = find_env_file()
        if env_file:
            load_dotenv(env_file, override=True)
            logger.info(f"📥 Loaded environment from: {env_file}")
        else:
            logger.info("📥 Using system environment variables (no .env file)")
    
    except ImportError:
        logger.warning("⚠️  python-dotenv not installed, using system environment only")
    except Exception as e:
        logger.error(f"❌ Error loading .env file: {e}")


# Load environment variables BEFORE class definition
load_environment()


# ============================================================================
# PYDANTIC CONFIGURATION CLASSES
# ============================================================================

class SecurityConfig(BaseSettings):
    """Security and authentication configuration"""
    
    # Secret Keys (REQUIRED)
    SECRET_KEY: str = Field(
        ...,  # Required
        min_length=32,
        description="Main application secret key (min 32 characters)"
    )
    
    JWT_SECRET_KEY: str = Field(
        ...,  # Required
        min_length=32,
        description="JWT signing secret key (min 32 characters)"
    )
    
    # Optional encryption key
    ENCRYPTION_KEY: Optional[str] = Field(
        None,
        min_length=64,
        max_length=64,
        description="Hex encryption key (exactly 64 characters)"
    )
    
    # JWT Settings
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(
        default=3600,
        ge=300,
        le=86400,
        description="JWT access token expiry in seconds (5 min - 24 hours)"
    )
    
    JWT_REFRESH_TOKEN_EXPIRES: int = Field(
        default=2592000,
        ge=86400,
        description="JWT refresh token expiry in seconds (min 24 hours)"
    )
    
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    @validator('SECRET_KEY', 'JWT_SECRET_KEY')
    def validate_secret_length(cls, v, field):
        """Ensure secrets are strong enough"""
        if not v:
            raise ValueError(f"{field.name} cannot be empty")
        
        if len(v) < 32:
            raise ValueError(
                f"{field.name} must be at least 32 characters long. "
                f"Current length: {len(v)}. "
                f"Generate a strong secret with: "
                f"python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        # Warn if using obvious placeholder values
        placeholder_values = [
            'changeme', 'your-secret', 'dev-secret', 'test-secret',
            'your-flask-secret-key', 'your-super-secret'
        ]
        
        if any(placeholder in v.lower() for placeholder in placeholder_values):
            logger.warning(
                f"⚠️  {field.name} contains placeholder text. "
                f"Use strong random values in production!"
            )
        
        return v
    
    @validator('ENCRYPTION_KEY')
    def validate_encryption_key(cls, v):
        """Validate encryption key format"""
        if v is None:
            return v
        
        if len(v) != 64:
            raise ValueError(
                f"ENCRYPTION_KEY must be exactly 64 hex characters. "
                f"Current length: {len(v)}. "
                f"Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        # Verify it's valid hex
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("ENCRYPTION_KEY must be a valid hexadecimal string")
        
        return v
    
    class Config:
        env_file = find_env_file()
        env_file_encoding = 'utf-8'
        case_sensitive = True


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017/smart_hiring_db",
        description="MongoDB connection string"
    )
    
    DB_NAME: str = Field(
        default="smart_hiring_db",
        description="Database name"
    )
    
    # MongoDB credentials (for docker-compose)
    MONGO_USERNAME: Optional[str] = Field(default="admin")
    MONGO_PASSWORD: Optional[str] = Field(default=None)
    
    @validator('MONGODB_URI')
    def validate_mongodb_uri(cls, v):
        """Ensure MongoDB URI is valid"""
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError(
                "MONGODB_URI must start with 'mongodb://' or 'mongodb+srv://'"
            )
        return v
    
    class Config:
        env_file = find_env_file()
        env_file_encoding = 'utf-8'


class RedisConfig(BaseSettings):
    """Redis and Celery configuration"""
    
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    CELERY_BROKER_URL: Optional[str] = Field(default=None)
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None)
    
    ENABLE_BACKGROUND_WORKERS: bool = Field(
        default=False,
        description="Enable Celery background workers"
    )
    
    @validator('CELERY_BROKER_URL', always=True)
    def set_celery_broker(cls, v, values):
        """Default to REDIS_URL if not specified"""
        return v or values.get('REDIS_URL')
    
    @validator('CELERY_RESULT_BACKEND', always=True)
    def set_celery_backend(cls, v, values):
        """Default to REDIS_URL if not specified"""
        return v or values.get('REDIS_URL')
    
    class Config:
        env_file = find_env_file()
        env_file_encoding = 'utf-8'


class ApplicationConfig(BaseSettings):
    """Application-level configuration"""
    
    # Application Identity
    APP_ENV: str = Field(
        default="development",
        description="Application environment"
    )
    
    APP_NAME: str = Field(
        default="SmartHiringSystem",
        description="Application name"
    )
    
    APP_VERSION: str = Field(
        default="2.0.0",
        description="Application version"
    )
    
    PORT: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Application port"
    )
    
    # Debug & Development
    DEBUG: bool = Field(
        default=False,
        description="Debug mode (NEVER enable in production)"
    )
    
    FLASK_DEBUG: bool = Field(
        default=False,
        description="Flask debug mode"
    )
    
    TESTING: bool = Field(
        default=False,
        description="Testing mode"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    LOG_FILE: str = Field(
        default="logs/app.log",
        description="Log file path"
    )
    
    # CORS & Frontend
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS"
    )
    
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    @validator('APP_ENV')
    def validate_environment(cls, v):
        """Validate environment name"""
        valid_envs = ['development', 'production', 'staging', 'testing']
        if v.lower() not in valid_envs:
            logger.warning(
                f"⚠️  APP_ENV '{v}' not standard. "
                f"Recommended: {', '.join(valid_envs)}"
            )
        return v.lower()
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of: {', '.join(valid_levels)}"
            )
        return v_upper
    
    def get_allowed_origins_list(self) -> list:
        """Parse comma-separated ALLOWED_ORIGINS into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
    
    class Config:
        env_file = find_env_file()
        env_file_encoding = 'utf-8'


# ============================================================================
# UNIFIED CONFIGURATION CLASS
# ============================================================================

class Config:
    """
    Unified configuration class that lazy-loads all sub-configurations.
    This prevents early validation failures during import.
    """
    
    _security_config: Optional[SecurityConfig] = None
    _database_config: Optional[DatabaseConfig] = None
    _redis_config: Optional[RedisConfig] = None
    _app_config: Optional[ApplicationConfig] = None
    _validation_errors: list = []
    
    @classmethod
    def load(cls, validate: bool = True) -> 'Config':
        """
        Load all configuration sections.
        
        Args:
            validate: If True, raise exception on validation errors.
                     If False, log errors but continue.
        
        Returns:
            Config instance
        """
        instance = cls()
        
        try:
            # Load all config sections
            instance._security_config = SecurityConfig()
            instance._database_config = DatabaseConfig()
            instance._redis_config = RedisConfig()
            instance._app_config = ApplicationConfig()
            
            logger.info("✅ Configuration loaded successfully")
            
        except ValidationError as e:
            error_msg = "❌ Configuration validation failed:\n"
            for error in e.errors():
                field = ' -> '.join(str(x) for x in error['loc'])
                message = error['msg']
                error_msg += f"  • {field}: {message}\n"
            
            instance._validation_errors.append(error_msg)
            logger.error(error_msg)
            
            if validate:
                raise ValueError(error_msg)
        
        except Exception as e:
            error_msg = f"❌ Unexpected error loading configuration: {e}"
            instance._validation_errors.append(error_msg)
            logger.error(error_msg)
            
            if validate:
                raise
        
        return instance
    
    @property
    def security(self) -> SecurityConfig:
        """Access security configuration"""
        if self._security_config is None:
            self._security_config = SecurityConfig()
        return self._security_config
    
    @property
    def database(self) -> DatabaseConfig:
        """Access database configuration"""
        if self._database_config is None:
            self._database_config = DatabaseConfig()
        return self._database_config
    
    @property
    def redis(self) -> RedisConfig:
        """Access Redis configuration"""
        if self._redis_config is None:
            self._redis_config = RedisConfig()
        return self._redis_config
    
    @property
    def app(self) -> ApplicationConfig:
        """Access application configuration"""
        if self._app_config is None:
            self._app_config = ApplicationConfig()
        return self._app_config
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary (safe for logging - no secrets)"""
        return {
            'app_name': self.app.APP_NAME,
            'app_version': self.app.APP_VERSION,
            'environment': self.app.APP_ENV,
            'port': self.app.PORT,
            'debug': self.app.DEBUG,
            'database': self.database.DB_NAME,
            'redis_enabled': self.redis.ENABLE_BACKGROUND_WORKERS,
            'log_level': self.app.LOG_LEVEL,
            'secret_key_length': len(self.security.SECRET_KEY),
            'jwt_expiry': self.security.JWT_ACCESS_TOKEN_EXPIRES,
        }
    
    def validate_all(self) -> tuple[bool, list]:
        """
        Validate all configuration sections.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            _ = self.security
        except Exception as e:
            errors.append(f"Security config: {e}")
        
        try:
            _ = self.database
        except Exception as e:
            errors.append(f"Database config: {e}")
        
        try:
            _ = self.redis
        except Exception as e:
            errors.append(f"Redis config: {e}")
        
        try:
            _ = self.app
        except Exception as e:
            errors.append(f"Application config: {e}")
        
        return (len(errors) == 0, errors)


# ============================================================================
# LEGACY COMPATIBILITY LAYER
# ============================================================================

class DevelopmentConfig:
    """Legacy compatibility - Development configuration"""
    def __init__(self):
        self.config = Config.load(validate=False)
        self.DEBUG = True
        self.FLASK_ENV = 'development'
        self._copy_from_new_config()
    
    def _copy_from_new_config(self):
        """Copy values from new config system"""
        self.SECRET_KEY = self.config.security.SECRET_KEY
        self.JWT_SECRET_KEY = self.config.security.JWT_SECRET_KEY
        self.JWT_ACCESS_TOKEN_EXPIRES = self.config.security.JWT_ACCESS_TOKEN_EXPIRES
        self.MONGODB_URI = self.config.database.MONGODB_URI
        self.DB_NAME = self.config.database.DB_NAME
        self.FRONTEND_URL = self.config.app.FRONTEND_URL


class ProductionConfig:
    """Legacy compatibility - Production configuration"""
    def __init__(self):
        self.config = Config.load(validate=True)
        self.DEBUG = False
        self.FLASK_ENV = 'production'
        self._copy_from_new_config()
    
    def _copy_from_new_config(self):
        """Copy values from new config system"""
        self.SECRET_KEY = self.config.security.SECRET_KEY
        self.JWT_SECRET_KEY = self.config.security.JWT_SECRET_KEY
        self.JWT_ACCESS_TOKEN_EXPIRES = self.config.security.JWT_ACCESS_TOKEN_EXPIRES
        self.MONGODB_URI = self.config.database.MONGODB_URI
        self.DB_NAME = self.config.database.DB_NAME
        self.FRONTEND_URL = self.config.app.FRONTEND_URL


class TestingConfig:
    """Legacy compatibility - Testing configuration"""
    def __init__(self):
        self.config = Config.load(validate=False)
        self.TESTING = True
        self.DB_NAME = 'smart_hiring_test_db'
        self._copy_from_new_config()
    
    def _copy_from_new_config(self):
        """Copy values from new config system"""
        self.SECRET_KEY = self.config.security.SECRET_KEY
        self.JWT_SECRET_KEY = self.config.security.JWT_SECRET_KEY
        self.JWT_ACCESS_TOKEN_EXPIRES = self.config.security.JWT_ACCESS_TOKEN_EXPIRES
        self.MONGODB_URI = self.config.database.MONGODB_URI
        self.FRONTEND_URL = self.config.app.FRONTEND_URL


# Legacy config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# ============================================================================
# MODULE-LEVEL INSTANCE (for backward compatibility)
# ============================================================================

# Create default instance (lazy-loaded, no validation on import)
_default_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global config instance.
    Safe to call during imports - validation happens on first access.
    """
    global _default_config
    if _default_config is None:
        _default_config = Config.load(validate=False)
    return _default_config


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    """
    Example usage and testing
    """
    print("=" * 80)
    print("SMART HIRING SYSTEM - Configuration Test")
    print("=" * 80)
    
    try:
        # Load configuration
        cfg = Config.load(validate=True)
        
        # Print summary
        summary = cfg.get_summary()
        print("\n✅ Configuration Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Validate
        is_valid, errors = cfg.validate_all()
        if is_valid:
            print("\n✅ All configuration sections valid!")
        else:
            print("\n❌ Configuration errors:")
            for error in errors:
                print(f"  • {error}")
    
    except Exception as e:
        print(f"\n❌ Configuration failed: {e}")
        sys.exit(1)
