from backend.core.config import SMOOTHING_ALPHA

class EngagementSmoother:
    def __init__(self):
        self.value = 0.0

    def update(self, x):
        self.value = SMOOTHING_ALPHA * x + (1 - SMOOTHING_ALPHA) * self.value
        return self.value
