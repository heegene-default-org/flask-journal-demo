"""Flask 애플리케이션 실행 파일"""
import os
from app import create_app, db

# 애플리케이션 생성
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Flask 쉘 컨텍스트"""
    from app.models import User, Entry
    return {
        'db': db,
        'User': User,
        'Entry': Entry
    }


@app.cli.command()
def init_db():
    """데이터베이스 초기화"""
    db.create_all()
    print('데이터베이스가 초기화되었습니다.')


@app.cli.command()
def create_test_data():
    """테스트 데이터 생성"""
    from app.models import User, Entry
    
    # 테스트 사용자 생성
    user = User(username='test_user', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # 테스트 일기 생성
    entries = [
        Entry(
            user_id=user.id,
            title='첫 번째 일기',
            content='오늘은 날씨가 좋았다. Docker를 배우는 중이다.',
            mood='행복',
            tags=['날씨', '학습']
        ),
        Entry(
            user_id=user.id,
            title='두 번째 일기',
            content='Flask 애플리케이션 개발이 재미있다.',
            mood='즐거움',
            tags=['개발', 'Flask']
        ),
        Entry(
            user_id=user.id,
            title='세 번째 일기',
            content='컨테이너화를 마쳤다. 배포가 쉬워질 것 같다.',
            mood='만족',
            tags=['Docker', '배포']
        )
    ]
    
    for entry in entries:
        db.session.add(entry)
    
    db.session.commit()
    print('테스트 데이터가 생성되었습니다.')
    print(f'사용자: test_user / 비밀번호: password123')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
