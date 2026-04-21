from datetime import datetime

from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


# db.Model을 상속받은 User 클래스 작성
class User(db.Model, UserMixin):
    # 테이블 이름 지정
    __tablename__ = "users"
    
    # 컬럼 정의
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 패스워드 설정을 위한 프로퍼티
    @property
    def password(self):
        raise AttributeError("비밀번호는 직접 읽을 수 없습니다.")

    # 패스워드 세터 함수: 비밀번호를 해시화하여 저장
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 패스워드 일치 여부 확인
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 메일 주소 중복 체크
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None


# 로그인한 사용자 정보를 가져오는 로더 함수
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)