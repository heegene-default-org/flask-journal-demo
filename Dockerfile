# 멀티스테이지 빌드를 사용한 Flask 일기장 애플리케이션 Dockerfile

# ================================
# 빌드 스테이지
# ================================
FROM python:3.11-slim as builder

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ================================
# 프로덕션 스테이지
# ================================
FROM python:3.11-slim

# 메타데이터 레이블
LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="Flask Journal Application"

# 보안: non-root 사용자 생성
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# 런타임 종속성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 Python 패키지 복사
COPY --from=builder /root/.local /home/appuser/.local

# 환경 변수 설정
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=run.py

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 사용자 전환
USER appuser

# 포트 노출
EXPOSE 5000

# 헬스체크 (애플리케이션이 /health 엔드포인트를 제공한다고 가정)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 애플리케이션 실행 (Gunicorn 사용)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
