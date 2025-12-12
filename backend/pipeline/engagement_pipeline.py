import time
from backend.pipeline.video_source import VideoSource
from backend.pipeline.frame_processor import process_frame
from backend.models.face_detector import FaceDetector
from backend.models.emotion_model import EmotionModel
from backend.analysis.smoothing import EngagementSmoother
from backend.storage.log_writer import LogWriter
from backend.utils.file_utils import ensure_dir

class EngagementPipeline:

    def __init__(self):
        self.running = False
        self.current_session = None
        self.source = None
        self.log = None

        self.face_detector = FaceDetector()
        self.emotion_model = EmotionModel()
        self.smoother = EngagementSmoother()

    def start(self, session_id, mode, video_path):
        self.current_session = session_id

        # create needed folders
        ensure_dir("output/")
        ensure_dir("output/logs/")

        # init video source
        self.source = VideoSource(mode, video_path)
        self.source.open()

        # init log file
        self.log = LogWriter(f"output/logs/{session_id}.csv")

        # allow loop() to run
        self.running = True

    def stop(self):
        """Stop the loop safely without closing file immediately."""
        self.running = False  # tell loop() to stop

    def loop(self):
        """Main processing loop (running inside a thread)."""
        while self.running:
            ret, frame = self.source.read_frame()

            if not ret:
                break

            data = process_frame(frame, self.face_detector, self.emotion_model, self.smoother)
            if data:
                try:
                    self.log.write(
                        time.time(),
                        data["dominant"],
                        data["eng_raw"],
                        data["eng_smooth"]
                    )
                except ValueError:
                    # file already closed
                    break

        # only close resources AFTER loop finishes
        if self.source:
            self.source.release()

        if self.log:
            try:
                self.log.close()
            except:
                pass
