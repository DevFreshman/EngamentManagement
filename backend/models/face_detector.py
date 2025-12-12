from mtcnn import MTCNN

class FaceDetector:
    def __init__(self):
        self.detector = MTCNN()

    def detect(self, frame):
        try:
            faces = self.detector.detect_faces(frame)
        except Exception:
            # nếu MTCNN lỗi thì coi như không có mặt
            return []

        boxes = []
        for f in faces:
            x, y, w, h = f.get("box", (0, 0, 0, 0))

            # bỏ những box lỗi / size âm
            if w <= 0 or h <= 0:
                continue

            boxes.append((x, y, w, h))

        return boxes
