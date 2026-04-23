import os
import openrouteservice
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()

class RoutingService:
    def __init__(self):
        self.api_key = os.getenv("ORS_API_KEY")
        self.client = None
        if self.api_key:
            self.client = openrouteservice.Client(key=self.api_key)
        else:
            print("Warning: No ORS_API_KEY found. Running in MOCK MODE.")

    def get_route_stats(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float], mode: str) -> Dict:
        """
        Fetches distance and duration for a given mode.
        start_coords/end_coords are (lat, lon).
        ORS expects (lon, lat).
        """
        if not self.client:
            return self._mock_route(start_coords, end_coords, mode)

        # Convert (lat, lon) to (lon, lat) for ORS
        coords = ((start_coords[1], start_coords[0]), (end_coords[1], end_coords[0]))
        
        profile = self._get_profile(mode)
        
        try:
            routes = self.client.directions(coordinates=coords, profile=profile)
            summary = routes['routes'][0]['summary']
            return {
                "distance_km": round(summary['distance'] / 1000, 2),
                "duration_min": round(summary['duration'] / 60, 2),
                "mode": mode
            }
        except Exception as e:
            print(f"Routing error for {mode}: {e}")
            return self._mock_route(start_coords, end_coords, mode)

    def _get_profile(self, mode: str) -> str:
        mapping = {
            "cab": "driving-car",
            "car": "driving-car",
            "auto": "driving-car", # Approximation
            "walk": "foot-walking",
            "cycle": "cycling-regular"
        }
        return mapping.get(mode.lower(), "driving-car")

    def _mock_route(self, start, end, mode) -> Dict:
        # Very basic distance approximation: approx 111km per degree
        dist = ((start[0]-end[0])**2 + (start[1]-end[1])**2)**0.5 * 111
        
        speeds = {
            "cab": 25, # km/h
            "auto": 20,
            "walk": 5,
            "metro": 35
        }
        speed = speeds.get(mode.lower(), 20)
        duration = (dist / speed) * 60
        
        return {
            "distance_km": round(dist, 2),
            "duration_min": round(duration, 2),
            "mode": mode,
            "is_mock": True
        }
