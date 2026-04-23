from app.core.decision_engine import DecisionEngine
from models.schemas import RouteRequest
from datetime import datetime
import json

def test_recommendation():
    engine = DecisionEngine()
    
    # Example: Karol Bagh (28.64, 77.19) to Saket (28.52, 77.21)
    request = RouteRequest(
        src=(28.6440, 77.1885), # Karol Bagh Metro
        dest=(28.5279, 77.2056), # Malviya Nagar (near Saket)
        time=datetime(2026, 4, 24, 18, 0) # Peak Hour (6 PM)
    )
    
    print(f"Testing Peak Hour Recommendation (18:00)...")
    res = engine.get_recommendation(request)
    
    print(f"\nBest Mode: {res.best_mode}")
    print(f"Explanation: {res.explanation}")
    print("\nAll Options:")
    for opt in res.options:
        print(f"- {opt.mode}: Score {opt.score}, Time {opt.time}m, Cost ₹{opt.cost}")

    # Test Non-Peak
    request.time = datetime(2026, 4, 24, 14, 0) # 2 PM
    print(f"\nTesting Non-Peak Recommendation (14:00)...")
    res_off = engine.get_recommendation(request)
    print(f"Best Mode: {res_off.best_mode}")
    for opt in res_off.options:
        print(f"- {opt.mode}: Score {opt.score}, Time {opt.time}m, Cost ₹{opt.cost}")

if __name__ == "__main__":
    test_recommendation()
