from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, JournalEntry
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """메인 페이지 - 일기 목록"""
    entries = JournalEntry.query.order_by(JournalEntry.created_at.desc()).all()
    return render_template('index.html', entries=entries)

@app.route('/write')
def write():
    """일기 작성 페이지"""
    return render_template('write.html', entry=None)

@app.route('/write/<int:entry_id>')
def edit(entry_id):
    """일기 수정 페이지"""
    entry = JournalEntry.query.get_or_404(entry_id)
    return render_template('write.html', entry=entry)

@app.route('/save', methods=['POST'])
def save():
    """일기 저장"""
    title = request.form.get('title')
    content = request.form.get('content')
    emotion = request.form.get('emotion')
    entry_id = request.form.get('entry_id')
    
    if not title or not content or not emotion:
        flash('모든 필드를 입력해주세요.', 'error')
        return redirect(url_for('write'))
    
    if entry_id:
        # 수정
        entry = JournalEntry.query.get_or_404(entry_id)
        entry.title = title
        entry.content = content
        entry.emotion = emotion
        entry.updated_at = datetime.utcnow()
        flash('일기가 수정되었습니다.', 'success')
    else:
        # 새 일기 작성
        entry = JournalEntry(title=title, content=content, emotion=emotion)
        db.session.add(entry)
        flash('일기가 저장되었습니다.', 'success')
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/detail/<int:entry_id>')
def detail(entry_id):
    """일기 상세 보기"""
    entry = JournalEntry.query.get_or_404(entry_id)
    return render_template('detail.html', entry=entry)

@app.route('/delete/<int:entry_id>')
def delete(entry_id):
    """일기 삭제"""
    entry = JournalEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('일기가 삭제되었습니다.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)