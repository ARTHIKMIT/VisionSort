# VisionSort

AI-Powered Waste Segregation System, designed to classify waste items on a simulated conveyor belt to reduce contamination rates in material recycling centers.

## Architecture

This project is built with the following stack:
- **AI/ML**: Ultralytics YOLOv8 (classification mode) backed by PyTorch. 
  - *Why Classification?* We assume a sorting line where a camera captures a single centered item cropped out of a stream. This makes the pipeline faster and perfectly aligns with datasets like TrashNet.
- **Backend**: FastAPI with async Motor (MongoDB driver) handling API requests.
- **Frontend**: Vanilla HTML/CSS/JS with a responsive CSS grid, adhering to an industrial dark-mode aesthetic.
- **Database**: MongoDB for persistent logging of sorting events. In-memory fallback is provided if MongoDB is unavailable.

## Project Structure
```
VISIONSORT/
├── data/                  # Contains raw and processed TrashNet dataset
├── notebooks/             # Jupyter notebook for YOLO training exploration
├── ml/                    # Training and inference scripts
├── backend/               # FastAPI backend and DB modules
├── frontend/              # HTML/CSS/JS dashboard files
├── requirements.txt       # Python dependencies
├── .env                   # Configuration file
└── README.md              # This file
```

## Setup & Running the Application

### 1. Prerequisites
- Python 3.9+
- MongoDB running locally (default `mongodb://localhost:27017`). If it fails, the app uses in-memory mode.
- Optional: CUDA-enabled GPU (RTX 3050 supported for training with small batch sizes).

### 2. Environment Setup
```bash
cd VISIONSORT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Data Prep & Model Training (Optional)
If you just want to run the app, the inference script falls back to a pretrained nano model if `best.pt` is not found. To train a custom model on the TrashNet dataset:
```bash
python ml/train.py
```
This script will:
1. Download the dataset from Google Drive.
2. Extract and split it into Train/Val/Test directories.
3. Train YOLOv8-cls for 10 epochs.
4. Output `best.pt` to the `ml/` directory.

### 4. Start the Application
Start the FastAPI server:
```bash
python backend/main.py
```
The server will start on `http://localhost:8000`.

### 5. Open the Dashboard
Navigate to [http://localhost:8000](http://localhost:8000) in your web browser. 

You can interact with the live "camera feed" panel by clicking it and uploading images of trash to simulate the conveyor belt camera.

### Features
- **Real-time Inference**: Drag and drop images to see instant classification results.
- **Fault Detection**: The UI flashes red if a prediction confidence is < 60%.
- **Live Feed & Stats**: A historical feed of classifications and a live Chart.js summary.
