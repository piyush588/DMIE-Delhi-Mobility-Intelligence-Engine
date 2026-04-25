import pytest
from app.core.decision_engine import DecisionEngine
from models.schemas import RouteRequest
from datetime import datetime

@pytest.fixture
def engine():
    return DecisionEngine()

@pytest.mark.asyncio
async def test_ncr_multimodal(engine):
    # Delhi Gate to Gurugram (NCR Multi-modal)
    request = RouteRequest(
        src=(28.64, 77.24),  # Delhi Gate Area
        dest=(28.45, 77.02), # Gurgaon Area
        time=datetime(2026, 4, 24, 18, 0)
    )
    
    res = await engine.get_recommendation(request)
    
    assert res.best_mode == "metro"
    assert len(res.options) > 0
    print(f"✅ NCR Multi-modal Passed: {res.best_mode}")

@pytest.mark.asyncio
async def test_short_trip(engine):
    # Short trip (CP to Janpath) - Should use tiered heuristic path
    request = RouteRequest(
        src=(28.6289, 77.2190),
        dest=(28.6250, 77.2210),
        time=datetime(2026, 4, 24, 12, 0)
    )
    
    res = await engine.get_recommendation(request)
    assert res.best_mode in ["walk", "auto", "cab"]
    print(f"✅ Short Trip Passed: {res.best_mode}")
