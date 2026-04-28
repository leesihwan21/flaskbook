import cv2
from flask import Flask, Response

app = Flask(__name__)

# 카메라 설정을 최적화하여 엽니다.
def open_cam():
    # cv2.CAP_V4L2를 명시하여 리눅스 비디오 드라이버를 직접 사용합니다.
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    # WSL 환경에서 호환성이 가장 좋은 MJPG 포맷 지정
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # 프레임 버퍼를 최소화하여 지연시간 감소
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

camera = open_cam()

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            # 프레임을 못 읽으면 카메라를 다시 열어봅니다.
            print("⚠️ 카메라 프레임 읽기 실패... 재시도 중")
            continue
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return """
    <html>
        <body style="background: #222; color: white; text-align: center; font-family: sans-serif;">
            <h1>🎥 USB CAM 실시간 스트리밍</h1>
            <div style="margin: 20px auto; width: 80%; max-width: 800px; border: 10px solid #444;">
                <img src="/video_feed" style="width: 100%;">
            </div>
            <p>상태: <span style="color: #0f0;">ONLINE (Port 5001)</span></p>
        </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    if not camera.isOpened():
        print("❌ 장치는 붙어있으나 카메라를 초기화할 수 없습니다.")
    else:
        print("✅ 스트리밍 서버 시작! http://127.0.0.1:5001 로 접속하세요.")
        app.run(host='0.0.0.0', port=5001, threaded=True)