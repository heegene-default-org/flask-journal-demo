# Flask 일기장 애플리케이션 - 실행 가이드

## 🎯 이 저장소에 대해

이 저장소는 Flask 기반 일기장 애플리케이션을 Docker로 컨테이너화하는 완전한 솔루션을 제공합니다.

## 📦 포함된 내용

### ✅ 완성된 Docker 인프라
- Dockerfile (멀티스테이지 빌드)
- docker-compose.yml (기본 구성)
- docker-compose.dev.yml (개발 환경)
- docker-compose.prod.yml (프로덕션 환경)
- docker-compose.test.yml (테스트 환경)
- Nginx 리버스 프록시 설정
- PostgreSQL 초기화 스크립트
- Redis 캐시 설정

### 📚 완전한 문서
- **CONTAINERIZATION_GUIDE.md** - 150+ 페이지 분량의 완전한 가이드
- **DOCKER_QUICKSTART.md** - 빠른 시작 가이드
- **CONTAINERIZATION_SUMMARY.md** - 요약 문서

### 🚀 예제 Flask 애플리케이션 코드
- run.py - 애플리케이션 엔트리포인트
- config.py - 설정 파일
- requirements.txt - Python 종속성

## 🏃 빠른 시작 (3단계)

### 1️⃣ 사전 요구사항 확인

```bash
# Docker 버전 확인 (20.10 이상 필요)
docker --version

# Docker Compose 버전 확인 (2.0 이상 필요)
docker-compose --version
```

### 2️⃣ 환경 설정

```bash
# 저장소 클론 (이미 클론했다면 스킵)
git clone https://github.com/heegene-default-org/flask-journal-demo.git
cd flask-journal-demo

# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집 (중요!)
# SECRET_KEY를 강력한 랜덤 문자열로 변경
# 예: openssl rand -hex 32
```

### 3️⃣ 애플리케이션 실행

#### 옵션 A: 개발 환경으로 시작

```bash
# 개발 환경 실행 (코드 핫 리로드, 개발 도구 포함)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 로그 확인
docker-compose logs -f web

# 접속
# - Flask 앱: http://localhost:5000
# - Adminer (DB GUI): http://localhost:8080
# - Redis Commander: http://localhost:8081
```

#### 옵션 B: 프로덕션 환경으로 시작

```bash
# 프로덕션 환경 실행
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 접속
# - Nginx: http://localhost
```

## 📝 Flask 애플리케이션 개발 시작하기

현재 이 저장소에는 Docker 인프라만 준비되어 있습니다. 
실제 Flask 애플리케이션을 개발하려면 다음 단계를 따르세요:

### 1. 디렉토리 구조 생성

```bash
# 자동 생성 스크립트 실행
chmod +x setup_app.sh
./setup_app.sh

# 또는 수동으로 생성
mkdir -p app/templates app/static/css app/static/js tests
```

### 2. Flask 애플리케이션 파일 작성

#### `app/__init__.py` - Flask 앱 초기화
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    db.init_app(app)
    return app
```

#### `app/models.py` - 데이터베이스 모델
```python
from app import db

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### `app/routes.py` - 라우트 및 뷰
```python
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')
```

### 3. 템플릿 작성

#### `app/templates/base.html` - 기본 템플릿
```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask Journal</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

### 4. 데이터베이스 초기화

```bash
# 컨테이너 내부에서 실행
docker-compose exec web flask db init
docker-compose exec web flask db migrate -m "Initial migration"
docker-compose exec web flask db upgrade
```

## 🔧 유용한 명령어

### 컨테이너 관리

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 재시작
docker-compose restart web

# 모든 서비스 중지
docker-compose down

# 볼륨까지 모두 삭제 (주의: 데이터 삭제됨)
docker-compose down -v
```

### 개발 작업

```bash
# Flask 쉘 접속
docker-compose exec web flask shell

# 컨테이너 내부 Bash 접속
docker-compose exec web bash

# 데이터베이스 마이그레이션
docker-compose exec web flask db migrate -m "설명"
docker-compose exec web flask db upgrade

# 테스트 실행
docker-compose exec web pytest
```

### 디버깅

```bash
# 컨테이너 상태 확인
docker-compose ps

# 리소스 사용량
docker stats

# 네트워크 확인
docker network ls
docker network inspect flask-journal-demo_journal-network

# 볼륨 확인
docker volume ls
```

## 📖 더 알아보기

### 상세 문서 (필독!)

1. **[CONTAINERIZATION_GUIDE.md](CONTAINERIZATION_GUIDE.md)** 
   - 완전한 컨테이너화 가이드
   - 모범 사례 및 최적화 방법
   - 보안 고려사항
   - 프로덕션 배포 전략

2. **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)**
   - Docker 명령어 치트시트
   - 문제 해결 가이드
   - 모니터링 방법

3. **[CONTAINERIZATION_SUMMARY.md](CONTAINERIZATION_SUMMARY.md)**
   - 빠른 참조 요약

## 🎓 학습 경로

### 초급 (1-2주)
1. Docker 기본 개념 이해
2. 로컬에서 컨테이너 실행
3. 간단한 Flask 앱 개발
4. 데이터베이스 연동

### 중급 (2-4주)
5. 멀티컨테이너 구성 마스터
6. Nginx 리버스 프록시 설정
7. Redis 캐싱 구현
8. 로깅 및 모니터링

### 고급 (1-3개월)
9. CI/CD 파이프라인 구축
10. 프로덕션 환경 배포
11. Kubernetes 마이그레이션
12. 성능 최적화

## 🐛 문제 해결

### 자주 발생하는 문제

#### 1. 포트 충돌
```bash
# 에러: port is already allocated
# 해결: docker-compose.yml에서 포트 번호 변경
ports:
  - "5001:5000"  # 5000 대신 5001 사용
```

#### 2. 데이터베이스 연결 실패
```bash
# 헬스체크 확인
docker-compose exec db pg_isready

# 데이터베이스 로그 확인
docker-compose logs db

# 재시작
docker-compose restart db
```

#### 3. 권한 문제
```bash
# 디렉토리 권한 설정
sudo chown -R $USER:$USER logs uploads
chmod 755 logs uploads
```

## 💡 팁 & 트릭

### 개발 효율성 향상

```bash
# alias 설정 (.bashrc 또는 .zshrc에 추가)
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcr='docker-compose restart'
alias dce='docker-compose exec'

# 사용 예
dcu                    # 서비스 시작
dcl web                # 웹 서비스 로그
dce web flask shell    # Flask 쉘
```

### 데이터베이스 백업

```bash
# 백업
docker-compose exec db pg_dump -U journal_user journal_db > backup_$(date +%Y%m%d).sql

# 복원
docker-compose exec -T db psql -U journal_user journal_db < backup_20240101.sql
```

### 이미지 크기 최적화

```bash
# 이미지 크기 확인
docker images flask-journal-demo*

# 최적화 도구 사용
docker-slim build --target flask-journal-demo_web
```

## 🔐 보안 체크리스트

실제 프로덕션에 배포하기 전에 확인하세요:

- [ ] `.env` 파일이 Git에 커밋되지 않았는지 확인
- [ ] SECRET_KEY를 강력한 랜덤 문자열로 변경
- [ ] 데이터베이스 비밀번호를 기본값에서 변경
- [ ] DEBUG 모드를 프로덕션에서 비활성화
- [ ] HTTPS/SSL 인증서 설정
- [ ] 방화벽 규칙 구성
- [ ] 정기적인 보안 업데이트 적용
- [ ] 취약점 스캔 실행

## 🤝 기여하기

기여는 언제나 환영합니다!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

## 🆘 도움이 필요하신가요?

- 📧 이메일: support@example.com
- 💬 Discord: [링크]
- 🐙 Issues: https://github.com/heegene-default-org/flask-journal-demo/issues

---

**Happy Coding! 🚀**

이 프로젝트를 통해 Docker와 Flask를 마스터하세요!
