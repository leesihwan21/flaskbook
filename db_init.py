import os
import shutil
from apps.app import create_app, db
from flask_migrate import init

# 1. 기존 migrations 폴더가 있다면 삭제 (새로 시작하기 위해)
if os.path.exists("migrations"):
    shutil.rmtree("migrations")

# 2. 앱 생성
app = create_app("local")

# 3. DB 초기화 실행
with app.app_context():
    try:
        init()
        print("✅ 성공: migrations 폴더가 생성되었습니다!")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")