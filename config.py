"""Flask 애플리케이션 설정"""
import os


class Config:
    """기본 설정"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://journal_user:journal_pass@db:5432/journal_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis 캐시
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://cache:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 보안
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 업로드
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """테스트 환경 설정"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://test_user:test_pass@db:5432/test_db'
    )
    WTF_CSRF_ENABLED = False


# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
