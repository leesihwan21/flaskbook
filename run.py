from apps.app import create_app, socketio
import os

# "local" 설정으로 앱 생성
app = create_app("local")

if __name__ == '__main__':
    # SocketIO 전용 실행 방식 (eventlet 기반)
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)