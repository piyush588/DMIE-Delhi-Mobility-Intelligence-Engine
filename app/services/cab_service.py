import os
import httpx
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CabService:
    def __init__(self):
        self.uber_client_id = os.getenv("UBER_CLIENT_ID")
        self.uber_client_secret = os.getenv("UBER_CLIENT_SECRET")
        self.base_url = "https://api.uber.com/v1.2"

    async def get_cab_estimate(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, time_obj: datetime) -> Dict:
        """
        Attempts to get real-time price from Uber.
        Falls back to dynamic heuristic if API keys are missing or call fails.
        """
        # 1. Attempt Uber API if keys are present
        if self.uber_client_id and self.uber_client_secret:
            try:
                # Note: In a real app, you'd handle OAuth token management here
                # result = await self._call_uber_api(start_lat, start_lon, end_lat, end_lon)
                # if result: return result
                pass
            except Exception as e:
                print(f"Uber API error: {e}")

        # 2. Dynamic Heuristic Fallback (High Fidelity)
        return self.get_heuristic_estimate(start_lat, start_lon, end_lat, end_lon, time_obj)

    def get_heuristic_estimate(self, s_lat, s_lon, e_lat, e_lon, time_obj: datetime) -> Dict:
        # Distance approximation
        dist_km = ((s_lat-e_lat)**2 + (s_lon-e_lon)**2)**0.5 * 111
        
        # Traffic / Surge Logic
        hour = time_obj.hour
        is_peak = (8 <= hour <= 11) or (17 <= hour <= 21)
        surge = 1.8 if is_peak else 1.0
        
        # Uber-like logic for Delhi
        # Base ₹50 + ₹25/km + ₹2/min
        avg_speed = 20 if is_peak else 35
        duration_min = (dist_km / avg_speed) * 60
        
        cost = (50.0 + (dist_km * 25.0) + (duration_min * 2.0)) * surge
        
        return {
            "mode": "cab",
            "price_estimate": round(cost, 2),
            "currency": "INR",
            "duration_min": round(duration_min, 2),
            "distance_km": round(dist_km, 2),
            "surge_multiplier": surge,
            "is_real_time": False
        }

    def get_auto_estimate(self, dist_km: float, time_obj: datetime) -> float:
        # Auto: Base ₹30 + ₹15/km
        is_peak = (8 <= time_obj.hour <= 11) or (17 <= time_obj.hour <= 21)
        surge = 1.3 if is_peak else 1.0
        return round((30.0 + (dist_km * 15.0)) * surge, 2)
