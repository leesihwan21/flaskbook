from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

from apps.config import config

socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

db = SQLAlchemy()
csrf = CSRFProtect()

# LoginManager 인스턴스화
login_manager = LoginManager()

# login_view 속성에 미로그인 시 리다이렉트할 엔드포인트 지정
login_manager.login_view = "auth.signup"

# login_message 속성에 로그인 후 표시할 메시지 지정
# 여기서는 아무것도 표시하지 않도록 공백 지정
login_manager.login_message = ""


# create_app 함수 작성
def create_app(config_key):
    # Flask 인스턴스 생성
    app = Flask(__name__)
    socketio.init_app(app)
    app.config.from_object(config[config_key])

    # 2. db.init_app(app) 등이 끝난 뒤, 실제 필요할 때 여기서 임포트합니다.
    from apps.detector.service import AiStreamService

    # 스트림이 이미 실행 중인지 확인하기 위한 플래그
    is_streaming = False

    # apps/app.py
    @socketio.on('connect')
    def handle_connect():
        print("[DEBUG] 소켓 연결됨!")
    
        # 1. 아이디를 mbc320으로 변경 (VMS 설정과 동일하게)
        # 2. 비밀번호 Mbc320!! 중 !!를 %21%21로 변경하여 전송
        RTSP_URL = "rtsp://admin:Mbc320!!@192.168.0.48:554/ch0_1.264"
    
        socketio.start_background_task(AiStreamService.run_rtsp_stream, socketio, RTSP_URL)


    # apps/app.py 에 추가
    @socketio.on('set_detection_target')
    def handle_set_target(data):
        target = data.get('target')
        from apps.detector.service import AiStreamService
        AiStreamService.set_target(target)
        print(f"[DEBUG] 탐지 타겟 설정 완료: {target}")

    # SQLAlchemy와 앱을 연동
    db.init_app(app)
    # Migrate와 앱을 연동
    Migrate(app, db)
    csrf.init_app(app)

    # login_manager를 애플리케이션과 연동
    login_manager.init_app(app)

    # crud 패키지에서 views를 import
    from apps.crud import views as crud_views
    # register_blueprint를 사용하여 views의 crud를 앱에 등록
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # auth 패키지에서 views를 import
    from apps.auth import views as auth_views
    # register_blueprint를 사용하여 views의 auth를 앱에 등록
    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    # detector 패키지에서 views를 import
    from apps.detector import views as dt_views
    # register_blueprint를 사용하여 views의 detector를 앱에 등록
    app.register_blueprint(dt_views.dt, url_prefix="/")

    # 모델 import (마이그레이션 인식용)
    from apps.detector import models  # noqa

    # 커스텀 오류 화면 등록
    from apps.detector import views as error_views
    #app.register_error_handler(404, error_views.page_not_found)
    #app.register_error_handler(500, error_views.internal_server_error)

    return app