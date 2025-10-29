from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(20), nullable=False)  # 기쁨, 슬픔, 화남, 평온
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<JournalEntry {self.title}>'
    
    @property
    def emotion_color(self):
        """감정별 색상 테마 반환"""
        emotion_colors = {
            '기쁨': 'success',  # 초록색
            '슬픔': 'primary',  # 파란색
            '화남': 'danger',   # 빨간색
            '평온': 'info'      # 하늘색
        }
        return emotion_colors.get(self.emotion, 'secondary')
    
    @property
    def emotion_icon(self):
        """감정별 아이콘 반환"""
        emotion_icons = {
            '기쁨': '😊',
            '슬픔': '😢',
            '화남': '😠',
            '평온': '😌'
        }
        return emotion_icons.get(self.emotion, '📝')