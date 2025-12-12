import csv

class LogWriter:
    def __init__(self, path):
        self.f = open(path, "w", newline="")
        self.writer = csv.writer(self.f)
        self.writer.writerow(["timestamp", "emotion", "eng_raw", "eng_smooth"])

    def write(self, ts, emo, raw, smooth):
        self.writer.writerow([ts, emo, raw, smooth])

    def close(self):
        self.f.close()
