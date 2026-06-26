import os
import shutil
import random
import urllib.request
from pathlib import Path
from ultralytics import YOLO

# Configuration
DATA_DIR = Path("../data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# TrashNet dataset Hugging Face URL
TRASHNET_URL = "https://huggingface.co/datasets/garythung/trashnet/resolve/main/dataset-resized.zip"

CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

def download_and_extract():
    """Downloads the TrashNet dataset if not already present."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "dataset-resized.zip"
    
    if not zip_path.exists():
        print("Downloading dataset from Hugging Face (this may take a minute)...")
        urllib.request.urlretrieve(TRASHNET_URL, str(zip_path))
        print("Download complete.")
        
    extracted_dir = RAW_DIR / "dataset-resized"
    if not extracted_dir.exists():
        print("Extracting dataset...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DIR)
            
    return extracted_dir

def split_dataset(source_dir):
    """Splits the dataset into 80/10/10 train/val/test splits."""
    if PROCESSED_DIR.exists():
        print("Processed dataset already exists. Skipping split.")
        return
        
    print("Splitting dataset into train/val/test...")
    for split in ["train", "val", "test"]:
        for cls in CLASSES:
            (PROCESSED_DIR / split / cls).mkdir(parents=True, exist_ok=True)
            
    for cls in CLASSES:
        cls_dir = source_dir / cls
        if not cls_dir.exists():
            continue
            
        images = list(cls_dir.glob("*.jpg"))
        random.shuffle(images)
        
        n = len(images)
        train_end = int(0.8 * n)
        val_end = int(0.9 * n)
        
        train_imgs = images[:train_end]
        val_imgs = images[train_end:val_end]
        test_imgs = images[val_end:]
        
        for img in train_imgs:
            shutil.copy(img, PROCESSED_DIR / "train" / cls / img.name)
        for img in val_imgs:
            shutil.copy(img, PROCESSED_DIR / "val" / cls / img.name)
        for img in test_imgs:
            shutil.copy(img, PROCESSED_DIR / "test" / cls / img.name)
            
    print("Dataset splitting complete.")

def train_model():
    """Trains the YOLOv8 classification model."""
    print("Initializing YOLOv8-cls model...")
    # Load a pretrained YOLOv8 classification model (nano size for fast training & lower VRAM usage)
    model = YOLO("yolov8n-cls.pt")
    
    print("Starting training...")
    # Train the model
    # imgsz=224 is standard for classification, batch=16 fits easily in 4GB VRAM
    results = model.train(
        data=str(PROCESSED_DIR.absolute()), 
        epochs=10, # Keep it short for demo purposes
        imgsz=224, 
        batch=16,
        project="runs",
        name="visionsort_cls"
    )
    
    print("Training complete!")
    
    # Copy the best model to the ml directory
    best_weights = Path("runs/visionsort_cls/weights/best.pt")
    if best_weights.exists():
        shutil.copy(best_weights, "best.pt")
        print("Saved best.pt to ml directory.")
        
    print("Confusion matrix is saved in runs/visionsort_cls/confusion_matrix.png")

if __name__ == "__main__":
    random.seed(42)
    # Ensure working directory is the ml folder
    os.chdir(Path(__file__).parent)
    
    source_dir = download_and_extract()
    split_dataset(source_dir)
    train_model()
