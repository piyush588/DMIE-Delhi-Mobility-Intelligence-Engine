
import sys
import os
import asyncio
from datetime import datetime

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.decision_engine import DecisionEngine
from models.schemas import RouteRequest
from app.services.metro_service import MetroService

async def debug():
    # Use absolute path for metro data
    metro_data_path = "/Users/piyush/Desktop/routing_engine/smart-route-india/data/metro.json"
    engine = DecisionEngine()
    engine.metro = MetroService(data_path=metro_data_path)
    
    # New Delhi to Cyber Hub
    src = [28.64307, 77.22144] # NDLS (Exact from metro.json)
    dest = [28.4951, 77.0886] # IndusInd Bank Cyber City (Rapid Metro)
    
    req = RouteRequest(src=src, dest=dest, time=datetime.now())
    
    res = await engine.get_recommendation(req)
    
    print(f"Best Mode: {res.best_mode}")
    print(f"Explanation: {res.explanation}")
    print("\nOptions:")
    for opt in res.options:
        print(f"- {opt.mode}: Score={opt.score}, Time={opt.time}m, Cost=Rs.{opt.cost}")
        if opt.is_multimodal:
            for seg in opt.segments:
                print(f"  > {seg.mode}: {seg.from_loc} -> {seg.to_loc}")

if __name__ == "__main__":
    asyncio.run(debug())
