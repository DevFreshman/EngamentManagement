from deepface import DeepFace

class EmotionModel:
    def __init__(self):
        # dùng DeepFace như 1 engine stateless
        self.engine = DeepFace

    def predict(self, face_img):
        try:
            # gọi DeepFace, bỏ detect lại (vì mình đã detect face rồi)
            result = self.engine.analyze(
                face_img,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="skip"  # 👈 quan trọng
            )

            # DeepFace đôi khi trả list
            if isinstance(result, list):
                if len(result) == 0:
                    return None, None
                result = result[0]

            emotions = result.get("emotion")
            dominant = result.get("dominant_emotion")

            if emotions is None:
                return None, None

            # normalize về 0-1
            probs = {k: v / 100.0 for k, v in emotions.items()}
            return probs, dominant

        except Exception:
            # DeepFace lỗi (shape, không đọc được, v.v.) -> bỏ frame
            return None, None
