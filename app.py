from flask import Flask
import os

app = Flask(__name__)

# 설정
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def index():
    """메인 페이지"""
    return '''
    <html>
        <head>
            <title>Flask Journal Demo</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #0078d4;
                    margin-bottom: 20px;
                }
                .info {
                    background: #e7f3ff;
                    padding: 15px;
                    border-left: 4px solid #0078d4;
                    margin: 20px 0;
                }
                .status {
                    color: #107c10;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Flask Journal Demo</h1>
                <p class="status">✅ 애플리케이션이 성공적으로 실행 중입니다!</p>
                
                <div class="info">
                    <h3>Azure 배포 정보</h3>
                    <p>이 애플리케이션은 Azure App Service에서 실행되도록 설계되었습니다.</p>
                    <ul>
                        <li>Python Flask 웹 프레임워크</li>
                        <li>Azure PostgreSQL 데이터베이스</li>
                        <li>Azure Blob Storage 파일 저장</li>
                        <li>Azure Key Vault 시크릿 관리</li>
                        <li>Application Insights 모니터링</li>
                    </ul>
                </div>

                <div class="info">
                    <h3>다음 단계</h3>
                    <ol>
                        <li>Azure 리소스 배포 (<code>deploy-azure-infrastructure.sh</code> 실행)</li>
                        <li>데이터베이스 마이그레이션</li>
                        <li>GitHub Actions를 통한 CI/CD 설정</li>
                        <li>Application Insights에서 모니터링 확인</li>
                    </ol>
                </div>

                <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                    📚 자세한 내용은 
                    <a href="https://github.com/heegene-default-org/flask-journal-demo/blob/main/AZURE_DEPLOYMENT_PLAN.md" 
                       style="color: #0078d4;">Azure 배포 계획서</a>를 참조하세요.
                </p>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    """헬스 체크 엔드포인트"""
    return {
        'status': 'healthy',
        'version': '1.0.0'
    }, 200

if __name__ == '__main__':
    app.run(debug=True)
