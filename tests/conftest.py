import os
import shutil
import pytest
from apps.app import create_app, db
from apps.crud.models import User, UserImage, UserImageTag

@pytest.fixture
def app(): # 이름을 app으로 변경하여 테스트 코드와 맞춥니다.
    # 1. 테스트용 앱 생성 및 설정
    app = create_app("testing")
    
    # 이미지 업로드 경로 설정 (KeyError 방지)
    app.config.update(
        UPLOAD_FOLDER=os.path.join(app.root_path, "tests", "test_images")
    )

    app.app_context().push()
    
    # 2. 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()
    
    # 3. 테스트용 이미지 디렉토리 생성
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    yield app
    
    # 4. 테스트 종료 후 정리 (Cleanup)
    with app.app_context():
        # 순서대로 삭제하여 외래 키 제약 조건 충돌 방지
        UserImageTag.query.delete()
        UserImage.query.delete()
        User.query.delete()
        db.session.commit()
        
    if os.path.exists(app.config["UPLOAD_FOLDER"]):
        shutil.rmtree(app.config["UPLOAD_FOLDER"])

@pytest.fixture
def client(app):
    """테스트용 클라이언트 피스처"""
    return app.test_client()

@pytest.fixture
def logged_in_client(client):
    """로그인된 상태의 클라이언트를 반환하는 피스처"""
    # 테스트용 사용자 생성
    user = User(
        username="testuser",
        email="test@example.com",
        password="password"
    )
    db.session.add(user)
    db.session.commit()

    # 로그인 수행
    client.post(
        "/auth/login",
        data=dict(email="test@example.com", password="password"),
        follow_redirects=True
    )
    return client