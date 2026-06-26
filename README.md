<div align="center">
  <h1>♻️ VisionSort</h1>
  <p><strong>AI-Powered Waste Segregation System</strong></p>
  <p>🔴 <strong><a href="https://visionsort.onrender.com">View Live Demo</a></strong> 🔴</p>
  
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com/)
  [![Ultralytics YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)](https://github.com/ultralytics/ultralytics)
  [![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248.svg)](https://www.mongodb.com/)
</div>

<hr/>

## 📖 About The Project

Material recycling centers suffer from incredibly high contamination rates because manual sorting fails to segregate plastics, metals, paper, glass, and biological waste rapidly and accurately. 

**VisionSort** is a full-stack, end-to-end prototype designed to solve this problem. It simulates a conveyor belt camera on a sorting line, dynamically classifying waste items in real-time to drastically reduce contamination and improve recycling efficiency.

### 🌟 Key Features
- **Real-Time AI Inference:** Utilizes a custom fine-tuned YOLOv8 classification model to rapidly identify trash categories.
- **Factory Dashboard:** A sleek, industrial-themed dark-mode UI (built without frameworks) featuring dynamic live feeds and analytics.
- **Contamination Alerts:** Automatically triggers flashing visual fault warnings if an item is classified with a low confidence score (< 60%).
- **Automated Data Pipeline:** Built-in Python script to automatically download, extract, and split the TrashNet dataset for seamless model retraining.
- **Resilient Backend:** Built with FastAPI and Async Motor. If a MongoDB daemon isn't running locally, the API silently falls back to an in-memory database to keep the demo alive.

---

## 🛠 Tech Stack

- **Machine Learning**: `PyTorch`, `Ultralytics (YOLOv8-cls)`
- **Backend**: `Python`, `FastAPI`, `Uvicorn`
- **Database**: `MongoDB`, `Motor` (Async)
- **Frontend**: `Vanilla HTML5`, `CSS Grid`, `JavaScript`, `Chart.js`

---

## 📂 Project Structure

```text
VISIONSORT/
├── data/                  # Auto-generated: Stores raw & processed TrashNet datasets
├── ml/                    
│   ├── train.py           # Auto-downloads dataset and fine-tunes YOLOv8
│   ├── infer.py           # ML inference engine loading the trained weights
│   └── classes.yaml       # Defines the 6 waste classes
├── backend/               
│   ├── main.py            # FastAPI application entrypoint
│   ├── routes.py          # API Endpoints (/predict, /stats, /recent)
│   ├── db.py              # MongoDB async connection & in-memory fallback
│   └── schemas.py         # Pydantic validation models
├── frontend/              
│   ├── index.html         # Dashboard Layout
│   ├── style.css          # Industrial dark-mode styling
│   └── script.js          # API consumption and Chart.js logic
├── requirements.txt       # Pinned dependency file
└── .env                   # Configuration variables
```

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### 1. Prerequisites
Ensure you have `Python 3.9+` installed. *(Optional: A local MongoDB instance running on port 27017 for data persistence).*

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/ARTHIKMIT/VisionSort.git
cd VisionSort
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Model Training (Optional)
If you wish to retrain the model from scratch on the TrashNet dataset, simply run the training script. It handles dataset downloading and splitting automatically:
```bash
python ml/train.py
```
*(If skipped, the backend will safely fallback to a lightweight, pretrained `yolov8n-cls` generic model for demonstration purposes).*

### 4. Start the Application
Run the backend server as a Python module:
```bash
python -m backend.main
```
Navigate to **http://localhost:8000** in your browser to interact with the VisionSort Control Panel.

---

## 🧠 AI Architecture Decisions

**Why YOLOv8 Classification instead of Object Detection?**
In an industrial sorting line setting, cameras are typically positioned over segments of a conveyor belt, capturing items isolated by optical sorters or physical separators. Because the stream processes one item per frame (simulated by the TrashNet dataset), an Image Classification head is significantly lighter, trains orders of magnitude faster, and consumes heavily reduced VRAM compared to a bounding-box Object Detection model—achieving identical segregation outcomes.

---

<div align="center">
  <i>Developed for academic research and demonstration purposes.</i>
</div>
