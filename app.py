import os
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 데이터베이스 초기화
db = SQLAlchemy(app)

# 로그인 매니저 초기화
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth 초기화
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# 사용자 모델
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    google_id = db.Column(db.String(150), unique=True, nullable=False)
    profile_pic = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    journals = db.relationship('Journal', backref='author', lazy=True)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# 저널 모델
class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 라우트
@app.route('/')
def index():
    if current_user.is_authenticated:
        journals = Journal.query.filter_by(user_id=current_user.id).order_by(Journal.created_at.desc()).all()
        return render_template('index.html', journals=journals)
    return render_template('login.html')

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            # 사용자 조회 또는 생성
            user = User.query.filter_by(google_id=user_info['sub']).first()
            
            if not user:
                user = User(
                    email=user_info['email'],
                    name=user_info.get('name', user_info['email']),
                    google_id=user_info['sub'],
                    profile_pic=user_info.get('picture')
                )
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash('구글 로그인에 성공했습니다!', 'success')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'로그인 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('index'))

@app.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_journal():
    from flask import request
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            journal = Journal(
                title=title,
                content=content,
                user_id=current_user.id
            )
            db.session.add(journal)
            db.session.commit()
            flash('저널이 작성되었습니다!', 'success')
            return redirect(url_for('index'))
        else:
            flash('제목과 내용을 모두 입력해주세요.', 'error')
    
    return render_template('new_journal.html')

@app.route('/journal/<int:journal_id>/delete', methods=['POST'])
@login_required
def delete_journal(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    
    if journal.user_id != current_user.id:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(journal)
    db.session.commit()
    flash('저널이 삭제되었습니다.', 'info')
    return redirect(url_for('index'))

# 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
