import matplotlib
matplotlib.use("Agg")  # FIX lỗi Tkinter khi chạy trong server

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def create_charts(session_id):
    log_path = f"output/logs/{session_id}.csv"
    out_dir = f"output/reports/{session_id}/"
    ensure_dir(out_dir)

    df = pd.read_csv(log_path)

    if df.empty:
        return {"emotion_pie": None, "engagement_line": None}

    # Pie chart
    plt.figure(figsize=(6, 6))
    df["emotion"].value_counts().plot.pie(autopct="%1.1f%%")
    plt.title("Emotion Distribution")
    pie_path = os.path.join(out_dir, "emotion_pie.png")
    plt.savefig(pie_path)
    plt.close()

    # Line chart
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=df["eng_smooth"])
    plt.title("Engagement Over Time")
    plt.ylabel("Engagement")
    plt.xlabel("Frame Index")
    line_path = os.path.join(out_dir, "engagement_line.png")
    plt.savefig(line_path)
    plt.close()

    return {"emotion_pie": pie_path, "engagement_line": line_path}
