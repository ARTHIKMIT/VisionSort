from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime, timezone
import io
import uuid
import os
from PIL import Image

# Import ML inference function
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from ml.infer import predict

# Import DB and Schemas
from backend.db import get_database
from backend.schemas import PredictionResponse, StatsResponse, RecentFeedResponse, RecentPrediction

router = APIRouter()

# In-memory fallback if MongoDB is not available
_in_memory_records = []

@router.post("/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image, runs YOLOv8 classification,
    and stores the result in MongoDB.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
        
    try:
        # Read image to memory
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Run ML Inference
        result = predict(image)
        
        # Prepare record
        predicted_class = result["class"]
        confidence_score = result["confidence"]
        timestamp = datetime.now(timezone.utc)
        image_ref = f"{uuid.uuid4()}_{file.filename}"
        
        record = {
            "predicted_class": predicted_class,
            "confidence_score": confidence_score,
            "timestamp": timestamp,
            "image_reference": image_ref
        }
        
        # Save to DB or in-memory fallback
        db = get_database()
        if db is not None:
            await db.predictions.insert_one(record.copy())
        else:
            # Fallback to in-memory
            record["_id"] = str(uuid.uuid4())
            _in_memory_records.append(record)
            
        return PredictionResponse(
            predicted_class=predicted_class,
            confidence_score=confidence_score,
            timestamp=timestamp,
            image_reference=image_ref
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Returns aggregated counts per class and average confidence."""
    db = get_database()
    
    if db is not None:
        pipeline = [
            {"$group": {
                "_id": "$predicted_class",
                "count": {"$sum": 1},
                "avg_conf": {"$avg": "$confidence_score"}
            }}
        ]
        
        results = await db.predictions.aggregate(pipeline).to_list(None)
        
        total = sum(r["count"] for r in results)
        class_counts = {r["_id"]: r["count"] for r in results}
        
        # Weighted average confidence
        if total > 0:
            avg_conf = sum(r["avg_conf"] * (r["count"] / total) for r in results)
        else:
            avg_conf = 0.0
            
    else:
        # In-memory fallback
        total = len(_in_memory_records)
        class_counts = {}
        total_conf = 0
        for r in _in_memory_records:
            cls = r["predicted_class"]
            class_counts[cls] = class_counts.get(cls, 0) + 1
            total_conf += r["confidence_score"]
        
        avg_conf = (total_conf / total) if total > 0 else 0.0

    return StatsResponse(
        total_processed=total,
        class_counts=class_counts,
        average_confidence=avg_conf
    )

@router.get("/recent", response_model=RecentFeedResponse)
async def get_recent():
    """Returns last 20 classification events for the live feed."""
    db = get_database()
    
    recent_items = []
    
    if db is not None:
        cursor = db.predictions.find().sort("timestamp", -1).limit(20)
        async for doc in cursor:
            recent_items.append(RecentPrediction(
                id=str(doc["_id"]),
                predicted_class=doc["predicted_class"],
                confidence_score=doc["confidence_score"],
                timestamp=doc["timestamp"]
            ))
    else:
        # In-memory fallback
        recent = sorted(_in_memory_records, key=lambda x: x["timestamp"], reverse=True)[:20]
        for doc in recent:
            recent_items.append(RecentPrediction(
                id=str(doc["_id"]),
                predicted_class=doc["predicted_class"],
                confidence_score=doc["confidence_score"],
                timestamp=doc["timestamp"]
            ))
            
    return RecentFeedResponse(recent=recent_items)
