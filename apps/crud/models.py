from datetime import datetime
from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    user_images = db.relationship(
        "UserImage", 
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

    @staticmethod
    def is_duplicate_email(email):
        return User.query.filter_by(email=email).first() is not None

class UserImage(db.Model):
    __tablename__ = "user_images"
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    image_path = db.Column(db.String(255))
    is_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class UserImageTag(db.Model):
    __tablename__ = "user_image_tags"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_image_id = db.Column(db.String(100), db.ForeignKey("user_images.id"))
    tag_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)