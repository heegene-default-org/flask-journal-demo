# Flask Journal Demo - Docker 빠른 시작 가이드

## 🚀 빠른 시작

### 사전 요구사항

- Docker 20.10 이상
- Docker Compose 2.0 이상

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열고 SECRET_KEY 등 필요한 값을 수정
```

### 2. 컨테이너 실행

#### 개발 환경

```bash
# 개발 모드로 실행 (코드 변경 시 자동 리로드)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 로그 확인
docker-compose logs -f web
```

#### 프로덕션 환경

```bash
# 프로덕션 모드로 실행
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. 애플리케이션 접속

- **Flask 앱**: http://localhost:5000
- **Nginx (프록시)**: http://localhost
- **Adminer (DB 관리)**: http://localhost:8080 (개발 모드만)
- **Redis Commander**: http://localhost:8081 (개발 모드만)

### 4. 데이터베이스 마이그레이션

```bash
# 마이그레이션 초기화
docker-compose exec web flask db init

# 마이그레이션 생성
docker-compose exec web flask db migrate -m "Initial migration"

# 마이그레이션 적용
docker-compose exec web flask db upgrade
```

## 📋 유용한 명령어

### Docker 기본 명령어

```bash
# 모든 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d web db

# 서비스 중지
docker-compose stop

# 서비스 중지 및 컨테이너 제거
docker-compose down

# 볼륨까지 모두 제거 (주의: 데이터 삭제됨)
docker-compose down -v

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f web

# 실행 중인 컨테이너 목록
docker-compose ps

# 리소스 사용량 확인
docker stats
```

### 애플리케이션 명령어

```bash
# Flask 쉘 접속
docker-compose exec web flask shell

# 컨테이너 내부 쉘 접속
docker-compose exec web bash

# Python 스크립트 실행
docker-compose exec web python script.py

# 테스트 실행
docker-compose exec web pytest

# 데이터베이스 백업
docker-compose exec db pg_dump -U journal_user journal_db > backup.sql

# 데이터베이스 복원
docker-compose exec -T db psql -U journal_user journal_db < backup.sql
```

### 이미지 빌드 및 관리

```bash
# 이미지 다시 빌드
docker-compose build

# 캐시 없이 빌드
docker-compose build --no-cache

# 특정 서비스만 빌드
docker-compose build web

# 이미지 목록 확인
docker images

# 사용하지 않는 이미지 제거
docker image prune -a

# 이미지 크기 확인
docker images flask-journal-demo*
```

## 🔧 문제 해결

### 포트 충돌

```bash
# 이미 사용 중인 포트 확인
lsof -i :5000
# 또는
netstat -ano | findstr :5000  # Windows

# docker-compose.yml에서 포트 변경
# ports:
#   - "5001:5000"  # 호스트 포트를 5001로 변경
```

### 데이터베이스 연결 실패

```bash
# 데이터베이스 헬스체크 확인
docker-compose exec db pg_isready -U journal_user

# 데이터베이스 로그 확인
docker-compose logs db

# 컨테이너 재시작
docker-compose restart db
```

### 권한 문제

```bash
# 로그 디렉토리 권한 설정
mkdir -p logs uploads
chmod 755 logs uploads

# 컨테이너 사용자 확인
docker-compose exec web id
```

### 캐시 정리

```bash
# Redis 캐시 비우기
docker-compose exec cache redis-cli FLUSHALL

# Docker 빌드 캐시 정리
docker builder prune
```

## 📊 모니터링

### 헬스체크 확인

```bash
# 모든 서비스 상태 확인
docker-compose ps

# 웹 애플리케이션 헬스체크
curl http://localhost:5000/health

# 데이터베이스 헬스체크
docker-compose exec db pg_isready

# Redis 헬스체크
docker-compose exec cache redis-cli ping
```

### 리소스 모니터링

```bash
# 실시간 리소스 사용량
docker stats

# 특정 컨테이너만 모니터링
docker stats flask-journal-web

# 디스크 사용량
docker system df
```

## 🔒 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] SECRET_KEY를 강력한 랜덤 문자열로 변경
- [ ] 프로덕션에서 DEBUG 모드 비활성화
- [ ] 데이터베이스 비밀번호를 기본값에서 변경
- [ ] HTTPS 인증서 설정 (Let's Encrypt 권장)
- [ ] 방화벽 규칙 설정
- [ ] 정기적인 보안 업데이트 적용

## 📚 추가 자료

- [상세 컨테이너화 가이드](CONTAINERIZATION_GUIDE.md)
- [Docker 공식 문서](https://docs.docker.com/)
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)

## 🐛 이슈 리포팅

문제가 발생하면 다음 정보와 함께 이슈를 등록해주세요:

```bash
# 시스템 정보
docker version
docker-compose version

# 로그
docker-compose logs > logs.txt

# 컨테이너 상태
docker-compose ps
```
