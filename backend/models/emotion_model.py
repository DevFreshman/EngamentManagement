import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F

from .model_emotion import SimpleCNN
from .emotion_labels import EMOTION_LABELS


class EmotionModel:
    """
    predict(face_img) -> (probs_dict, dominant_label)
    """

    def __init__(self, weight_name="best_cnn.pt", device=None):
        self.labels = EMOTION_LABELS
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        weight_path = os.path.join(os.path.dirname(__file__), weight_name)

        # init model
        self.model = SimpleCNN(num_class=len(self.labels)).to(self.device).eval()

        ckpt = torch.load(weight_path, map_location=self.device)

        # resolve checkpoint format
        if isinstance(ckpt, dict):
            if "model_state_dict" in ckpt:
                state = ckpt["model_state_dict"]
            elif "state_dict" in ckpt:
                state = ckpt["state_dict"]
            elif "model" in ckpt:
                state = ckpt["model"]
            else:
                raise ValueError(f"Checkpoint keys không hợp lệ: {ckpt.keys()}")

            if hasattr(state, "state_dict"):
                self.model = state.to(self.device).eval()
            else:
                if any(k.startswith("module.") for k in state):
                    state = {k.replace("module.", "", 1): v for k, v in state.items()}
                self.model.load_state_dict(state, strict=True)

        elif hasattr(ckpt, "state_dict"):
            self.model = ckpt.to(self.device).eval()

        else:
            raise ValueError("Không nhận dạng được format best_cnn.pt")

        # bảo vệ: số label phải khớp output
        assert len(self.labels) == self.model.fc[-1].out_features

    @torch.inference_mode()
    def predict(self, face_img):
        try:
            x = self._preprocess(face_img).to(self.device)
            logits = self.model(x)
            probs_t = F.softmax(logits, dim=1)[0]

            probs = {self.labels[i]: float(probs_t[i]) for i in range(len(self.labels))}
            dominant = max(probs, key=probs.get)
            return probs, dominant

        except Exception as e:
            print("[EmotionModel error]", e)
            return None, None

    def _preprocess(self, img):
        if img is None:
            raise ValueError("face_img is None")

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))

        return torch.from_numpy(img).unsqueeze(0)
