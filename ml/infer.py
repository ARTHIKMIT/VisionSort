from pathlib import Path
from ultralytics import YOLO
import json

# Ensure we're relative to this file
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "best.pt"

# Initialize model variable globally
_model = None

def get_model():
    """Lazy load the YOLOv8 model."""
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            # Fallback to pretrained nano if best.pt doesn't exist for demo to not fail immediately
            print(f"Warning: {MODEL_PATH} not found. Using pretrained yolov8n-cls.pt.")
            _model = YOLO("yolov8n-cls.pt")
        else:
            _model = YOLO(str(MODEL_PATH))
    return _model

def predict(image_path_or_pil):
    """
    Runs inference on an image using the trained YOLOv8 model.
    Returns the predicted class name and confidence score.
    """
    model = get_model()
    
    # Run prediction (returns a list of Results objects)
    results = model.predict(image_path_or_pil, verbose=False)
    
    if not results:
        return {"class": "unknown", "confidence": 0.0}
        
    result = results[0]
    
    # Get top 1 prediction
    top1_index = result.probs.top1
    confidence = float(result.probs.top1conf)
    
    # Map index to class name
    class_name = result.names[top1_index]
    
    return {
        "class": class_name,
        "confidence": confidence
    }

if __name__ == "__main__":
    # Test script if run directly
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print(json.dumps(predict(img_path), indent=2))
    else:
        print("Usage: python infer.py <path_to_image>")
