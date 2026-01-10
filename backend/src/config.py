import os
from typing import Optional


class Config:
    """Base configuration class"""
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    APP_VERSION: str = os.environ.get('APP_VERSION', '1.0.0')
    ENVIRONMENT: str = os.environ.get('ENVIRONMENT', 'development')
    HOSTNAME: str = os.environ.get('HOSTNAME', 'unknown')
    PORT: int = int(os.environ.get('PORT', 5000))
    MAX_MESSAGE_LENGTH: int = int(os.environ.get('MAX_MESSAGE_LENGTH', '1000'))
    
    # Database configuration
    DB_USER: str = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD', 'postgres')
    DB_HOST: str = os.environ.get('DB_HOST', 'localhost')
    DB_PORT: str = os.environ.get('DB_PORT', '5432')
    DB_NAME: str = os.environ.get('DB_NAME', 'notes_db')
    SQLALCHEMY_DATABASE_URI: Optional[str] = os.environ.get('DATABASE_URL',
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # Logging configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security configuration
    SESSION_COOKIE_SECURE: bool = os.environ.get('ENVIRONMENT', 'development') != 'development'
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG: bool = True
    ENVIRONMENT: str = 'development'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG: bool = False
    ENVIRONMENT: str = 'production'
    SESSION_COOKIE_SECURE: bool = True


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG: bool = True
    TESTING: bool = True
    ENVIRONMENT: str = 'testing'
    WTF_CSRF_ENABLED: bool = False # Disable CSRF for testing
    CACHE_TYPE: str = 'simple'  # Use in-memory cache for testing


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.environ.get('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()