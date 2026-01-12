import cv2
from models.emotion_model import EmotionModel

model = EmotionModel()

img = cv2.imread("../happy.jpg")  # ảnh test
probs, dom = model.predict(img)

print("dominant:", dom)
print("probs:", probs)
