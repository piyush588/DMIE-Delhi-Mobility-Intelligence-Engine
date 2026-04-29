from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import datetime

class RouteRequest(BaseModel):
    src: Tuple[float, float] = Field(..., description="[lat, lon] of source")
    dest: Tuple[float, float] = Field(..., description="[lat, lon] of destination")
    time: Optional[datetime] = Field(default_factory=datetime.now)

class RouteSegment(BaseModel):
    mode: str
    from_loc: str
    to_loc: str
    distance_km: float
    duration_min: float
    cost: float
    line: Optional[str] = None
    color: Optional[str] = None

class RouteOption(BaseModel):
    mode: str
    is_multimodal: bool = False
    segments: List[RouteSegment] = []
    time: float = Field(..., description="Total time in minutes")
    cost: float = Field(..., description="Total cost in INR")
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

class IsochroneRequest(BaseModel):
    lat: float
    lng: float
    minutes: int
