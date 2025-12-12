import time

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, mode, video_path):
        session_id = str(int(time.time()))
        self.sessions[session_id] = {
            "mode": mode,
            "video_path": video_path,
            "active": True
        }
        return session_id

    def stop_session(self, session_id):
        if session_id in self.sessions:
            self.sessions[session_id]["active"] = False
