import json
import math
from typing import List, Dict, Optional

class MetroService:
    def __init__(self, data_path: str = "data/metro.json"):
        self.stations = []
        try:
            with open(data_path, "r") as f:
                self.stations = json.load(f)
        except Exception as e:
            print(f"Error loading metro data: {e}")

    def get_nearest_station(self, lat: float, lon: float, threshold_meters: float = 800) -> Optional[Dict]:
        """
        Finds the nearest metro station to a given coordinate.
        Uses Haversine formula for distance.
        """
        nearest = None
        min_dist = float('inf')

        for station in self.stations:
            s_lat = station["details"]["latitude"]
            s_lon = station["details"]["longitude"]
            
            dist = self.haversine(lat, lon, s_lat, s_lon)
            if dist < min_dist:
                min_dist = dist
                nearest = {
                    "name": station["name"],
                    "distance_m": dist,
                    "line": station["details"]["line"],
                    "coords": [s_lat, s_lon]
                }

        if nearest and nearest["distance_m"] <= threshold_meters:
            return nearest
        return None

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
