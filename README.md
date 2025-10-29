# Flask Journal Demo

감성적인 디자인의 일기장 웹 애플리케이션

## Features

- **감정 기반 일기 작성**: 기쁨, 슬픔, 화남, 평온 감정으로 일기 분류
- **아름다운 UI**: Bootstrap 5와 Glass-morphism 디자인
- **반응형 디자인**: 모바일과 데스크톱 모두 지원
- **완전한 CRUD**: 일기 작성, 읽기, 수정, 삭제
- **날짜별 정렬**: 최신 일기부터 표시
- **안전한 구현**: 보안 모범 사례 적용

## Tech Stack

- **Backend**: Flask 3.0.0, SQLAlchemy, SQLite
- **Frontend**: Bootstrap 5, Glass-morphism CSS
- **Security**: Environment-based configuration, Input validation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd flask-journal-demo

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Configuration

Set environment variables for production:

```bash
export SECRET_KEY="your-secret-key-here"
export FLASK_DEBUG="false"
```

## Usage

1. Open http://127.0.0.1:5000 in your browser
2. Click "일기 쓰기" to create a new journal entry
3. Select your emotion and write your thoughts
4. View, edit, or delete entries from the main page

## Project Structure

```
flask-journal-demo/
├── app.py              # Main Flask application
├── models.py           # Database models
├── requirements.txt    # Python dependencies
└── templates/         
    ├── base.html      # Base template with common layout
    ├── index.html     # Main page with journal list
    ├── write.html     # Create/edit journal entry
    └── detail.html    # View single journal entry
```
