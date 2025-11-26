# Flask Journal Demo

Flask 기반 일기장 애플리케이션 데모 프로젝트

## 📦 컨테이너화

이 프로젝트는 Docker를 사용하여 완전히 컨테이너화되어 있습니다.

### 빠른 시작

```bash
# 1. 환경 변수 설정
cp .env.example .env

# 2. 컨테이너 실행 (개발 환경)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 3. 애플리케이션 접속
# http://localhost:5000
```

### 주요 기능

- 🐳 **Docker 컨테이너화**: 일관된 개발 및 배포 환경
- 🔄 **Docker Compose**: 다중 컨테이너 오케스트레이션
- 📊 **PostgreSQL**: 안정적인 데이터 저장
- ⚡ **Redis**: 고성능 캐싱
- 🔒 **Nginx**: 리버스 프록시 및 SSL 지원
- 🚀 **CI/CD**: GitHub Actions 자동화

### 문서

- [📖 상세 컨테이너화 가이드](CONTAINERIZATION_GUIDE.md) - 완전한 가이드
- [🚀 Docker 빠른 시작](DOCKER_QUICKSTART.md) - 빠른 시작 가이드

### 아키텍처

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │
┌──────▼──────┐
│   Nginx     │ (리버스 프록시)
└──────┬──────┘
       │
┌──────▼──────┐
│   Flask     │ (웹 애플리케이션)
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌─▼────┐
│ DB  │ │Redis │
└─────┘ └──────┘
```

### 시스템 요구사항

- Docker 20.10+
- Docker Compose 2.0+
- 최소 2GB RAM
- 최소 5GB 디스크 공간

## 📚 추가 정보

### 지원되는 환경

- 개발 (Development)
- 테스트 (Testing)
- 프로덕션 (Production)

### 주요 컴포넌트

| 컴포넌트 | 버전 | 용도 |
|---------|------|------|
| Python | 3.11 | 런타임 |
| Flask | 3.0 | 웹 프레임워크 |
| PostgreSQL | 15 | 데이터베이스 |
| Redis | 7 | 캐시 |
| Nginx | Alpine | 리버스 프록시 |
| Gunicorn | 21.2 | WSGI 서버 |

## 🤝 기여하기

기여는 언제나 환영합니다! 이슈를 열거나 풀 리퀘스트를 보내주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.
