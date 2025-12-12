from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from collections import Counter

import numpy as np
import cv2

from backend.pipeline.engagement_pipeline import EngagementPipeline
from backend.storage.session_manager import SessionManager
from backend.analysis.report_generator import generate_report
from backend.analysis.visualization import create_charts
from backend.models.face_detector import FaceDetector
from backend.models.emotion_model import EmotionModel
from backend.core.config import EMOTION_WEIGHTS
from backend.storage.log_writer import LogWriter
from backend.utils.file_utils import ensure_dir

app = FastAPI()

# ==========================
#   GLOBAL INSTANCES
# ==========================
session_manager = SessionManager()
pipeline = EngagementPipeline()
thread = None  # background thread (pipeline loop)

# dùng riêng cho realtime /analyze_frame
rt_face_detector = FaceDetector()
rt_emotion_model = EmotionModel()

# logging cho realtime dashboard
rt_log: LogWriter | None = None
rt_session_id: str | None = None


# ==========================
#   CORS CONFIG
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
#   UTILS
# ==========================
def compute_engagement(prob_dict: dict) -> float:
    """
    Tính điểm engagement từ vector xác suất cảm xúc.
    Engagement = sum(p(emotion) * weight_emotion)
    """
    score = 0.0
    for emo, w in EMOTION_WEIGHTS.items():
        score += prob_dict.get(emo, 0.0) * w
    return score


# ==========================
#   ROOT
# ==========================
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running!"}


# ==========================
#   START SESSION (video / webcam - pipeline cũ)
# ==========================
@app.get("/start")
def start(mode: str = "video", video_path: str = "data/videos/sample.mp4"):
    """
    Khởi động 1 phiên phân tích mới (dùng cho pipeline video/webcam).
    """
    global thread

    # tạo session ID
    session_id = session_manager.create_session(mode, video_path)

    # khởi động pipeline
    pipeline.start(session_id, mode, video_path)

    # chạy loop trong thread riêng
    thread = threading.Thread(target=pipeline.loop, daemon=True)
    thread.start()

    return {"session_id": session_id, "status": "started"}


# ==========================
#   STOP SESSION + REPORT + CHARTS (pipeline cũ)

@app.get("/stop")
def stop():
    """
    Dừng phiên hiện tại, đợi ghi log xong,
    sau đó sinh báo cáo + dữ liệu biểu đồ từ file log.
    """
    global thread

    # yêu cầu pipeline dừng
    pipeline.stop()
    session_id = pipeline.current_session

    # đợi thread dừng hẳn (fix lỗi report 0-0-0)
    if thread is not None and thread.is_alive():
        thread.join()

    # đánh dấu session đã kết thúc
    session_manager.stop_session(session_id)

    # tạo báo cáo từ log
    report = generate_report(session_id)

    # tạo dữ liệu biểu đồ
    charts = create_charts(session_id)

    return {
        "session": session_id,
        "summary": report,
        "charts": charts,
    }


# ==========================
#   GET SESSION ANALYTICS
# ==========================
@app.get("/sessions/{session_id}/analytics")
def analytics(session_id: str):
    """
    Lấy lại report (summary + timeline) của 1 session bất kỳ.
    """
    return generate_report(session_id)


# ==========================
#   GET SESSION CHARTS
# ==========================
@app.get("/sessions/{session_id}/charts")
def charts(session_id: str):
    """
    Lấy lại dữ liệu biểu đồ của 1 session.
    """
    return create_charts(session_id)


# ==========================
#   REALTIME SESSION (dashboard dùng /analyze_frame)

@app.get("/rt_start")
def rt_start():
    """
    Bắt đầu 1 session realtime cho dashboard (không dùng VideoSource).
    CSV sẽ được ghi mỗi lần /analyze_frame được gọi.
    """
    global rt_log, rt_session_id

    if rt_log is not None:
        # đã có session realtime đang chạy
        return {"session_id": rt_session_id, "status": "already_started"}

    # tạo session id cho realtime
    rt_session_id = session_manager.create_session("realtime", "webcam_js")

    # đảm bảo thư mục tồn tại
    ensure_dir("output/")
    ensure_dir("output/logs/")

    # mở file log
    rt_log = LogWriter(f"output/logs/{rt_session_id}.csv")

    return {"session_id": rt_session_id, "status": "rt_started"}


@app.get("/rt_stop")
def rt_stop():
    """
    Kết thúc session realtime, đóng CSV và sinh report + charts.
    """
    global rt_log, rt_session_id

    if rt_session_id is None or rt_log is None:
        return {"error": "no_realtime_session"}

    session_id = rt_session_id

    # đóng file log
    rt_log.close()
    rt_log = None

    # đánh dấu session kết thúc
    session_manager.stop_session(session_id)

    # sinh report + charts từ CSV vừa log
    report = generate_report(session_id)
    charts = create_charts(session_id)

    rt_session_id = None

    return {
        "session": session_id,
        "summary": report,
        "charts": charts,
    }


# ==========================
#   REALTIME FRAME ANALYSIS (cho FE vẽ khung)

@app.post("/analyze_frame")
async def analyze_frame(frame: UploadFile = File(...)):
    """
    Nhận 1 frame (ảnh jpg/png) từ FE, detect nhiều mặt + emotion
    -> trả bbox + emotion + engagement cho từng mặt.

    ID ở đây là số thứ tự trong frame (1, 2, 3, ...),
    đủ để minh hoạ "Student 1, Student 2, ..." trong báo cáo.

    Nếu đang có session realtime (rt_start đã được gọi),
    thì mỗi lần gọi /analyze_frame sẽ ghi 1 dòng vào CSV.
    """

    global rt_log, rt_session_id

    # đọc raw bytes
    image_bytes = await frame.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"status": "invalid_image", "faces": []}

    # detect faces
    boxes = rt_face_detector.detect(img)

    results = []
    for idx, (x, y, w, h) in enumerate(boxes):
        if w <= 0 or h <= 0:
            continue

        face_img = img[y:y + h, x:x + w]
        if face_img is None or face_img.size == 0:
            continue

        probs, dominant = rt_emotion_model.predict(face_img)
        if probs is None:
            continue

        eng = compute_engagement(probs)

        results.append({
            "id": int(idx + 1),  # ID = 1,2,3,... trong frame hiện tại
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "emotion": str(dominant),
            "engagement": float(eng),
            "probs": {k: float(v) for k, v in probs.items()},
        })

    # GHI LOG REALTIME (nếu đang có session)
    if rt_log is not None and results:
        # engagement trung bình của cả frame
        avg_eng = sum(f["engagement"] for f in results) / len(results)
        # dominant emotion của frame = emotion xuất hiện nhiều nhất
        dominant_frame = Counter(f["emotion"] for f in results).most_common(1)[0][0]

        rt_log.write(
            time.time(),
            dominant_frame,
            avg_eng,
            avg_eng,  # ở đây raw = smooth, smoothing đã làm ở FE (line chart)
        )

    return {
        "status": "ok",
        "faces": results,
    }
