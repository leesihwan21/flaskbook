import cv2
import torch
import base64
import time
import os
from ultralytics import YOLO

class AiStreamService:
    _model = None
    _target_label = ""
    _device = 'cuda' if torch.cuda.is_available() else 'cpu'
    _running = False

    @classmethod
    def load_model(cls):
        if cls._model is None:
            cls._model = YOLO('yolov8n.pt')
            cls._model.to(cls._device)
            print(f"AI Model Loaded on: {cls._device}")
        return cls._model

    @classmethod
    def set_target(cls, label):
        cls._target_label = label.strip().lower()

    @classmethod
    def run_rtsp_stream(cls, socketio, rtsp_url):
        cls._running = True

        # ✅ USB CAM (숫자) vs IP CAM (문자열) 분기
        if isinstance(rtsp_url, int):
            print(f"[USB CAM] /dev/video{rtsp_url} 연결 시도...")
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_V4L2)
        else:
            print(f"[IP CAM] RTSP 연결 시도...")
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            print(f"[ERROR] 연결 실패: {rtsp_url}")
            return

        model = cls.load_model()
        frame_count = 0
        print(f"[START] AI 모니터링 시작 (Device: {cls._device})")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                socketio.sleep(0.1)
                continue

            frame = cv2.resize(frame, (640, 480))
            frame_count += 1

            if frame_count % 3 != 0:
                continue

            results = model.predict(frame, device='cpu', conf=0.7, verbose=False, imgsz=640)
            boxes = results[0].boxes
            annotated_frame = results[0].plot()

            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            encoded_image = base64.b64encode(buffer).decode('utf-8')

            socketio.emit('ai_frame', {
                'image': f"data:image/jpeg;base64,{encoded_image}",
                'count': frame_count
            })

            if cls._target_label:
                detected_names = [model.names[int(cls_idx)].lower() for cls_idx in boxes.cls.tolist()]
                if cls._target_label in detected_names:
                    socketio.emit('detection_alert', {
                        'label': cls._target_label,
                        'time': time.strftime('%H:%M:%S')
                    })

            socketio.sleep(0.01)

        cap.release()