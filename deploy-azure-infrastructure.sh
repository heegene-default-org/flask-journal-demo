#!/bin/bash

# Azure Flask Journal Demo - 인프라 배포 스크립트
# 이 스크립트는 Flask Journal 애플리케이션을 위한 Azure 리소스를 생성합니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 설정
RESOURCE_GROUP=${RESOURCE_GROUP:-"rg-flask-journal-prod"}
LOCATION=${LOCATION:-"koreacentral"}
APP_SERVICE_PLAN=${APP_SERVICE_PLAN:-"asp-flask-journal-prod"}
WEBAPP_NAME=${WEBAPP_NAME:-"app-flask-journal-prod"}
POSTGRES_SERVER=${POSTGRES_SERVER:-"psql-flask-journal-prod"}
POSTGRES_ADMIN_USER=${POSTGRES_ADMIN_USER:-"journaladmin"}
POSTGRES_DB_NAME=${POSTGRES_DB_NAME:-"journaldb"}
STORAGE_ACCOUNT=${STORAGE_ACCOUNT:-"stflaskjournalprod"}
KEYVAULT_NAME=${KEYVAULT_NAME:-"kv-flask-journal-prod"}
APP_INSIGHTS_NAME=${APP_INSIGHTS_NAME:-"ai-flask-journal-prod"}

log_info "Flask Journal Demo - Azure 인프라 배포 시작"
log_info "리소스 그룹: $RESOURCE_GROUP"
log_info "위치: $LOCATION"

# Azure CLI 로그인 확인
log_info "Azure CLI 인증 상태 확인 중..."
if ! az account show &> /dev/null; then
    log_error "Azure CLI에 로그인되어 있지 않습니다."
    log_info "다음 명령어로 로그인하세요: az login"
    exit 1
fi

log_info "현재 구독: $(az account show --query name -o tsv)"

# 1. 리소스 그룹 생성
log_info "Step 1/9: 리소스 그룹 생성 중..."
if az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "리소스 그룹 '$RESOURCE_GROUP'이 이미 존재합니다."
else
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags Environment=Production Application=FlaskJournal
    log_info "리소스 그룹 생성 완료"
fi

# 2. App Service Plan 생성
log_info "Step 2/9: App Service Plan 생성 중..."
if az appservice plan show --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "App Service Plan '$APP_SERVICE_PLAN'이 이미 존재합니다."
else
    az appservice plan create \
        --name "$APP_SERVICE_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku B1 \
        --is-linux
    log_info "App Service Plan 생성 완료"
fi

# 3. Web App 생성
log_info "Step 3/9: Web App 생성 중..."
if az webapp show --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "Web App '$WEBAPP_NAME'이 이미 존재합니다."
else
    az webapp create \
        --name "$WEBAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "PYTHON:3.11"
    
    # HTTPS 강제 설정
    az webapp update \
        --name "$WEBAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --https-only true
    
    # 최소 TLS 버전 설정
    az webapp config set \
        --name "$WEBAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --min-tls-version 1.2
    
    log_info "Web App 생성 완료"
fi

# 4. PostgreSQL 서버 생성
log_info "Step 4/9: PostgreSQL 서버 생성 중..."
if az postgres flexible-server show --name "$POSTGRES_SERVER" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "PostgreSQL 서버 '$POSTGRES_SERVER'이 이미 존재합니다."
else
    # 비밀번호 생성 (실제 환경에서는 환경 변수로 받아야 함)
    if [ -z "$POSTGRES_ADMIN_PASSWORD" ]; then
        log_warn "POSTGRES_ADMIN_PASSWORD 환경 변수가 설정되지 않았습니다."
        log_warn "임시 비밀번호를 생성합니다. 배포 후 반드시 변경하세요!"
        POSTGRES_ADMIN_PASSWORD=$(openssl rand -base64 32)
        echo "PostgreSQL Admin Password: $POSTGRES_ADMIN_PASSWORD" > .postgres-password.txt
        log_info "비밀번호가 .postgres-password.txt에 저장되었습니다."
    fi
    
    az postgres flexible-server create \
        --name "$POSTGRES_SERVER" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --admin-user "$POSTGRES_ADMIN_USER" \
        --admin-password "$POSTGRES_ADMIN_PASSWORD" \
        --sku-name Standard_B1ms \
        --tier Burstable \
        --storage-size 32 \
        --version 15 \
        --public-access 0.0.0.0
    
    log_info "PostgreSQL 서버 생성 완료"
    
    # 데이터베이스 생성
    az postgres flexible-server db create \
        --resource-group "$RESOURCE_GROUP" \
        --server-name "$POSTGRES_SERVER" \
        --database-name "$POSTGRES_DB_NAME"
    
    log_info "데이터베이스 '$POSTGRES_DB_NAME' 생성 완료"
fi

# 5. Storage Account 생성
log_info "Step 5/9: Storage Account 생성 중..."
if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "Storage Account '$STORAGE_ACCOUNT'이 이미 존재합니다."
else
    az storage account create \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku Standard_LRS \
        --kind StorageV2
    
    log_info "Storage Account 생성 완료"
    
    # Blob 컨테이너 생성
    STORAGE_KEY=$(az storage account keys list \
        --account-name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --query '[0].value' -o tsv)
    
    for container in "uploads" "static" "backups"; do
        az storage container create \
            --name "$container" \
            --account-name "$STORAGE_ACCOUNT" \
            --account-key "$STORAGE_KEY" \
            --public-access off
        log_info "컨테이너 '$container' 생성 완료"
    done
fi

# 6. Key Vault 생성
log_info "Step 6/9: Key Vault 생성 중..."
if az keyvault show --name "$KEYVAULT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "Key Vault '$KEYVAULT_NAME'이 이미 존재합니다."
else
    az keyvault create \
        --name "$KEYVAULT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --enable-rbac-authorization false
    
    log_info "Key Vault 생성 완료"
fi

# 7. Application Insights 생성
log_info "Step 7/9: Application Insights 생성 중..."
if az monitor app-insights component show --app "$APP_INSIGHTS_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_warn "Application Insights '$APP_INSIGHTS_NAME'이 이미 존재합니다."
else
    az monitor app-insights component create \
        --app "$APP_INSIGHTS_NAME" \
        --location "$LOCATION" \
        --resource-group "$RESOURCE_GROUP" \
        --application-type web
    
    log_info "Application Insights 생성 완료"
fi

# 8. Managed Identity 설정
log_info "Step 8/9: Managed Identity 구성 중..."
PRINCIPAL_ID=$(az webapp identity assign \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query principalId -o tsv)

log_info "Managed Identity Principal ID: $PRINCIPAL_ID"

# Key Vault 접근 권한 부여
az keyvault set-policy \
    --name "$KEYVAULT_NAME" \
    --object-id "$PRINCIPAL_ID" \
    --secret-permissions get list

log_info "Key Vault 접근 권한 부여 완료"

# 9. 시크릿 저장
log_info "Step 9/9: 시크릿 저장 중..."

# Flask Secret Key 생성 및 저장
FLASK_SECRET_KEY=$(openssl rand -base64 32)
az keyvault secret set \
    --vault-name "$KEYVAULT_NAME" \
    --name "FlaskSecretKey" \
    --value "$FLASK_SECRET_KEY" \
    > /dev/null

# 데이터베이스 연결 문자열 저장
if [ -n "$POSTGRES_ADMIN_PASSWORD" ]; then
    DB_CONNECTION_STRING="postgresql://${POSTGRES_ADMIN_USER}:${POSTGRES_ADMIN_PASSWORD}@${POSTGRES_SERVER}.postgres.database.azure.com/${POSTGRES_DB_NAME}?sslmode=require"
    az keyvault secret set \
        --vault-name "$KEYVAULT_NAME" \
        --name "DatabaseConnectionString" \
        --value "$DB_CONNECTION_STRING" \
        > /dev/null
fi

log_info "시크릿 저장 완료"

# Application Insights Instrumentation Key 가져오기
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app "$APP_INSIGHTS_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query instrumentationKey -o tsv)

# 10. Web App 설정 구성
log_info "Web App 설정 구성 중..."
az webapp config appsettings set \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        FLASK_APP=app.py \
        FLASK_ENV=production \
        SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://${KEYVAULT_NAME}.vault.azure.net/secrets/FlaskSecretKey/)" \
        DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://${KEYVAULT_NAME}.vault.azure.net/secrets/DatabaseConnectionString/)" \
        STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT" \
        APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY" \
    > /dev/null

log_info "Web App 설정 완료"

# 배포 완료 메시지
echo ""
log_info "=========================================="
log_info "Azure 인프라 배포 완료!"
log_info "=========================================="
echo ""
log_info "리소스 정보:"
log_info "  - 리소스 그룹: $RESOURCE_GROUP"
log_info "  - Web App URL: https://${WEBAPP_NAME}.azurewebsites.net"
log_info "  - PostgreSQL 서버: ${POSTGRES_SERVER}.postgres.database.azure.com"
log_info "  - Storage Account: $STORAGE_ACCOUNT"
log_info "  - Key Vault: $KEYVAULT_NAME"
echo ""
log_info "다음 단계:"
log_info "  1. 애플리케이션 코드를 배포하세요"
log_info "  2. 데이터베이스 마이그레이션을 실행하세요"
log_info "  3. Application Insights에서 모니터링을 확인하세요"
echo ""

if [ -f ".postgres-password.txt" ]; then
    log_warn "중요: PostgreSQL 관리자 비밀번호가 .postgres-password.txt에 저장되어 있습니다."
    log_warn "이 파일을 안전한 곳에 보관하고 저장소에 커밋하지 마세요!"
fi
