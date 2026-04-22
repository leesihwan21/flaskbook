import uuid
from datetime import datetime
from apps.app import db, login_manager
# ★ 핵심: auth 모듈에서 정의된 User 모델을 가져옵니다. 
# 이렇게 해야 'users' 테이블 중복 정의 에러가 사라집니다.
from apps.auth.models import User 

# 2. UserImage 모델
class UserImage(db.Model):
    __tablename__ = "user_images"
    # ★ 아래 한 줄을 반드시 추가하세요!
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    image_path = db.Column(db.String)
    is_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # UserImage와 UserImageTag의 1:N 관계
    user_image_tags = db.relationship("UserImageTag", backref="user_image")

# 3. UserImageTag 모델
class UserImageTag(db.Model):
    __tablename__ = "user_image_tags"
    # ★ 여기도 추가하는 것이 안전합니다.
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_image_id = db.Column(db.String, db.ForeignKey("user_images.id"))
    tag_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)