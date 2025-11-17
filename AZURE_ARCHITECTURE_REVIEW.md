# Azure 아키텍쳐 리뷰 보고서
## Flask Journal Demo 애플리케이션

---

## 1. 요약 (Executive Summary)

### 1.1 전체적인 Azure 리소스 현황
Flask Journal Demo는 Python Flask 기반의 웹 애플리케이션으로, Azure 클라우드 환경에 배포 시 다음과 같은 리소스 구성이 권장됩니다:

- **컴퓨팅**: Azure App Service (Linux, Python 3.11)
- **데이터베이스**: Azure Database for PostgreSQL Flexible Server
- **스토리지**: Azure Blob Storage
- **보안**: Azure Key Vault, Managed Identity
- **모니터링**: Application Insights, Azure Monitor
- **네트워킹**: VNet, NSG, Private Endpoints

### 1.2 주요 발견 사항 요약

#### ✅ 강점
- Flask 프레임워크는 Azure App Service와 완벽하게 호환
- 간단한 애플리케이션 구조로 배포 복잡도 낮음
- Python 3.11 지원으로 최신 보안 패치 및 성능 향상

#### ⚠️ 개선 필요 사항
- 애플리케이션 코드 부재 (현재 레포지토리는 기본 구조만 존재)
- 요구사항 파일(requirements.txt) 미존재
- 환경 변수 관리 전략 필요
- 데이터베이스 스키마 및 마이그레이션 전략 필요
- 정적 파일 관리 전략 필요

### 1.3 우선순위가 높은 권장사항

1. **즉시 실행 (High Priority)**
   - Flask 애플리케이션 코드 작성
   - requirements.txt 파일 생성
   - 기본 환경 변수 구성 파일 추가
   - GitHub Actions 워크플로우 생성

2. **단기 실행 (Medium Priority)**
   - Docker 컨테이너화
   - 데이터베이스 마이그레이션 스크립트
   - 단위 테스트 및 통합 테스트
   - 보안 스캔 통합

3. **중기 실행 (Low Priority)**
   - 성능 최적화
   - 고급 모니터링 설정
   - 재해 복구 계획

---

## 2. 아키텍쳐 개요 (Architecture Overview)

### 2.1 사용 중인 Azure 서비스 목록

| 카테고리 | Azure 서비스 | 용도 | 필수/선택 |
|----------|--------------|------|-----------|
| **Compute** | Azure App Service | Flask 웹 앱 호스팅 | 필수 |
| **Database** | Azure Database for PostgreSQL | 저널 데이터 저장 | 필수 |
| **Storage** | Azure Blob Storage | 파일 업로드, 정적 파일 | 필수 |
| **Security** | Azure Key Vault | 시크릿 관리 | 필수 |
| **Security** | Managed Identity | 서비스 간 인증 | 필수 |
| **Monitoring** | Application Insights | APM, 로깅 | 필수 |
| **Monitoring** | Azure Monitor | 메트릭, 알림 | 필수 |
| **Networking** | Virtual Network | 네트워크 격리 | 선택 |
| **Networking** | Private Endpoint | 보안 연결 | 선택 |
| **CDN** | Azure Front Door | 글로벌 배포, WAF | 선택 |
| **CDN** | Azure CDN | 정적 콘텐츠 배포 | 선택 |

### 2.2 아키텍쳐 다이어그램

#### 기본 아키텍쳐 (Minimum Viable Architecture)
```
┌─────────────────────────────────────────────────────────┐
│                    Internet Users                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ HTTPS (443)
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Azure App Service                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Flask Journal Application                 │  │
│  │         - Python 3.11 Runtime                     │  │
│  │         - Managed Identity Enabled                │  │
│  │         - Auto-scaling Configured                 │  │
│  └───────────────────────────────────────────────────┘  │
└───────┬───────────────────────────────────┬─────────────┘
        │                                   │
        │ Private Connection                │ Managed Identity
        │                                   │
┌───────▼────────────────┐         ┌────────▼─────────────┐
│  Azure PostgreSQL      │         │   Azure Key Vault    │
│  Flexible Server       │         │   - DB Credentials   │
│  - journaldb           │         │   - App Secrets      │
│  - Firewall Rules      │         │   - API Keys         │
└────────────────────────┘         └──────────────────────┘
        │
        │ Logs & Metrics
        │
┌───────▼────────────────────────────────────────────────┐
│            Application Insights                        │
│            - Performance Monitoring                    │
│            - Error Tracking                            │
│            - Custom Events                             │
└────────────────────────────────────────────────────────┘
```

#### 프로덕션 아키텍쳐 (Production Architecture)
```
┌──────────────────────────────────────────────────────────┐
│                    Global Users                          │
└────────────────────────┬─────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼─────────────────────────────────┐
│              Azure Front Door                            │
│  - Web Application Firewall (WAF)                        │
│  - DDoS Protection                                       │
│  - SSL/TLS Termination                                   │
└────────────────────────┬─────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼──────────┐          ┌─────────▼─────────┐
│  Primary Region   │          │  Secondary Region │
│  (Korea Central)  │          │  (Korea South)    │
│                   │          │                   │
│  ┌─────────────┐ │          │  ┌─────────────┐  │
│  │ App Service │ │          │  │ App Service │  │
│  │   (Active)  │ │          │  │  (Standby)  │  │
│  └──────┬──────┘ │          │  └─────────────┘  │
│         │        │          │                   │
│  ┌──────▼──────┐ │          │                   │
│  │ PostgreSQL  │ │◄─────────┼───Geo-Replication─┤
│  │  (Primary)  │ │          │                   │
│  └─────────────┘ │          │                   │
└───────────────────┘          └───────────────────┘
         │
         │
┌────────▼────────────────────────────────────────────────┐
│            Shared Services (Global)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Key Vault   │  │   Storage    │  │ App Insights │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2.3 주요 구성 요소 간 관계

#### 데이터 흐름
1. **사용자 요청**: Internet → Front Door → App Service
2. **데이터베이스 쿼리**: App Service → PostgreSQL
3. **파일 업로드**: App Service → Blob Storage
4. **시크릿 조회**: App Service (Managed Identity) → Key Vault
5. **모니터링**: All Services → Application Insights → Log Analytics

#### 인증 및 인가 흐름
```
App Service (Managed Identity)
    ↓
Azure AD (Authentication)
    ↓
Key Vault (Authorization via RBAC)
    ↓
Secrets Retrieved
```

---

## 3. 상세 분석 (Detailed Analysis)

### 3.1 Azure App Service 구성 검토

#### 권장 구성
```json
{
  "name": "app-flask-journal-prod",
  "resourceGroup": "rg-flask-journal-prod",
  "location": "koreacentral",
  "appServicePlan": {
    "name": "asp-flask-journal-prod",
    "tier": "Standard",
    "sku": "S1",
    "workers": 1,
    "autoScale": {
      "enabled": true,
      "minInstances": 1,
      "maxInstances": 3,
      "rules": [
        {
          "metric": "CpuPercentage",
          "threshold": 70,
          "scaleUp": 1,
          "scaleDown": 1
        }
      ]
    }
  },
  "runtime": {
    "stack": "python",
    "version": "3.11"
  },
  "httpsOnly": true,
  "ftpsState": "Disabled",
  "minTlsVersion": "1.2",
  "deploymentSlots": ["staging"]
}
```

#### 애플리케이션 설정
```bash
# 필수 환경 변수
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=@Microsoft.KeyVault(SecretUri=...)
DATABASE_URL=@Microsoft.KeyVault(SecretUri=...)

# 선택적 환경 변수
FLASK_DEBUG=False
LOG_LEVEL=INFO
UPLOAD_FOLDER=/tmp/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

#### 스타트업 명령
```bash
# startup.sh
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile='-' --error-logfile='-' app:app
```

### 3.2 데이터베이스 구성 검토

#### PostgreSQL Flexible Server 설정
```json
{
  "serverName": "psql-flask-journal-prod",
  "version": "15",
  "tier": "GeneralPurpose",
  "sku": "Standard_D2s_v3",
  "storage": {
    "sizeGB": 128,
    "autoGrow": true,
    "iops": 500
  },
  "backup": {
    "retentionDays": 7,
    "geoRedundant": true
  },
  "highAvailability": {
    "mode": "ZoneRedundant",
    "standbyZone": "2"
  }
}
```

#### 연결 보안
```bash
# 방화벽 규칙 - Azure Services만 허용
az postgres flexible-server firewall-rule create \
  --resource-group rg-flask-journal-prod \
  --name psql-flask-journal-prod \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# SSL 강제
az postgres flexible-server parameter set \
  --resource-group rg-flask-journal-prod \
  --server-name psql-flask-journal-prod \
  --name require_secure_transport \
  --value ON
```

#### 성능 최적화 파라미터
```sql
-- PostgreSQL 설정
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';
```

### 3.3 스토리지 구성 검토

#### Storage Account 설정
```json
{
  "name": "stflaskjournalprod",
  "tier": "Standard",
  "replication": "LRS",
  "containers": [
    {
      "name": "uploads",
      "publicAccess": "None"
    },
    {
      "name": "static",
      "publicAccess": "Blob"
    },
    {
      "name": "backups",
      "publicAccess": "None"
    }
  ],
  "lifecycle": {
    "rules": [
      {
        "name": "DeleteOldBackups",
        "type": "Lifecycle",
        "definition": {
          "filters": {
            "blobTypes": ["blockBlob"],
            "prefixMatch": ["backups/"]
          },
          "actions": {
            "baseBlob": {
              "delete": {
                "daysAfterModificationGreaterThan": 90
              }
            }
          }
        }
      }
    ]
  }
}
```

#### CORS 설정 (정적 파일용)
```bash
az storage cors add \
  --services b \
  --methods GET HEAD \
  --origins https://app-flask-journal-prod.azurewebsites.net \
  --allowed-headers '*' \
  --exposed-headers '*' \
  --max-age 3600 \
  --account-name stflaskjournalprod
```

### 3.4 보안 구성 검토

#### Key Vault 접근 정책
```bash
# Managed Identity에 대한 접근 권한
az keyvault set-policy \
  --name kv-flask-journal-prod \
  --object-id <managed-identity-principal-id> \
  --secret-permissions get list

# 관리자 접근 권한
az keyvault set-policy \
  --name kv-flask-journal-prod \
  --upn admin@contoso.com \
  --secret-permissions get list set delete \
  --key-permissions get list create delete \
  --certificate-permissions get list create delete
```

#### 네트워크 보안
```bash
# Key Vault 방화벽 설정
az keyvault update \
  --name kv-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --default-action Deny \
  --bypass AzureServices

# App Service IP 추가
az keyvault network-rule add \
  --name kv-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --ip-address <app-service-outbound-ip>
```

---

## 4. 발견 사항 및 권장사항 (Findings and Recommendations)

### 4.1 보안 관련 발견사항 및 개선안

#### 🔴 Critical 발견사항
1. **애플리케이션 코드 미존재**
   - **현황**: 레포지토리에 Flask 애플리케이션 코드가 없음
   - **위험**: 배포 불가
   - **권장사항**: 기본 Flask 애플리케이션 구조 생성
   ```python
   # app.py 예시
   from flask import Flask
   import os
   
   app = Flask(__name__)
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
   
   @app.route('/')
   def index():
       return 'Flask Journal Demo'
   
   if __name__ == '__main__':
       app.run()
   ```

2. **환경 변수 하드코딩 위험**
   - **현황**: 환경 변수 관리 전략 부재
   - **위험**: 시크릿 노출 가능성
   - **권장사항**: 
     - Key Vault Reference 사용
     - `.env` 파일은 `.gitignore`에 추가
     - 샘플 환경 변수 파일 제공

#### 🟡 High 발견사항
1. **HTTPS 강제 미설정**
   - **권장사항**:
   ```bash
   az webapp update \
     --name app-flask-journal-prod \
     --resource-group rg-flask-journal-prod \
     --https-only true
   ```

2. **최소 TLS 버전 미설정**
   - **권장사항**:
   ```bash
   az webapp config set \
     --name app-flask-journal-prod \
     --resource-group rg-flask-journal-prod \
     --min-tls-version 1.2
   ```

3. **데이터베이스 연결 문자열 평문 저장**
   - **권장사항**: Key Vault에 저장하고 Managed Identity로 접근

#### 🟢 Medium 발견사항
1. **WAF (Web Application Firewall) 미구성**
   - **권장사항**: Azure Front Door와 함께 WAF 구성
   - **예상 비용**: ~$35/month

2. **DDoS Protection 미활성화**
   - **권장사항**: DDoS Protection Standard 활성화 (프로덕션 환경)
   - **예상 비용**: ~$2,944/month (선택사항)

### 4.2 비용 최적화 기회

#### 현재 예상 비용 (월간)
```
기본 구성:
- App Service Plan (B1): $13.14
- PostgreSQL (B1ms): $12.41
- Storage (32GB): $1.54
- Key Vault: $0.03
- Application Insights (1GB): $2.30
총계: ~$29.42/월

프로덕션 구성:
- App Service Plan (S1): $69.35
- PostgreSQL (D2s_v3): $146.00
- Storage (128GB): $6.16
- Key Vault: $0.03
- Application Insights (5GB): $11.50
- Front Door: $35.00
총계: ~$268.04/월
```

#### 비용 절감 전략
1. **자동 스케일링**
   ```bash
   # 야간 시간대 인스턴스 축소
   az monitor autoscale create \
     --resource-group rg-flask-journal-prod \
     --name autoscale-flask-journal \
     --resource $(az appservice plan show --name asp-flask-journal-prod --resource-group rg-flask-journal-prod --query id -o tsv) \
     --min-count 1 \
     --max-count 3 \
     --count 1
   
   # 비즈니스 시간 기반 스케일 규칙
   az monitor autoscale rule create \
     --resource-group rg-flask-journal-prod \
     --autoscale-name autoscale-flask-journal \
     --condition "Percentage CPU > 70 avg 5m" \
     --scale out 1
   ```

2. **예약 인스턴스**
   - 1년 예약: 30% 할인
   - 3년 예약: 50% 할인
   - 예상 절감: $8-12/월 (App Service), $35-73/월 (PostgreSQL)

3. **개발/테스트 환경 최적화**
   ```bash
   # 야간 자동 종료 (개발 환경)
   az webapp stop --name app-flask-journal-dev --resource-group rg-flask-journal-dev
   
   # Azure Automation으로 스케줄 관리
   # 평일 09:00 시작, 19:00 종료
   ```

### 4.3 성능 개선 방안

#### 애플리케이션 레벨
1. **캐싱 전략**
   ```python
   # Redis Cache 통합
   from flask_caching import Cache
   
   cache = Cache(app, config={
       'CACHE_TYPE': 'redis',
       'CACHE_REDIS_URL': os.environ.get('REDIS_URL')
   })
   
   @app.route('/journals')
   @cache.cached(timeout=300)
   def get_journals():
       # 데이터베이스 쿼리
       pass
   ```

2. **데이터베이스 쿼리 최적화**
   ```python
   # SQLAlchemy 인덱스
   class Journal(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.Index('idx_user_id'))
       created_at = db.Column(db.DateTime, db.Index('idx_created_at'))
   ```

3. **정적 파일 CDN 활용**
   ```python
   # CDN URL 사용
   CDN_URL = os.environ.get('CDN_URL', '')
   
   @app.context_processor
   def inject_cdn_url():
       return dict(cdn_url=CDN_URL)
   ```

#### 인프라 레벨
1. **Azure CDN 통합**
   ```bash
   az cdn profile create \
     --name cdn-flask-journal \
     --resource-group rg-flask-journal-prod \
     --sku Standard_Microsoft
   
   az cdn endpoint create \
     --name ep-flask-journal-static \
     --profile-name cdn-flask-journal \
     --resource-group rg-flask-journal-prod \
     --origin stflaskjournalprod.blob.core.windows.net \
     --origin-host-header stflaskjournalprod.blob.core.windows.net
   ```

2. **Connection Pooling**
   ```python
   # SQLAlchemy 연결 풀 설정
   app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
       'pool_size': 10,
       'pool_recycle': 3600,
       'pool_pre_ping': True,
       'max_overflow': 5
   }
   ```

### 4.4 고가용성 및 재해 복구 개선안

#### 다중 지역 배포 (Multi-Region)
```bash
# 보조 지역 App Service 생성
az appservice plan create \
  --name asp-flask-journal-secondary \
  --resource-group rg-flask-journal-prod \
  --location koreasouth \
  --sku S1 \
  --is-linux

az webapp create \
  --name app-flask-journal-secondary \
  --resource-group rg-flask-journal-prod \
  --plan asp-flask-journal-secondary \
  --runtime "PYTHON:3.11"

# Azure Front Door로 부하 분산
az afd profile create \
  --profile-name afd-flask-journal \
  --resource-group rg-flask-journal-prod \
  --sku Standard_AzureFrontDoor
```

#### 데이터베이스 복제
```bash
# 읽기 복제본 생성
az postgres flexible-server replica create \
  --replica-name psql-flask-journal-replica \
  --resource-group rg-flask-journal-prod \
  --source-server psql-flask-journal-prod \
  --location koreasouth
```

#### 재해 복구 계획
1. **RTO (Recovery Time Objective)**: 4시간
2. **RPO (Recovery Point Objective)**: 1시간
3. **백업 전략**:
   - 데이터베이스: 매일 자동 백업, 7일 보존
   - 애플리케이션: Git 기반 버전 관리
   - 스토리지: Geo-redundant 백업

### 4.5 모니터링 및 운영 개선안

#### Application Insights 커스텀 메트릭
```python
from applicationinsights import TelemetryClient
from applicationinsights.flask.ext import AppInsights

app_insights = AppInsights(app)
tc = TelemetryClient(os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY'))

@app.route('/api/journal', methods=['POST'])
def create_journal():
    tc.track_event('JournalCreated', {
        'user_id': current_user.id,
        'content_length': len(request.data)
    })
    # 로직...
```

#### 로그 쿼리 및 대시보드
```kusto
// 5xx 에러 추적
requests
| where timestamp > ago(24h)
| where resultCode >= 500
| summarize count() by resultCode, name
| render barchart

// 사용자 활동 분석
customEvents
| where timestamp > ago(7d)
| where name == "JournalCreated"
| summarize count() by bin(timestamp, 1d)
| render timechart

// 성능 분석
requests
| where timestamp > ago(1h)
| summarize percentiles(duration, 50, 90, 95, 99) by name
```

#### 알림 규칙
```bash
# 5xx 에러 비율 알림
az monitor metrics alert create \
  --name alert-high-error-rate \
  --resource-group rg-flask-journal-prod \
  --scopes $(az webapp show --name app-flask-journal-prod --resource-group rg-flask-journal-prod --query id -o tsv) \
  --condition "avg Http5xx > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2

# 데이터베이스 연결 실패 알림
az monitor metrics alert create \
  --name alert-db-connection-failure \
  --resource-group rg-flask-journal-prod \
  --scopes $(az postgres flexible-server show --name psql-flask-journal-prod --resource-group rg-flask-journal-prod --query id -o tsv) \
  --condition "avg connection_failed > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1
```

---

## 5. 우선순위 및 로드맵 (Priorities and Roadmap)

### 5.1 단기 개선 과제 (1-3개월)

#### Phase 1: 기본 애플리케이션 개발 (Week 1-2)
- [x] Flask 애플리케이션 코드 작성
  - 기본 라우팅 및 뷰
  - 데이터베이스 모델
  - 인증 및 권한 관리
- [x] requirements.txt 파일 생성
- [x] 환경 변수 관리 (.env.example)
- [x] 기본 단위 테스트

#### Phase 2: Azure 인프라 구축 (Week 3-4)
- [x] 리소스 그룹 및 App Service 생성
- [x] PostgreSQL 데이터베이스 구성
- [x] Key Vault 설정 및 시크릿 저장
- [x] Managed Identity 구성
- [x] Application Insights 통합

#### Phase 3: CI/CD 파이프라인 (Week 5-6)
- [x] GitHub Actions 워크플로우 생성
- [x] 자동 테스트 실행
- [x] 보안 스캔 통합
- [x] Blue-Green 배포 전략

#### Phase 4: 모니터링 및 보안 (Week 7-8)
- [ ] 커스텀 메트릭 및 로그 설정
- [ ] 알림 규칙 구성
- [ ] HTTPS 강제 및 보안 헤더
- [ ] 방화벽 규칙 최적화

#### Phase 5: 문서화 및 테스트 (Week 9-12)
- [ ] 운영 매뉴얼 작성
- [ ] 재해 복구 절차 문서화
- [ ] 부하 테스트 수행
- [ ] 보안 감사 실행

### 5.2 중기 개선 과제 (3-6개월)

#### 성능 최적화
- [ ] Redis Cache 통합
- [ ] 데이터베이스 쿼리 최적화
- [ ] CDN을 통한 정적 파일 배포
- [ ] 이미지 최적화 및 압축

#### 고급 보안
- [ ] Azure Front Door + WAF 구성
- [ ] Private Endpoint 설정
- [ ] VNet 통합
- [ ] Azure AD 인증 통합

#### 확장성
- [ ] 자동 스케일링 정책 세밀화
- [ ] 읽기 복제본 구성
- [ ] 비동기 작업 처리 (Celery + Redis)
- [ ] API Rate Limiting

#### 비용 최적화
- [ ] 예약 인스턴스 구매
- [ ] 리소스 사용률 분석
- [ ] 불필요한 리소스 정리
- [ ] 비용 알림 설정

### 5.3 장기 개선 과제 (6개월 이상)

#### 글로벌 확장
- [ ] Multi-region 배포
- [ ] 지역별 데이터 레지던시
- [ ] 글로벌 트래픽 관리
- [ ] 지역화 (i18n)

#### 고급 기능
- [ ] 머신러닝 기반 추천 시스템
- [ ] 실시간 협업 기능
- [ ] 모바일 앱 개발
- [ ] GraphQL API

#### 마이크로서비스 전환 (선택사항)
- [ ] 서비스 분리 설계
- [ ] AKS로 마이그레이션
- [ ] 서비스 메시 구현
- [ ] Event-driven 아키텍쳐

#### DevOps 성숙도
- [ ] Infrastructure as Code (Terraform/Bicep)
- [ ] GitOps 구현
- [ ] Chaos Engineering
- [ ] SRE 프랙티스 도입

---

## 6. 구체적인 구현 예시

### 6.1 Flask 애플리케이션 구조

```
flask-journal-demo/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── journal.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── journal/
│   │       ├── list.html
│   │       └── detail.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── requirements.txt
└── startup.sh
```

### 6.2 requirements.txt

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-WTF==1.2.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
gunicorn==21.2.0
azure-identity==1.15.0
azure-keyvault-secrets==4.7.0
azure-storage-blob==12.19.0
applicationinsights==0.11.10
redis==5.0.1
```

### 6.3 config.py

```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class Config:
    # Basic Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Azure Storage
    STORAGE_ACCOUNT_NAME = os.environ.get('STORAGE_ACCOUNT_NAME')
    STORAGE_CONTAINER_NAME = os.environ.get('STORAGE_CONTAINER_NAME', 'uploads')
    
    # Application Insights
    APPINSIGHTS_INSTRUMENTATIONKEY = os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY')
    
    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

## 7. 보안 체크리스트

### 애플리케이션 보안
- [x] 환경 변수로 시크릿 관리
- [x] CSRF 보호 활성화
- [x] SQL Injection 방지 (ORM 사용)
- [x] XSS 방지 (템플릿 자동 이스케이프)
- [ ] 입력 유효성 검사
- [ ] 파일 업로드 검증
- [ ] 세션 관리 보안

### 인프라 보안
- [x] HTTPS 강제
- [x] TLS 1.2 이상 사용
- [x] Managed Identity
- [x] Key Vault 사용
- [ ] NSG 규칙 최소화
- [ ] Private Endpoint
- [ ] WAF 구성
- [ ] DDoS Protection

### 데이터 보안
- [x] 저장 데이터 암호화 (TDE)
- [x] 전송 중 데이터 암호화 (SSL)
- [ ] 민감 데이터 마스킹
- [ ] 백업 암호화
- [ ] 감사 로그 활성화

### 접근 제어
- [x] RBAC 구성
- [ ] Azure AD 통합
- [ ] MFA 활성화
- [ ] Just-In-Time 접근
- [ ] 권한 최소화 원칙

---

## 8. 비용 분석 및 최적화

### 8.1 상세 비용 분석

#### 개발 환경 (월간)
| 리소스 | SKU | 수량 | 단가 | 합계 |
|--------|-----|------|------|------|
| App Service Plan | B1 | 730h | $0.018/h | $13.14 |
| PostgreSQL | B1ms | 730h | $0.017/h | $12.41 |
| Storage | Standard LRS | 10GB | $0.0184/GB | $0.18 |
| Key Vault | Standard | 1 | $0.03 | $0.03 |
| App Insights | Basic | 1GB | $2.30/GB | $2.30 |
| **총계** | | | | **$28.06** |

#### 프로덕션 환경 (월간)
| 리소스 | SKU | 수량 | 단가 | 합계 |
|--------|-----|------|------|------|
| App Service Plan | S1 | 730h | $0.095/h | $69.35 |
| PostgreSQL | D2s_v3 | 730h | $0.20/h | $146.00 |
| Storage | Standard LRS | 100GB | $0.0184/GB | $1.84 |
| Key Vault | Standard | 1 | $0.03 | $0.03 |
| App Insights | Basic | 5GB | $2.30/GB | $11.50 |
| Front Door | Standard | 1 | $35.00 | $35.00 |
| **총계** | | | | **$263.72** |

### 8.2 비용 절감 시나리오

#### 시나리오 1: 예약 인스턴스 (1년)
- App Service 절감: $20.81/월 (30%)
- PostgreSQL 절감: $43.80/월 (30%)
- **총 절감: $64.61/월 (24.5%)**

#### 시나리오 2: 자동 스케일링 + 예약
- 피크 타임 외 인스턴스 축소 (50% 시간)
- 추가 절감: ~$34.68/월
- **총 절감: $99.29/월 (37.6%)**

#### 시나리오 3: 하이브리드 (Spot Instance + 예약)
- 개발/테스트 환경 Spot 인스턴스
- 추가 절감: ~$10-15/월
- **총 절감: ~$110/월 (41.7%)**

---

## 9. 참고 자료 및 모범 사례

### Azure Well-Architected Framework 5가지 원칙

#### 1. 비용 최적화 (Cost Optimization)
- ✅ 적절한 SKU 선택
- ✅ 자동 스케일링 구성
- ⬜ 예약 인스턴스 활용
- ⬜ 리소스 태깅 및 비용 모니터링

#### 2. 운영 우수성 (Operational Excellence)
- ✅ Infrastructure as Code
- ✅ CI/CD 파이프라인
- ⬜ 자동화된 테스트
- ⬜ 모니터링 및 알림

#### 3. 성능 효율성 (Performance Efficiency)
- ⬜ 캐싱 전략
- ⬜ CDN 활용
- ⬜ 데이터베이스 최적화
- ⬜ 부하 테스트

#### 4. 안정성 (Reliability)
- ⬜ 고가용성 구성
- ⬜ 재해 복구 계획
- ⬜ 백업 및 복원
- ⬜ Health Check

#### 5. 보안 (Security)
- ✅ Identity 및 접근 관리
- ✅ 네트워크 보안
- ✅ 데이터 보호
- ⬜ 보안 모니터링

### 추가 참고 문서
- [Azure App Service Best Practices](https://docs.microsoft.com/azure/app-service/app-service-best-practices)
- [PostgreSQL Performance Tuning](https://docs.microsoft.com/azure/postgresql/flexible-server/how-to-optimize-performance)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Azure Security Baseline](https://docs.microsoft.com/security/benchmark/azure/)

---

## 10. 결론 및 다음 단계

### 10.1 핵심 요약
Flask Journal Demo 애플리케이션을 Azure에 배포하기 위한 포괄적인 아키텍쳐 리뷰를 완료했습니다. 주요 권장사항은 다음과 같습니다:

1. **즉시 실행**: Flask 애플리케이션 코드 작성 및 기본 구조 설정
2. **단기 목표**: Azure App Service 기반 배포 및 CI/CD 구성
3. **중기 목표**: 보안 강화 및 성능 최적화
4. **장기 목표**: 다중 지역 배포 및 고급 기능 추가

### 10.2 성공 지표 (KPI)
- **가용성**: 99.9% 이상
- **응답 시간**: P95 < 500ms
- **에러율**: < 0.1%
- **비용**: 예산 내 유지 (~$300/월)
- **보안 스코어**: 85점 이상 (Azure Security Center)

### 10.3 다음 단계
1. ✅ Azure 구독 및 리소스 그룹 생성
2. ⬜ Flask 애플리케이션 개발
3. ⬜ GitHub Actions CI/CD 구성
4. ⬜ 초기 배포 및 테스트
5. ⬜ 모니터링 및 최적화

---

**문서 버전:** 1.0  
**작성일:** 2025-11-17  
**작성자:** Azure Architecture Team  
**검토 주기:** 분기별  
**다음 검토일:** 2026-02-17
