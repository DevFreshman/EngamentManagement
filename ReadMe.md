
# Student Engagement Analysis System

## Overview
The **Student Engagement Analysis System** is an intelligent application designed to analyze student engagement levels in real time using computer vision and deep learning techniques.  
The system captures video from a webcam, detects faces, recognizes emotions, and computes engagement scores based on emotional states over time.

This project supports educational research, online learning platforms, and classroom analytics by providing objective engagement insights.

---

## Objectives
- Detect student faces from a live camera feed
- Recognize facial emotions in real time
- Calculate engagement levels based on emotional weights
- Smooth engagement scores to reduce noise
- Store session data for post-analysis
- Generate visual reports and engagement statistics

---

## System Architecture
The system follows a modular pipeline-based architecture:

Camera Input  
→ Face Detection  
→ Emotion Recognition  
→ Engagement Scoring  
→ Smoothing & Aggregation  
→ Session Storage  
→ Visualization & Report Generation  

---

## Technologies Used

### Backend
- Python 3.10+
- FastAPI
- OpenCV
- NumPy
- Threading

### Machine Learning
- CNN-based Emotion Recognition Model
- Facial image preprocessing (48×48 grayscale)
- Emotion-to-engagement weighted mapping

### Frontend
- HTML, CSS, JavaScript
- Live camera preview
- Emotion and engagement label overlay

---

## Project Structure

```

StudentEngagementAnalysisM/
│
├── backend/
│   ├── pipeline/
│   │   └── engagement_pipeline.py
│   ├── models/
│   │   ├── face_detector.py
│   │   └── emotion_model.py
│   ├── analysis/
│   │   ├── report_generator.py
│   │   └── visualization.py
│   ├── storage/
│   │   └── session_manager.py
│   └── core/
│       └── config.py
│
├── frontend/
│   └── index.html
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore

```

---

## Engagement Calculation
Each detected emotion is mapped to an engagement weight:

| Emotion   | Engagement Level |
|----------|------------------|
| Happy    | High             |
| Neutral  | Medium           |
| Sad      | Low              |
| Angry   | Very Low         |
| Surprise | Medium–High      |

The system computes:
- Raw engagement score from emotion weights
- Smoothed engagement score using moving average

---

## How to Run the Project

### 1. Clone the repository
```

git clone [https://github.com/DevFreshman/EngamentManagement.git](https://github.com/DevFreshman/EngamentManagement.git)
cd EngamentManagement

```

### 2. Create and activate virtual environment
```

python -m venv venv
venv\Scripts\activate

```

### 3. Install dependencies
```

pip install -r requirements.txt

```

### 4. Start the backend server
```

uvicorn backend.app:app --reload

```

### 5. Access the application
- API documentation: http://127.0.0.1:8000/docs
- Frontend UI: open frontend/index.html

---

## Output and Reports
The system generates:
- Timestamped emotion logs
- Raw and smoothed engagement values
- Engagement charts
- Session summary reports

These outputs help analyze attention trends and emotional changes during learning sessions.

---


## Author
Student Name: Hoàng Đức Mạnh
Major: Computer Science / Information Technology  
University: Your University  
Academic Year: 2024–2025

---

## License
This project is developed for academic and research purposes only.