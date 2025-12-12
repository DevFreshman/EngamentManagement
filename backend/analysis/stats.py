import pandas as pd

def compute_stats(log_path):
    df = pd.read_csv(log_path)
    return {
        "avg": float(df["eng_smooth"].mean()),
        "max": float(df["eng_smooth"].max()),
        "min": float(df["eng_smooth"].min()),
        "emotion_distribution": df["emotion"].value_counts().to_dict()
    }
