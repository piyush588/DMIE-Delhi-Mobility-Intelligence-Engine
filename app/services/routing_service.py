import os
import httpx
import json
from typing import Dict, Tuple, Optional, List
from dotenv import load_dotenv

load_dotenv()

class RoutingService:
    _client: Optional[httpx.AsyncClient] = None

    def __init__(self):
        self.api_key = os.getenv("ORS_API_KEY")
        # Updated default URL to the new heigit.org domain as per deprecation notice
        self.base_url = os.getenv("ORS_BASE_URL", "https://api.heigit.org")
        self._cache = {} 
        if not self.api_key:
            print("CRITICAL: No ORS_API_KEY found in environment!")

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(
                timeout=15.0, 
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=20)
            )
        return cls._client

    async def get_route_stats(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float], mode: str) -> Dict:
        if not self.api_key:
            return self._mock_route(start_coords, end_coords, mode)

        cache_key = (round(start_coords[0], 4), round(start_coords[1], 4), 
                     round(end_coords[0], 4), round(end_coords[1], 4), mode)
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        profile = self._get_profile(mode)
        url = f"{self.base_url}/v2/directions/{profile}"
        
        body = {
            "coordinates": [[start_coords[1], start_coords[0]], [end_coords[1], end_coords[0]]]
        }
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            client = self.get_client()
            response = await client.post(url, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            summary = data['routes'][0]['summary']
            result = {
                "distance_km": round(summary['distance'] / 1000, 2),
                "duration_min": round(summary['duration'] / 60, 2),
                "mode": mode
            }
            self._cache[cache_key] = result
            return result
        except Exception as e:
            print(f"Routing error: {e}")
            return self._mock_route(start_coords, end_coords, mode)

    async def get_isochrone(self, lat: float, lng: float, minutes: int) -> Dict:
        if not self.api_key:
            raise Exception("ORS_API_KEY is missing on the server")

        url = f"{self.base_url}/v2/isochrones/driving-car"
        
        body = {
            "locations": [[float(lng), float(lat)]],
            "range": [int(minutes) * 60],
            "range_type": "time",
            "attributes": ["total_pop"],
            "intersections": False
        }
        
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json; charset=utf-8"
        }

        try:
            client = self.get_client()
            response = await client.post(url, json=body, headers=headers)
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_detail = response.json()
                except:
                    pass
                print(f"ORS API Error ({response.status_code}): {error_detail}")
                raise Exception(f"ORS API failed with status {response.status_code}: {error_detail}")
                
            return response.json()
        except httpx.TimeoutException:
            print("ORS API Timeout")
            raise Exception("Connection to OpenRouteService timed out")
        except Exception as e:
            print(f"Internal Isochrone error: {str(e)}")
            raise e

    def _get_profile(self, mode: str) -> str:
        mapping = {
            "cab": "driving-car",
            "car": "driving-car",
            "auto": "driving-car",
            "walk": "foot-walking",
            "cycle": "cycling-regular"
        }
        return mapping.get(mode.lower(), "driving-car")

    def _mock_route(self, start, end, mode) -> Dict:
        dist = ((start[0]-end[0])**2 + (start[1]-end[1])**2)**0.5 * 111
        speeds = {"cab": 25, "auto": 20, "walk": 5, "metro": 35}
        speed = speeds.get(mode.lower(), 20)
        duration = (dist / speed) * 60
        return {
            "distance_km": round(dist, 2),
            "duration_min": round(duration, 2),
            "mode": mode,
            "is_mock": True
        }
