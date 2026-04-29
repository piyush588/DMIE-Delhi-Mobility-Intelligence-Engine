from fastapi import APIRouter, HTTPException
from models.schemas import RouteRequest, RecommendationResponse, IsochroneRequest
from app.core.decision_engine import DecisionEngine
from app.services.routing_service import RoutingService

router = APIRouter()
engine = DecisionEngine()
routing_service = RoutingService()

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_route(request: RouteRequest):
    try:
        recommendation = await engine.get_recommendation(request)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/isochrone")
async def get_isochrone(request: IsochroneRequest):
    try:
        isochrone_data = await routing_service.get_isochrone(request.lat, request.lng, request.minutes)
        return isochrone_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DMIE", "version": "1.0.0"}
