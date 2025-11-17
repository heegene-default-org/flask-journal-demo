# Azure 배포 구현 계획서
## Flask Journal Demo 애플리케이션

---

## 1. 요약 (Executive Summary)

본 문서는 Flask Journal Demo 애플리케이션을 Azure 클라우드 환경에 배포하기 위한 종합적인 구현 계획을 제시합니다.

### 주요 목표
- Python Flask 기반 저널 애플리케이션의 Azure 배포
- 확장 가능하고 안전한 클라우드 인프라 구축
- 비용 효율적인 리소스 활용
- CI/CD 파이프라인을 통한 자동화된 배포
- 모니터링 및 운영 최적화

### 권장 배포 옵션
1. **Azure App Service** (Web Apps) - 권장 옵션
2. **Azure Container Instances** - 컨테이너화된 배포
3. **Azure Kubernetes Service (AKS)** - 대규모 엔터프라이즈 환경

---

## 2. 아키텍쳐 개요

### 2.1 기본 아키텍쳐 (Azure App Service)

```
┌─────────────────────────────────────────────────────────────┐
│                        Azure Cloud                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Azure Front Door (Optional)            │    │
│  │                  Global CDN & WAF                   │    │
│  └──────────────────────┬─────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────┐    │
│  │            Azure App Service Plan                   │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐   │    │
│  │  │     Flask Journal Web App                  │   │    │
│  │  │     (Python 3.11 Runtime)                  │   │    │
│  │  └────────────────────────────────────────────┘   │    │
│  └──────────────────────┬─────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────┐    │
│  │         Azure Database for PostgreSQL              │    │
│  │              (Flexible Server)                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Azure Storage Account                    │   │
│  │   - Blob Storage (정적 파일, 업로드)                │   │
│  │   - File Share (공유 파일)                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Azure Key Vault                        │   │
│  │   - 데이터베이스 연결 문자열                         │   │
│  │   - API 키 및 시크릿                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Application Insights                        │   │
│  │   - 애플리케이션 모니터링                           │   │
│  │   - 로그 수집 및 분석                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 사용 Azure 서비스

| 서비스 | 목적 | 티어/SKU |
|--------|------|----------|
| Azure App Service | 웹 애플리케이션 호스팅 | B1 (Basic) / S1 (Standard) |
| Azure Database for PostgreSQL | 데이터베이스 | Burstable B1ms / General Purpose D2s_v3 |
| Azure Storage Account | 파일 저장소 | Standard LRS |
| Azure Key Vault | 시크릿 관리 | Standard |
| Application Insights | 모니터링 및 로깅 | Pay-as-you-go |
| Azure Front Door (Optional) | 글로벌 부하 분산 및 WAF | Standard |
| Azure CDN (Optional) | 정적 콘텐츠 배포 | Standard Microsoft |

---

## 3. 단계별 구현 계획

### Phase 1: 기본 인프라 설정 (1주차)

#### 3.1 리소스 그룹 생성
```bash
az group create \
  --name rg-flask-journal-prod \
  --location koreacentral \
  --tags Environment=Production Application=FlaskJournal
```

#### 3.2 App Service 계획 생성
```bash
az appservice plan create \
  --name asp-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --location koreacentral \
  --sku B1 \
  --is-linux
```

#### 3.3 Web App 생성
```bash
az webapp create \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --plan asp-flask-journal-prod \
  --runtime "PYTHON:3.11"
```

### Phase 2: 데이터베이스 구성 (1주차)

#### 3.4 PostgreSQL 서버 생성
```bash
az postgres flexible-server create \
  --name psql-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --location koreacentral \
  --admin-user journaladmin \
  --admin-password <strong-password> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15 \
  --public-access 0.0.0.0
```

#### 3.5 데이터베이스 생성
```bash
az postgres flexible-server db create \
  --resource-group rg-flask-journal-prod \
  --server-name psql-flask-journal-prod \
  --database-name journaldb
```

### Phase 3: 스토리지 및 보안 (1주차)

#### 3.6 Storage Account 생성
```bash
az storage account create \
  --name stflaskjournalprod \
  --resource-group rg-flask-journal-prod \
  --location koreacentral \
  --sku Standard_LRS \
  --kind StorageV2
```

#### 3.7 Key Vault 생성
```bash
az keyvault create \
  --name kv-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --location koreacentral \
  --enable-rbac-authorization false
```

#### 3.8 시크릿 저장
```bash
# 데이터베이스 연결 문자열
az keyvault secret set \
  --vault-name kv-flask-journal-prod \
  --name DatabaseConnectionString \
  --value "postgresql://journaladmin:<password>@psql-flask-journal-prod.postgres.database.azure.com/journaldb"

# 앱 시크릿 키
az keyvault secret set \
  --vault-name kv-flask-journal-prod \
  --name FlaskSecretKey \
  --value "<generated-secret-key>"
```

### Phase 4: 모니터링 구성 (2주차)

#### 3.9 Application Insights 생성
```bash
az monitor app-insights component create \
  --app ai-flask-journal-prod \
  --location koreacentral \
  --resource-group rg-flask-journal-prod \
  --application-type web
```

#### 3.10 Web App에 Application Insights 연결
```bash
# Instrumentation Key 가져오기
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app ai-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --query instrumentationKey -o tsv)

# Web App 설정에 추가
az webapp config appsettings set \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

### Phase 5: Managed Identity 구성 (2주차)

#### 3.11 System-Assigned Managed Identity 활성화
```bash
az webapp identity assign \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod
```

#### 3.12 Key Vault 접근 권한 부여
```bash
# Web App의 Principal ID 가져오기
PRINCIPAL_ID=$(az webapp identity show \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --query principalId -o tsv)

# Key Vault 접근 정책 설정
az keyvault set-policy \
  --name kv-flask-journal-prod \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

### Phase 6: 애플리케이션 배포 (2주차)

#### 3.13 애플리케이션 설정 구성
```bash
az webapp config appsettings set \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --settings \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    DATABASE_URL=@Microsoft.KeyVault(SecretUri=https://kv-flask-journal-prod.vault.azure.net/secrets/DatabaseConnectionString/) \
    SECRET_KEY=@Microsoft.KeyVault(SecretUri=https://kv-flask-journal-prod.vault.azure.net/secrets/FlaskSecretKey/) \
    STORAGE_ACCOUNT_NAME=stflaskjournalprod
```

#### 3.14 배포 설정
```bash
# GitHub Actions를 위한 배포 자격 증명 생성
az webapp deployment source config \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --repo-url https://github.com/heegene-default-org/flask-journal-demo \
  --branch main \
  --manual-integration
```

---

## 4. CI/CD 파이프라인 구성

### 4.1 GitHub Actions 워크플로우

GitHub Actions를 사용하여 자동화된 배포 파이프라인을 구성합니다.

**워크플로우 단계:**
1. 코드 체크아웃
2. Python 환경 설정
3. 의존성 설치
4. 테스트 실행
5. 보안 스캔 (Bandit, Safety)
6. Azure Web App 배포

### 4.2 배포 슬롯 전략

```bash
# 스테이징 슬롯 생성
az webapp deployment slot create \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --slot staging

# 배포 후 스왑
az webapp deployment slot swap \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --slot staging \
  --target-slot production
```

---

## 5. 네트워크 및 보안 구성

### 5.1 VNet 통합 (Optional - Standard 이상)

```bash
# VNet 생성
az network vnet create \
  --name vnet-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --location koreacentral \
  --address-prefix 10.0.0.0/16

# 서브넷 생성
az network vnet subnet create \
  --name snet-webapp \
  --resource-group rg-flask-journal-prod \
  --vnet-name vnet-flask-journal-prod \
  --address-prefix 10.0.1.0/24 \
  --delegations Microsoft.Web/serverFarms

# VNet 통합
az webapp vnet-integration add \
  --name app-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --vnet vnet-flask-journal-prod \
  --subnet snet-webapp
```

### 5.2 네트워크 보안 그룹 (NSG)

```bash
az network nsg create \
  --name nsg-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --location koreacentral

# HTTPS만 허용
az network nsg rule create \
  --name AllowHTTPS \
  --nsg-name nsg-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --priority 100 \
  --destination-port-ranges 443 \
  --protocol Tcp \
  --access Allow
```

### 5.3 Private Endpoint (데이터베이스)

```bash
# 데이터베이스를 위한 Private Endpoint
az network private-endpoint create \
  --name pe-psql-flask-journal \
  --resource-group rg-flask-journal-prod \
  --vnet-name vnet-flask-journal-prod \
  --subnet snet-data \
  --private-connection-resource-id $(az postgres flexible-server show \
    --name psql-flask-journal-prod \
    --resource-group rg-flask-journal-prod \
    --query id -o tsv) \
  --group-id postgresqlServer \
  --connection-name conn-psql
```

---

## 6. 백업 및 재해 복구

### 6.1 데이터베이스 백업

```bash
# 자동 백업 구성 (7일 보존)
az postgres flexible-server parameter set \
  --resource-group rg-flask-journal-prod \
  --server-name psql-flask-journal-prod \
  --name backup_retention_days \
  --value 7

# Geo-redundant 백업 (선택)
az postgres flexible-server update \
  --resource-group rg-flask-journal-prod \
  --name psql-flask-journal-prod \
  --geo-redundant-backup Enabled
```

### 6.2 Web App 백업

```bash
az webapp config backup create \
  --resource-group rg-flask-journal-prod \
  --webapp-name app-flask-journal-prod \
  --container-url https://stflaskjournalprod.blob.core.windows.net/backups?<SAS-token> \
  --backup-name dailybackup \
  --frequency 1d \
  --retain-one true \
  --retention 30
```

---

## 7. 모니터링 및 알림

### 7.1 Azure Monitor 알림 규칙

```bash
# CPU 사용률이 80% 이상일 때 알림
az monitor metrics alert create \
  --name alert-high-cpu \
  --resource-group rg-flask-journal-prod \
  --scopes $(az webapp show --name app-flask-journal-prod --resource-group rg-flask-journal-prod --query id -o tsv) \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group-ids /subscriptions/<subscription-id>/resourceGroups/rg-flask-journal-prod/providers/microsoft.insights/actionGroups/ag-flask-journal

# 응답 시간이 느릴 때 알림
az monitor metrics alert create \
  --name alert-slow-response \
  --resource-group rg-flask-journal-prod \
  --scopes $(az webapp show --name app-flask-journal-prod --resource-group rg-flask-journal-prod --query id -o tsv) \
  --condition "avg HttpResponseTime > 3000" \
  --window-size 5m \
  --evaluation-frequency 1m
```

### 7.2 Log Analytics 쿼리

```kusto
// 최근 24시간 오류 로그
traces
| where timestamp > ago(24h)
| where severityLevel >= 3
| order by timestamp desc

// 느린 요청 분석
requests
| where timestamp > ago(1h)
| where duration > 1000
| summarize count(), avg(duration) by name
| order by avg_duration desc
```

---

## 8. 비용 최적화 전략

### 8.1 추정 월간 비용 (기본 구성)

| 리소스 | SKU/크기 | 예상 비용 (USD) |
|--------|----------|-----------------|
| App Service Plan (B1) | 1 인스턴스 | $13.14 |
| PostgreSQL Flexible Server (B1ms) | Burstable | $12.41 |
| Storage Account (32GB) | Standard LRS | $1.54 |
| Key Vault | Standard | $0.03 |
| Application Insights (1GB) | Pay-as-you-go | $2.30 |
| **총 예상 비용** | | **~$29.42/월** |

### 8.2 비용 절감 방안

1. **자동 스케일링 구성**
   - 트래픽이 적을 때 인스턴스 수 감소
   - 야간/주말 자동 중지 (개발/테스트 환경)

2. **예약 인스턴스 활용**
   - 1년 예약 시 최대 30% 할인
   - 3년 예약 시 최대 50% 할인

3. **Azure Hybrid Benefit**
   - 기존 라이선스 활용

4. **리소스 태깅 및 비용 관리**
   ```bash
   az tag create --resource-id <resource-id> \
     --tags CostCenter=IT Environment=Production Owner=DevTeam
   ```

---

## 9. 보안 체크리스트

- [x] HTTPS 강제 적용
- [x] Managed Identity 사용
- [x] Key Vault에 시크릿 저장
- [x] 데이터베이스 방화벽 규칙 설정
- [x] NSG를 통한 네트워크 제어
- [ ] WAF (Web Application Firewall) 구성
- [ ] DDoS Protection 활성화
- [ ] Private Endpoint 사용
- [ ] 정기적인 보안 스캔
- [ ] Defender for Cloud 활성화

---

## 10. 다음 단계 및 권장사항

### 단기 (1-3개월)
1. ✅ 기본 App Service 배포 완료
2. ✅ PostgreSQL 데이터베이스 구성
3. ✅ CI/CD 파이프라인 설정
4. ⬜ 모니터링 대시보드 구성
5. ⬜ 백업 및 복구 절차 테스트

### 중기 (3-6개월)
1. ⬜ VNet 통합 및 Private Endpoint 구성
2. ⬜ Azure Front Door를 통한 글로벌 배포
3. ⬜ 자동 스케일링 정책 최적화
4. ⬜ 성능 튜닝 및 캐싱 전략
5. ⬜ 재해 복구 계획 수립 및 테스트

### 장기 (6개월 이상)
1. ⬜ Multi-region 배포 고려
2. ⬜ AKS로의 마이그레이션 검토
3. ⬜ 고급 보안 기능 적용
4. ⬜ 머신러닝 기반 이상 탐지
5. ⬜ 비용 최적화 지속 개선

---

## 11. 참고 문서

- [Azure App Service 공식 문서](https://docs.microsoft.com/azure/app-service/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/azure/postgresql/)
- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)
- [Python on Azure App Service](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Azure Key Vault 모범 사례](https://docs.microsoft.com/azure/key-vault/general/best-practices)

---

**문서 버전:** 1.0  
**작성일:** 2025-11-17  
**검토자:** Azure Architecture Team
