# flask-journal-demo
Demo project for flask based journal app

## 기능

- 🔐 Google OAuth 로그인/로그아웃
- 📝 개인 저널 작성 및 관리
- 🗑️ 저널 삭제
- 👤 사용자별 저널 관리

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/heegene-default-org/flask-journal-demo.git
cd flask-journal-demo
```

### 2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. Google OAuth 설정

#### Google Cloud Console에서 OAuth 클라이언트 생성:

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "사용자 인증 정보"로 이동
4. "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID" 선택
5. 애플리케이션 유형: "웹 애플리케이션" 선택
6. 승인된 리디렉션 URI 추가:
   - `http://localhost:5000/authorize`
7. 클라이언트 ID와 클라이언트 보안 비밀번호 저장

### 5. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 Google OAuth 정보 입력:

```bash
cp .env.example .env
```

`.env` 파일 편집:
```
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 6. 애플리케이션 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 사용 방법

1. Google 계정으로 로그인
2. "새 저널 작성" 버튼 클릭
3. 제목과 내용을 입력하고 저장
4. 메인 페이지에서 저널 목록 확인
5. 저널 삭제 시 "삭제" 버튼 클릭

## 프로젝트 구조

```
flask-journal-demo/
├── app.py                 # 메인 애플리케이션 파일
├── requirements.txt       # Python 의존성
├── .env.example          # 환경 변수 예시
├── .gitignore            # Git 제외 파일
├── journal.db            # SQLite 데이터베이스 (자동 생성)
└── templates/            # HTML 템플릿
    ├── base.html         # 기본 레이아웃
    ├── login.html        # 로그인 페이지
    ├── index.html        # 메인 페이지 (저널 목록)
    └── new_journal.html  # 새 저널 작성 페이지
```

## 기술 스택

- **Backend**: Flask 3.0.0
- **Authentication**: Google OAuth 2.0 (Authlib)
- **Database**: SQLite (SQLAlchemy)
- **Session Management**: Flask-Login
- **Frontend**: HTML/CSS (내장 스타일)

## 보안 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- 프로덕션 환경에서는 강력한 `SECRET_KEY` 사용
- HTTPS 사용 권장 (프로덕션)
- 데이터베이스는 SQLite 대신 PostgreSQL/MySQL 사용 권장 (프로덕션)

## 라이선스

MIT License
