from fastapi import APIRouter, HTTPException
from models.schemas import RouteRequest, RecommendationResponse
from app.core.decision_engine import DecisionEngine

router = APIRouter()
engine = DecisionEngine()

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_route(request: RouteRequest):
    try:
        recommendation = await engine.get_recommendation(request)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DMIE", "version": "1.0.0"}
