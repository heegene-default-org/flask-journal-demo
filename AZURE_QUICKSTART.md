# Azure 배포 가이드
## Flask Journal Demo 빠른 시작

이 가이드는 Flask Journal Demo 애플리케이션을 Azure에 신속하게 배포하는 방법을 설명합니다.

---

## 📋 사전 요구사항

- Azure 구독 계정
- Azure CLI 설치 ([설치 가이드](https://docs.microsoft.com/cli/azure/install-azure-cli))
- Git
- Python 3.11 이상 (로컬 개발용)

---

## 🚀 빠른 배포 (5분)

### 1단계: Azure CLI 로그인

```bash
az login
```

원하는 구독 선택:
```bash
az account set --subscription "<Your-Subscription-ID>"
```

### 2단계: 환경 변수 설정 (선택사항)

```bash
export RESOURCE_GROUP="rg-flask-journal-prod"
export LOCATION="koreacentral"
export WEBAPP_NAME="app-flask-journal-prod"
export POSTGRES_ADMIN_PASSWORD="YourStrongPassword123!"
```

### 3단계: 인프라 배포

#### 방법 A: Bash 스크립트 사용 (권장)

```bash
chmod +x deploy-azure-infrastructure.sh
./deploy-azure-infrastructure.sh
```

#### 방법 B: Bicep 템플릿 사용

```bash
# 리소스 그룹 생성
az group create --name rg-flask-journal-prod --location koreacentral

# Bicep 템플릿 배포
az deployment group create \
  --resource-group rg-flask-journal-prod \
  --template-file azure-infrastructure.bicep \
  --parameters postgresAdminPassword='YourStrongPassword123!'
```

### 4단계: 애플리케이션 배포

#### 방법 A: Azure CLI로 직접 배포

```bash
# 웹앱 이름 확인 (Bicep 배포 후 출력에서 확인)
WEBAPP_NAME="<your-webapp-name>"

# ZIP 배포
zip -r app.zip . -x "*.git*" "*venv*" "*__pycache__*"
az webapp deployment source config-zip \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME \
  --src app.zip
```

#### 방법 B: GitHub Actions 사용 (CI/CD)

1. GitHub Secrets 설정:
   - `AZURE_CREDENTIALS`: Azure 서비스 주체 자격 증명

2. Azure 서비스 주체 생성:
```bash
az ad sp create-for-rbac \
  --name "flask-journal-github-actions" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/rg-flask-journal-prod \
  --sdk-auth
```

3. 출력된 JSON을 GitHub Secrets의 `AZURE_CREDENTIALS`에 저장

4. GitHub Actions 워크플로우 파일 생성:
```bash
mkdir -p .github/workflows
cat > .github/workflows/azure-deploy.yml << 'EOF'
name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_WEBAPP_NAME: app-flask-journal-prod
  PYTHON_VERSION: '3.11'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        package: .
EOF

git add .github/workflows/azure-deploy.yml
git commit -m "Add GitHub Actions workflow"
git push
```

---

## 🔧 배포 후 설정

### 1. 데이터베이스 마이그레이션 (필요시)

```bash
# SSH를 통해 Web App에 접속
az webapp ssh --resource-group rg-flask-journal-prod --name $WEBAPP_NAME

# 마이그레이션 실행
flask db upgrade
```

### 2. 애플리케이션 확인

배포된 애플리케이션 URL 확인:
```bash
az webapp show \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME \
  --query defaultHostName -o tsv
```

브라우저에서 `https://<your-app-name>.azurewebsites.net` 접속

### 3. 로그 확인

```bash
# 실시간 로그 스트리밍
az webapp log tail \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME

# 로그 다운로드
az webapp log download \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME
```

---

## 📊 모니터링

### Application Insights 대시보드

1. Azure Portal에서 Application Insights 리소스 열기
2. "Application Dashboard" 클릭
3. 성능, 오류, 사용자 메트릭 확인

### 커스텀 쿼리 (Log Analytics)

```kusto
// 최근 24시간 요청 분석
requests
| where timestamp > ago(24h)
| summarize count() by bin(timestamp, 1h), resultCode
| render timechart

// 오류 추적
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc
```

---

## 🔒 보안 설정

### 1. HTTPS 강제 (이미 설정됨)

```bash
az webapp update \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME \
  --https-only true
```

### 2. 커스텀 도메인 설정

```bash
# 도메인 추가
az webapp config hostname add \
  --resource-group rg-flask-journal-prod \
  --webapp-name $WEBAPP_NAME \
  --hostname www.yourdomain.com

# SSL 인증서 바인딩
az webapp config ssl bind \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

### 3. IP 제한 (선택사항)

```bash
az webapp config access-restriction add \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME \
  --rule-name AllowOfficeIP \
  --action Allow \
  --ip-address 1.2.3.4/32 \
  --priority 100
```

---

## 💰 비용 관리

### 예상 월간 비용

| 구성 | 비용 (USD) |
|------|-----------|
| 개발 환경 (B1) | ~$28/월 |
| 프로덕션 환경 (S1) | ~$264/월 |

### 비용 절감 팁

1. **개발 환경 자동 종료**
```bash
# 야간 자동 중지 (평일 19:00)
# Azure Automation 또는 Logic Apps 사용
```

2. **예약 인스턴스 구매**
```bash
# 1년 약정 시 30% 할인
# 3년 약정 시 50% 할인
```

3. **자동 스케일링 설정**
```bash
az monitor autoscale create \
  --resource-group rg-flask-journal-prod \
  --name autoscale-rules \
  --resource $(az appservice plan show --name asp-flask-journal-prod --resource-group rg-flask-journal-prod --query id -o tsv) \
  --min-count 1 \
  --max-count 3 \
  --count 1
```

---

## 🧹 리소스 정리

### 개별 리소스 삭제

```bash
az webapp delete --resource-group rg-flask-journal-prod --name $WEBAPP_NAME
```

### 전체 리소스 그룹 삭제 (모든 리소스 제거)

```bash
az group delete --name rg-flask-journal-prod --yes --no-wait
```

---

## 📖 추가 문서

- [Azure 배포 구현 계획서](./AZURE_DEPLOYMENT_PLAN.md) - 상세한 배포 계획 및 아키텍쳐
- [Azure 아키텍쳐 리뷰 보고서](./AZURE_ARCHITECTURE_REVIEW.md) - 포괄적인 아키텍쳐 분석 및 권장사항
- [Azure App Service 공식 문서](https://docs.microsoft.com/azure/app-service/)
- [Python on Azure 가이드](https://docs.microsoft.com/azure/app-service/quickstart-python)

---

## 🆘 트러블슈팅

### 애플리케이션이 시작되지 않음

1. 로그 확인:
```bash
az webapp log tail --resource-group rg-flask-journal-prod --name $WEBAPP_NAME
```

2. 환경 변수 확인:
```bash
az webapp config appsettings list \
  --resource-group rg-flask-journal-prod \
  --name $WEBAPP_NAME
```

### 데이터베이스 연결 실패

1. 방화벽 규칙 확인:
```bash
az postgres flexible-server firewall-rule list \
  --resource-group rg-flask-journal-prod \
  --name psql-flask-journal-prod
```

2. 연결 문자열 확인:
```bash
az keyvault secret show \
  --vault-name kv-flask-journal-prod \
  --name DatabaseConnectionString
```

### 502/503 오류

1. App Service Plan 스케일업:
```bash
az appservice plan update \
  --name asp-flask-journal-prod \
  --resource-group rg-flask-journal-prod \
  --sku S1
```

2. Gunicorn 워커 수 조정 (startup.sh)

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:
- [Azure 지원 센터](https://azure.microsoft.com/support/)
- [GitHub Issues](https://github.com/heegene-default-org/flask-journal-demo/issues)
- [Stack Overflow - Azure Tag](https://stackoverflow.com/questions/tagged/azure)

---

**마지막 업데이트**: 2025-11-17  
**버전**: 1.0
