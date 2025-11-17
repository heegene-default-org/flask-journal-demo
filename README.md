# Flask Journal Demo

Python Flask 기반 저널 애플리케이션 데모 프로젝트

## 📖 개요

Flask Journal Demo는 Azure 클라우드 환경에 배포 가능한 웹 기반 저널 애플리케이션입니다. 
이 프로젝트는 Azure의 다양한 서비스를 활용하여 확장 가능하고 안전한 애플리케이션 배포 방법을 제시합니다.

## 🚀 빠른 시작

### 로컬 개발

```bash
# 레포지토리 클론
git clone https://github.com/heegene-default-org/flask-journal-demo.git
cd flask-journal-demo

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 입력

# 애플리케이션 실행
python app.py
```

브라우저에서 `http://localhost:5000` 접속

### Azure 배포

상세한 배포 가이드는 [Azure 빠른 시작 가이드](./AZURE_QUICKSTART.md)를 참조하세요.

```bash
# Azure CLI 로그인
az login

# 인프라 배포
chmod +x deploy-azure-infrastructure.sh
./deploy-azure-infrastructure.sh

# 애플리케이션 배포는 GitHub Actions를 통해 자동화
```

## 📚 문서

### Azure 배포 관련 문서

- **[Azure 배포 구현 계획서](./AZURE_DEPLOYMENT_PLAN.md)** - 종합적인 Azure 배포 전략 및 단계별 구현 가이드
  - 아키텍쳐 다이어그램 및 서비스 구성
  - 단계별 배포 절차 (CLI 명령어 포함)
  - CI/CD 파이프라인 구성
  - 네트워크 및 보안 설정
  - 백업 및 재해 복구 전략
  - 비용 최적화 방안

- **[Azure 아키텍쳐 리뷰 보고서](./AZURE_ARCHITECTURE_REVIEW.md)** - 포괄적인 아키텍쳐 분석 및 권장사항
  - Azure 리소스 현황 및 분석
  - Well-Architected Framework 기반 검토
  - 보안, 성능, 비용 최적화 권장사항
  - 우선순위별 개선 로드맵
  - 구체적인 구현 예시 및 코드

- **[Azure 빠른 시작 가이드](./AZURE_QUICKSTART.md)** - 5분 안에 Azure에 배포하기
  - 빠른 배포 명령어
  - 트러블슈팅 가이드
  - 모니터링 및 로그 확인
  - 비용 관리 팁

### 인프라 코드

- **[azure-infrastructure.bicep](./azure-infrastructure.bicep)** - Azure Bicep IaC 템플릿
- **[deploy-azure-infrastructure.sh](./deploy-azure-infrastructure.sh)** - Bash 배포 스크립트

## 🏗️ 아키텍쳐

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │
       │ HTTPS
       ▼
┌──────────────────┐
│ Azure Front Door │ (Optional)
│   + WAF          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Azure App       │
│  Service         │
│  (Python 3.11)   │
└───┬──────────┬───┘
    │          │
    │          └────────────┐
    │                       │
    ▼                       ▼
┌────────────┐     ┌────────────────┐
│ PostgreSQL │     │  Key Vault     │
│ Database   │     │  Blob Storage  │
└────────────┘     └────────────────┘
```

## 🔧 주요 기능

- ✅ Flask 웹 프레임워크
- ✅ Azure App Service 호스팅
- ✅ PostgreSQL 데이터베이스
- ✅ Azure Blob Storage 통합
- ✅ Key Vault 시크릿 관리
- ✅ Application Insights 모니터링
- ✅ Managed Identity 인증
- ✅ CI/CD (GitHub Actions)

## 💻 기술 스택

### 백엔드
- Python 3.11
- Flask 3.0
- SQLAlchemy
- Gunicorn

### Azure 서비스
- Azure App Service
- Azure Database for PostgreSQL
- Azure Blob Storage
- Azure Key Vault
- Application Insights
- Azure Monitor

### DevOps
- GitHub Actions
- Azure CLI
- Bicep (IaC)

## 📊 모니터링

Application Insights를 통한 실시간 모니터링:
- 애플리케이션 성능 메트릭
- 오류 추적 및 로깅
- 사용자 활동 분석
- 커스텀 이벤트 추적

자세한 내용은 [Azure 배포 계획서 - 모니터링 섹션](./AZURE_DEPLOYMENT_PLAN.md#7-모니터링-및-알림)을 참조하세요.

## 🔒 보안

- HTTPS 강제 적용
- TLS 1.2 이상 사용
- Azure Key Vault를 통한 시크릿 관리
- Managed Identity 기반 인증
- 데이터베이스 방화벽 규칙
- 정기적인 보안 스캔

보안 체크리스트는 [Azure 아키텍쳐 리뷰 보고서](./AZURE_ARCHITECTURE_REVIEW.md#7-보안-체크리스트)를 참조하세요.

## 💰 비용

예상 월간 비용:
- **개발 환경**: ~$28/월
- **프로덕션 환경**: ~$264/월

비용 최적화 방안은 [Azure 배포 계획서 - 비용 최적화](./AZURE_DEPLOYMENT_PLAN.md#8-비용-최적화-전략)를 참조하세요.

## 🤝 기여

기여는 언제나 환영합니다! 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 라이선스 파일을 참조하세요.

## 📞 지원

- GitHub Issues: [이슈 등록](https://github.com/heegene-default-org/flask-journal-demo/issues)
- Azure 지원: [Azure 지원 센터](https://azure.microsoft.com/support/)

## 🙏 참고 자료

- [Azure App Service 문서](https://docs.microsoft.com/azure/app-service/)
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)
- [Python on Azure 가이드](https://docs.microsoft.com/azure/developer/python/)

---

**버전**: 1.0  
**마지막 업데이트**: 2025-11-17
