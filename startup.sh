#!/bin/bash
# Azure App Service 시작 스크립트

# Gunicorn으로 Flask 애플리케이션 실행
gunicorn --bind=0.0.0.0:8000 \
         --workers=4 \
         --timeout=600 \
         --access-logfile='-' \
         --error-logfile='-' \
         --log-level=info \
         app:app
