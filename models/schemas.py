from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import datetime

class RouteRequest(BaseModel):
    src: Tuple[float, float] = Field(..., description="[lat, lon] of source")
    dest: Tuple[float, float] = Field(..., description="[lat, lon] of destination")
    time: Optional[datetime] = Field(default_factory=datetime.now)

class RouteOption(BaseModel):
    mode: str
    time: float = Field(..., description="Time in minutes")
    cost: float = Field(..., description="Cost in INR")
    score: float
    confidence: float = 0.8
    distance_km: float

class MetroStation(BaseModel):
    name: str
    distance_m: float
    line: List[str]
    coords: List[float]

class RecommendationResponse(BaseModel):
    best_mode: str
    confidence: float
    explanation: str
    nearest_metro_src: Optional[MetroStation] = None
    nearest_metro_dest: Optional[MetroStation] = None
    options: List[RouteOption]
