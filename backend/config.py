"""
Configuration settings for FVS Result Management System
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fvs_results.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security: Require SECRET_KEY in production
    @staticmethod
    def get_secret_key():
        key = os.environ.get('SECRET_KEY')
        if not key:
            if os.environ.get('FLASK_ENV', 'development') == 'production':
                raise ValueError("SECRET_KEY environment variable must be set in production")
            return 'dev-only-key-never-use-in-production'  # Only for development
        return key
    
    SECRET_KEY = get_secret_key()
    JSON_SORT_KEYS = False
    
    # Rate limiting configuration
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
