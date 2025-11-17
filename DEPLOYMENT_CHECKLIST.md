# Azure 배포 체크리스트
## Flask Journal Demo

이 체크리스트는 Azure 배포의 모든 단계를 추적하는 데 사용됩니다.

---

## 📋 배포 전 준비사항

### 계정 및 권한
- [ ] Azure 구독 계정 보유
- [ ] 적절한 권한 확보 (Contributor 이상)
- [ ] Azure CLI 설치 및 구성
- [ ] Git 설치
- [ ] Python 3.11+ 설치 (로컬 개발용)

### 환경 설정
- [ ] 리소스 네이밍 규칙 결정
- [ ] 배포 리전 선택 (권장: Korea Central)
- [ ] 비용 예산 승인
- [ ] 보안 정책 검토

---

## 🏗️ 인프라 배포 (Phase 1)

### 리소스 그룹
- [ ] 리소스 그룹 생성
  ```bash
  az group create --name rg-flask-journal-prod --location koreacentral
  ```
- [ ] 태그 설정 (Environment, Application, CostCenter)

### Compute 리소스
- [ ] App Service Plan 생성 (SKU: B1 또는 S1)
- [ ] Web App 생성 (Python 3.11)
- [ ] HTTPS 강제 활성화
- [ ] 최소 TLS 버전 1.2 설정
- [ ] System-Assigned Managed Identity 활성화

### 데이터베이스
- [ ] PostgreSQL Flexible Server 생성
- [ ] 관리자 비밀번호 생성 및 안전하게 저장
- [ ] 데이터베이스 생성 (journaldb)
- [ ] 방화벽 규칙 설정 (Azure Services 허용)
- [ ] SSL 연결 강제
- [ ] 백업 설정 (7일 보존)

### 스토리지
- [ ] Storage Account 생성
- [ ] Blob 컨테이너 생성
  - [ ] uploads (Private)
  - [ ] static (Private)
  - [ ] backups (Private)
- [ ] 최소 TLS 버전 1.2 설정
- [ ] 공개 액세스 비활성화

### 보안
- [ ] Key Vault 생성
- [ ] Managed Identity에 Key Vault 접근 권한 부여
- [ ] 시크릿 저장
  - [ ] FlaskSecretKey
  - [ ] DatabaseConnectionString
  - [ ] (필요시) 추가 API 키
- [ ] Soft Delete 활성화
- [ ] 접근 정책 최소화

### 모니터링
- [ ] Log Analytics Workspace 생성
- [ ] Application Insights 생성
- [ ] Web App에 Application Insights 연결
- [ ] 커스텀 메트릭 설정

---

## 💻 애플리케이션 배포 (Phase 2)

### 코드 준비
- [ ] requirements.txt 확인
- [ ] .env.example 검토
- [ ] app.py 구성 확인
- [ ] startup.sh 실행 권한 설정

### 환경 변수 설정
- [ ] FLASK_APP 설정
- [ ] FLASK_ENV=production 설정
- [ ] SECRET_KEY (Key Vault Reference)
- [ ] DATABASE_URL (Key Vault Reference)
- [ ] STORAGE_ACCOUNT_NAME 설정
- [ ] APPINSIGHTS_INSTRUMENTATIONKEY 설정

### 배포 실행
- [ ] 로컬 테스트 완료
- [ ] Azure Web App에 배포
  - [ ] ZIP 배포 또는
  - [ ] GitHub Actions 또는
  - [ ] Azure DevOps
- [ ] 배포 성공 확인
- [ ] 애플리케이션 URL 접속 테스트

### 데이터베이스 초기화
- [ ] 마이그레이션 스크립트 실행
- [ ] 초기 데이터 로드 (필요시)
- [ ] 연결 테스트

---

## 🔧 배포 후 구성 (Phase 3)

### 성능 최적화
- [ ] 자동 스케일링 규칙 설정
- [ ] 연결 풀 구성
- [ ] 캐싱 전략 구현 (선택)
- [ ] CDN 설정 (선택)

### 보안 강화
- [ ] 네트워크 보안 그룹 (NSG) 구성
- [ ] IP 제한 설정 (필요시)
- [ ] WAF 구성 (프로덕션)
- [ ] 정기 보안 스캔 일정 설정

### 백업 및 복구
- [ ] 데이터베이스 자동 백업 확인
- [ ] Web App 백업 구성
- [ ] 복구 테스트 수행
- [ ] 재해 복구 계획 문서화

### 모니터링 및 알림
- [ ] 알림 규칙 생성
  - [ ] CPU 사용률 > 80%
  - [ ] 메모리 사용률 > 80%
  - [ ] HTTP 5xx 오류 발생
  - [ ] 응답 시간 > 3초
- [ ] 로그 쿼리 템플릿 생성
- [ ] 대시보드 구성
- [ ] 알림 수신자 설정

---

## 🚀 CI/CD 설정 (Phase 4)

### GitHub Actions
- [ ] Azure 서비스 주체 생성
- [ ] GitHub Secrets 설정
  - [ ] AZURE_CREDENTIALS
  - [ ] (필요시) 추가 시크릿
- [ ] 워크플로우 파일 생성
- [ ] 빌드 단계 구성
- [ ] 테스트 단계 구성
- [ ] 배포 단계 구성
- [ ] 첫 번째 자동 배포 테스트

### 배포 슬롯 (프로덕션)
- [ ] 스테이징 슬롯 생성
- [ ] 슬롯 별 환경 변수 구성
- [ ] 배포 후 스왑 테스트
- [ ] 자동 스왑 규칙 설정

---

## 🧪 테스트 및 검증

### 기능 테스트
- [ ] 메인 페이지 로드 확인
- [ ] Health Check 엔드포인트 확인 (/health)
- [ ] 데이터베이스 연결 확인
- [ ] 파일 업로드 테스트 (구현시)
- [ ] 사용자 인증 테스트 (구현시)

### 성능 테스트
- [ ] 부하 테스트 수행
- [ ] 응답 시간 측정
- [ ] 동시 사용자 처리 확인
- [ ] 자동 스케일링 동작 확인

### 보안 테스트
- [ ] HTTPS 강제 확인
- [ ] TLS 버전 확인
- [ ] 시크릿 노출 검사
- [ ] SQL Injection 테스트
- [ ] XSS 테스트
- [ ] CSRF 보호 확인

---

## 📊 운영 준비

### 문서화
- [ ] 운영 매뉴얼 작성
- [ ] 트러블슈팅 가이드 작성
- [ ] 에스컬레이션 프로세스 정의
- [ ] 연락처 정보 업데이트

### 모니터링 설정
- [ ] 일일 헬스 체크 일정 설정
- [ ] 주간 성능 리포트 자동화
- [ ] 월간 비용 리뷰 일정 설정
- [ ] 로그 보존 정책 구성

### 팀 교육
- [ ] 운영팀 교육 완료
- [ ] 개발팀 배포 프로세스 숙지
- [ ] 긴급 대응 절차 공유
- [ ] Azure Portal 접근 권한 부여

---

## 💰 비용 관리

### 비용 모니터링
- [ ] 비용 알림 설정
- [ ] 예산 설정 ($50, $100, $200 임계값)
- [ ] 리소스 태깅 완료
- [ ] 월간 비용 리뷰 일정

### 최적화
- [ ] 미사용 리소스 식별
- [ ] 예약 인스턴스 검토
- [ ] 자동 스케일다운 설정
- [ ] 스토리지 계층화 정책

---

## 🔄 지속적 개선

### 단기 (1-3개월)
- [ ] 성능 메트릭 기준선 설정
- [ ] 사용자 피드백 수집
- [ ] 보안 취약점 스캔
- [ ] 비용 최적화 구현

### 중기 (3-6개월)
- [ ] VNet 통합 검토
- [ ] Private Endpoint 구성
- [ ] Redis Cache 추가
- [ ] 다중 지역 배포 계획

### 장기 (6개월+)
- [ ] 마이크로서비스 아키텍쳐 검토
- [ ] AKS 마이그레이션 평가
- [ ] 고급 AI/ML 기능 추가
- [ ] 글로벌 확장 전략

---

## ✅ 배포 완료 확인

최종 체크리스트:
- [ ] 모든 리소스가 정상 작동
- [ ] 모니터링 및 알림 활성화
- [ ] 백업 구성 완료
- [ ] 보안 검토 통과
- [ ] 문서화 완료
- [ ] 팀 교육 완료
- [ ] 비용 모니터링 활성화
- [ ] 운영 준비 완료

---

## 📝 서명

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| 프로젝트 관리자 | | | |
| 개발 팀장 | | | |
| 인프라 엔지니어 | | | |
| 보안 담당자 | | | |
| 운영 팀장 | | | |

---

**체크리스트 버전**: 1.0  
**마지막 업데이트**: 2025-11-17  
**다음 검토일**: [배포 후 1개월]
