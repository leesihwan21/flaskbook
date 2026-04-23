import pytest
import io

# 1. 메인 페이지 테스트
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

# tests/test_detector.py
from flask import url_for

# tests/test_detector.py
def test_upload_page(app, logged_in_client):
    with app.test_request_context():
        url = url_for("detector.upload_image")
    
    response = logged_in_client.get(url)
    
    # [디버깅용] 어디로 가라고 하는지 확인
    if response.status_code == 302:
        print(f"\n[DEBUG] Redirected to: {response.location}")
        
    assert response.status_code == 200

def test_upload_no_image(logged_in_client):
    response = logged_in_client.post("/images/new", data={})
    assert response.status_code in [200, 400]

# 4. 잘못된 이미지 ID로 탐지 시도
def test_detect_invalid_id(client):
    response = client.post("/images/detect/99999")
    assert response.status_code in [404, 302, 500]

# 5. 없는 이미지 삭제 시도
def test_delete_invalid_id(client):
    response = client.post("/images/delete/99999")
    assert response.status_code in [404, 302, 500]