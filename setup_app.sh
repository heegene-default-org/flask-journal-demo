#!/bin/bash
# Flask 일기장 애플리케이션 디렉토리 구조 생성 스크립트

echo "Flask 일기장 애플리케이션 디렉토리 구조 생성 중..."

# 디렉토리 생성
mkdir -p app/templates
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p tests
mkdir -p logs
mkdir -p uploads
mkdir -p migrations

# __init__.py 파일 생성
cat > app/__init__.py << 'EOF'
"""Flask 일기장 애플리케이션 메인 파일"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache

# 확장 초기화
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()


def create_app(config_name=None):
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    
    # 설정 로드
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # 기본 설정
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://journal_user:journal_pass@localhost:5432/journal_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Redis 캐시 설정
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    
    # 로그인 설정
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    
    # 블루프린트 등록
    from app.routes import main_bp, auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 헬스체크 엔드포인트
    @app.route('/health')
    def health_check():
        """헬스체크 엔드포인트 - Docker 컨테이너 모니터링용"""
        return {'status': 'healthy', 'service': 'flask-journal'}, 200
    
    return app
EOF

echo "✓ app/__init__.py 생성 완료"

# 디렉토리 생성 완료 메시지
echo "✓ 디렉토리 구조 생성 완료"
echo ""
echo "생성된 디렉토리:"
echo "  - app/"
echo "  - app/templates/"
echo "  - app/static/css/"
echo "  - app/static/js/"
echo "  - tests/"
echo "  - logs/"
echo "  - uploads/"
echo "  - migrations/"
echo ""
echo "다음 단계:"
echo "1. 나머지 Flask 애플리케이션 파일 작성 (models.py, routes.py)"
echo "2. 템플릿 파일 작성 (templates/*.html)"
echo "3. Docker 컨테이너 실행: docker-compose up -d"
echo "4. 데이터베이스 마이그레이션: docker-compose exec web flask db upgrade"
echo "5. 테스트 데이터 생성: docker-compose exec web flask create-test-data"
