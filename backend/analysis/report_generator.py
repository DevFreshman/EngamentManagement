import os
import pandas as pd
from backend.analysis.stats import compute_stats

def generate_report(session_id):
    log_path = f"output/logs/{session_id}.csv"

    # File không tồn tại
    if not os.path.exists(log_path):
        return {
            "session_id": session_id,
            "error": "log_not_found",
            "summary": None,
            "timeline": [],
            "emotions": []
        }

    # File tồn tại nhưng size = 0 → không có data (webcam không detect được mặt)
    if os.path.getsize(log_path) == 0:
        return {
            "session_id": session_id,
            "warning": "empty_log",
            "summary": {
                "avg": 0,
                "max": 0,
                "min": 0,
                "emotion_distribution": {}
            },
            "timeline": [],
            "emotions": []
        }

    # Đọc file CSV – file có thể hợp lệ hoặc chỉ có 1 dòng header
    try:
        df = pd.read_csv(log_path)
    except Exception:
        # Lỗi pandas khi file hỏng hoặc chỉ có header
        return {
            "session_id": session_id,
            "warning": "csv_read_error",
            "summary": {
                "avg": 0,
                "max": 0,
                "min": 0,
                "emotion_distribution": {}
            },
            "timeline": [],
            "emotions": []
        }

    # CSV chỉ có header nhưng không có dữ liệu
    if len(df) == 0:
        return {
            "session_id": session_id,
            "warning": "no_rows_in_log",
            "summary": {
                "avg": 0,
                "max": 0,
                "min": 0,
                "emotion_distribution": {}
            },
            "timeline": [],
            "emotions": []
        }

    # Compute stats bình thường
    stats = compute_stats(log_path)

    return {
        "session_id": session_id,
        "summary": stats,
        "timeline": df["eng_smooth"].tolist(),
        "emotions": df["emotion"].tolist(),
    }
