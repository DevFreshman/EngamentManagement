import cv2

class VideoSource:
    def __init__(self, mode, path):
        self.mode = mode
        self.path = path
        self.cap = None

    def open(self):
        if self.mode == "webcam":
            self.cap = cv2.VideoCapture(0)
        else:
            self.cap = cv2.VideoCapture(self.path)

    def read_frame(self):
        if not self.cap:
            return False, None
        return self.cap.read()

    def release(self):
        if self.cap:
            self.cap.release()
