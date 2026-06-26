from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PredictionResponse(BaseModel):
    predicted_class: str
    confidence_score: float
    timestamp: datetime
    image_reference: Optional[str] = None
    
class StatsResponse(BaseModel):
    total_processed: int
    class_counts: dict
    average_confidence: float
    
class RecentPrediction(BaseModel):
    id: str
    predicted_class: str
    confidence_score: float
    timestamp: datetime
    
class RecentFeedResponse(BaseModel):
    recent: List[RecentPrediction]
