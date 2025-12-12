from backend.core.config import EMOTION_WEIGHTS

def compute_engagement(prob_dict):
    score = 0.0
    for emo, w in EMOTION_WEIGHTS.items():
        score += prob_dict.get(emo, 0.0) * w
    return score

def process_frame(frame, face_detector, emotion_model, smoother):
    # 1. detect face
    faces = face_detector.detect(frame)
    if len(faces) == 0:
        # không có mặt -> bỏ frame
        return None

    # 2. lấy face đầu tiên
    x, y, w, h = faces[0]

    if w <= 0 or h <= 0:
        return None

    # 3. crop mặt
    face_img = frame[y:y+h, x:x+w]

    # nếu crop ra ảnh rỗng
    if face_img is None or face_img.size == 0:
        return None

    # 4. predict emotion
    probs, dominant = emotion_model.predict(face_img)
    if probs is None:
        return None

    # 5. tính engagement
    eng_raw = compute_engagement(probs)
    eng_smooth = smoother.update(eng_raw)

    return {
        "faces": faces,
        "dominant": dominant,
        "eng_raw": eng_raw,
        "eng_smooth": eng_smooth,
    }
