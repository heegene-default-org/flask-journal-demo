#!/bin/bash

# 로컬 개발 환경 설정 스크립트
# Flask Journal Demo

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Flask Journal Demo - 로컬 개발 환경 설정${NC}"
echo ""

# Python 버전 확인
echo "Python 버전 확인 중..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo -e "${YELLOW}경고: Python $REQUIRED_VERSION 이상이 권장됩니다. 현재: $PYTHON_VERSION${NC}"
fi

# 가상 환경 생성
if [ ! -d "venv" ]; then
    echo "가상 환경 생성 중..."
    python3 -m venv venv
    echo -e "${GREEN}✓ 가상 환경 생성 완료${NC}"
else
    echo "가상 환경이 이미 존재합니다."
fi

# 가상 환경 활성화
echo "가상 환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "pip 업그레이드 중..."
pip install --upgrade pip > /dev/null

# 의존성 설치
echo "의존성 설치 중..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 의존성 설치 완료${NC}"
else
    echo -e "${YELLOW}경고: requirements.txt를 찾을 수 없습니다.${NC}"
fi

# 환경 변수 파일 생성
if [ ! -f ".env" ]; then
    echo ".env 파일 생성 중..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env 파일이 .env.example에서 생성되었습니다.${NC}"
        echo -e "${YELLOW}주의: .env 파일을 편집하여 필요한 값을 설정하세요!${NC}"
    else
        echo "FLASK_APP=app.py" > .env
        echo "FLASK_ENV=development" >> .env
        echo "FLASK_DEBUG=True" >> .env
        echo "SECRET_KEY=dev-secret-key-change-this" >> .env
        echo -e "${GREEN}✓ 기본 .env 파일이 생성되었습니다.${NC}"
    fi
else
    echo ".env 파일이 이미 존재합니다."
fi

# 개발 도구 설치 (선택사항)
echo ""
read -p "개발 도구를 설치하시겠습니까? (pytest, flake8, black) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "개발 도구 설치 중..."
    pip install pytest pytest-cov flake8 black bandit safety
    echo -e "${GREEN}✓ 개발 도구 설치 완료${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}로컬 개발 환경 설정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "다음 명령어로 애플리케이션을 실행하세요:"
echo ""
echo "  source venv/bin/activate  # 가상 환경 활성화"
echo "  python app.py             # 애플리케이션 실행"
echo ""
echo "또는:"
echo ""
echo "  flask run                 # Flask 개발 서버 실행"
echo ""
echo "브라우저에서 http://localhost:5000 을 열어 확인하세요."
echo ""
