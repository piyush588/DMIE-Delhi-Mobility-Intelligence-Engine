import json
import math
import heapq
from typing import Dict, Optional, List, Tuple

class MetroService:
    def __init__(self, data_path: str = "data/metro.json"):
        self.stations = []
        self.graph = {}
        self.edges = {}
        try:
            with open(data_path, "r") as f:
                self.stations = json.load(f)
            self._build_graph()
        except Exception as e:
            print(f"Error loading metro data: {e}")

    def _build_graph(self):
        for s in self.stations:
            name = s["name"]
            self.graph[name] = {
                "coords": (s["details"]["latitude"], s["details"]["longitude"]),
                "lines": set(s["details"]["line"])
            }

        for name1, data1 in self.graph.items():
            self.edges[name1] = []
            for name2, data2 in self.graph.items():
                if name1 == name2: continue
                shared_lines = data1["lines"].intersection(data2["lines"])
                if shared_lines:
                    dist = self.haversine(data1["coords"][0], data1["coords"][1], data2["coords"][0], data2["coords"][1])
                    self.edges[name1].append((name2, dist, list(shared_lines)[0]))

    def get_nearest_station(self, lat: float, lon: float, threshold_meters: float = 800) -> Optional[Dict]:
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

    def get_metro_route(self, src_name: str, dest_name: str) -> Optional[List[Tuple[str, str, str]]]:
        """
        Returns a list of segments: [(start_station, end_station, line_name)]
        """
        if src_name not in self.graph or dest_name not in self.graph:
            return None

        q = [(0, src_name, [src_name], [])] # dist, current, path, lines_used
        visited = set()
        
        while q:
            dist, curr, path, lines_used = heapq.heappop(q)
            if curr == dest_name:
                segments = []
                if not lines_used:
                    return segments
                curr_line = lines_used[0]
                curr_start = path[0]
                for i in range(1, len(path)):
                    if lines_used[i-1] != curr_line:
                        segments.append((curr_start, path[i-1], curr_line))
                        curr_line = lines_used[i-1]
                        curr_start = path[i-1]
                segments.append((curr_start, path[-1], curr_line))
                return segments
                
            if curr in visited:
                continue
            visited.add(curr)
            
            for nxt, d, line in self.edges[curr]:
                if nxt not in visited:
                    penalty = 0
                    if lines_used and lines_used[-1] != line:
                        penalty = 5.0 # Penalty for interchange to minimize changing lines
                    heapq.heappush(q, (dist + d + penalty, nxt, path + [nxt], lines_used + [line]))
                    
        return None

    def get_line_color(self, line_name: str) -> str:
        colors = {
            "Yellow Line": "bg-yellow-400",
            "Blue Line": "bg-blue-500",
            "Blue Line branch": "bg-blue-400",
            "Red Line": "bg-red-500",
            "Green Line": "bg-green-500",
            "Violet Line": "bg-purple-500",
            "Pink Line": "bg-pink-500",
            "Magenta Line": "bg-fuchsia-600",
            "Grey Line": "bg-slate-400",
            "Airport Express": "bg-orange-500"
        }
        return colors.get(line_name, "bg-slate-900")

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
