from datetime import datetime
from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # [중요] 관계 설정은 딱 한 번만, 그리고 전체 경로로 지정합니다.
    user_images = db.relationship(
        "apps.crud.models.UserImage", 
        backref="user", 
        cascade="all, delete-orphan"
    )

    @property
    def password(self):
        raise AttributeError("비밀번호는 직접 읽을 수 없습니다.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None

class UserImage(db.Model):
    __tablename__ = "user_images"
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    image_path = db.Column(db.String)
    is_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)