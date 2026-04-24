from datetime import datetime
from typing import List, Dict, Optional
from app.services.routing_service import RoutingService
from app.services.metro_service import MetroService
from app.core.scoring import ScoringEngine
from models.schemas import RouteRequest, RecommendationResponse, RouteOption, MetroStation, RouteSegment

class DecisionEngine:
    def __init__(self):
        self.routing = RoutingService()
        self.metro = MetroService()
        self.scoring = ScoringEngine()
        from app.services.cab_service import CabService
        self.cab = CabService()

    def get_recommendation(self, req: RouteRequest) -> RecommendationResponse:
        near_src = self.metro.get_nearest_station(req.src[0], req.src[1], threshold_meters=8000) # Threshold for NCR
        near_dest = self.metro.get_nearest_station(req.dest[0], req.dest[1], threshold_meters=8000)
        
        # Prelim distance
        rough_dist = ((req.src[0]-req.dest[0])**2 + (req.src[1]-req.dest[1])**2)**0.5 * 111

        options_raw = []
        
        # ... rest of logic

        # -- Option A: Pure Cab (Using Uber-like prices) --
        cab_data = self.cab.get_heuristic_estimate(req.src[0], req.src[1], req.dest[0], req.dest[1], req.time)
        options_raw.append({
            "mode": "cab",
            "time": cab_data["duration_min"],
            "cost": cab_data["price_estimate"],
            "distance_km": cab_data["distance_km"],
            "comfort": self._get_comfort_base("cab"),
            "reliability": self._get_reliability_base("cab"),
            "is_multimodal": False,
            "segments": []
        })

        # -- Option B: Generic Auto --
        auto_stats = self.routing.get_route_stats(req.src, req.dest, "auto")
        options_raw.append({
            "mode": "auto",
            "time": auto_stats["duration_min"],
            "cost": self.cab.get_auto_estimate(auto_stats["distance_km"], req.time),
            "distance_km": auto_stats["distance_km"],
            "comfort": self._get_comfort_base("auto"),
            "reliability": self._get_reliability_base("auto"),
            "is_multimodal": False,
            "segments": []
        })

        # -- Option C: Multi-modal Transit (The "Hub" Logic) --
        if near_src and near_dest:
            transit_option = self._calculate_transit_link(req, near_src, near_dest)
            if transit_option:
                options_raw.append(transit_option)

        # -- Option D: Walk (Only if < 5km) --
        if rough_dist <= 5.0:
            walk_stats = self.routing.get_route_stats(req.src, req.dest, "walk")
            options_raw.append({
                "mode": "walk",
                "time": walk_stats["duration_min"],
                "cost": 0.0,
                "distance_km": walk_stats["distance_km"],
                "comfort": self._get_comfort_base("walk"),
                "reliability": self._get_reliability_base("walk"),
                "is_multimodal": False,
                "segments": []
            })

        # 3. Score Options
        traffic_level = self.scoring.get_traffic_level(req.time)
        normalized_options = self.scoring.normalize_options(options_raw)
        
        final_options = []
        for opt in normalized_options:
            score = self.scoring.calculate_score(opt, traffic_level, is_near_metro=(near_src is not None), time_obj=req.time)
            final_options.append(RouteOption(
                mode=opt["mode"],
                is_multimodal=opt["is_multimodal"],
                segments=[RouteSegment(**s) for s in opt["segments"]],
                time=opt["time"],
                cost=opt["cost"],
                score=score,
                distance_km=opt["distance_km"]
            ))

        final_options.sort(key=lambda x: x.score, reverse=True)
        best = final_options[0]
        explanation = self._generate_explanation(best, traffic_level, near_src)

        return RecommendationResponse(
            best_mode=best.mode,
            confidence=best.score,
            explanation=explanation,
            nearest_metro_src=MetroStation(**near_src) if near_src else None,
            nearest_metro_dest=MetroStation(**near_dest) if near_dest else None,
            options=final_options
        )

    def _calculate_transit_link(self, req: RouteRequest, s_metro: Dict, d_metro: Dict) -> Optional[Dict]:
        """Calculates multi-modal: Last Mile 1 -> Metro -> Last Mile 2"""
        # Prelim distance
        rough_dist = ((req.src[0]-req.dest[0])**2 + (req.src[1]-req.dest[1])**2)**0.5 * 111
        if rough_dist < 2.5: # Don't suggest multimodal for very short trips
            return None
            
        # Segment 1: Source to Source-Metro (Auto)
        l1_dist = s_metro["distance_m"] / 1000
        l1_time = (l1_dist / 15) * 60 # 15km/h avg auto speed
        l1_cost = self.cab.get_auto_estimate(l1_dist, req.time)

        # Segment 2: Metro travel
        # Rough distance between metro stations
        m_dist = ((s_metro["coords"][0]-d_metro["coords"][0])**2 + (s_metro["coords"][1]-d_metro["coords"][1])**2)**0.5 * 111
        m_time = (m_dist / 35.0) * 60 # 35km/h avg metro speed
        m_cost = self._estimate_cost(m_dist, "metro", req.time)

        # Segment 3: Dest-Metro to Final Destination
        l2_dist = d_metro["distance_m"] / 1000
        l2_time = (l2_dist / 15) * 60
        l2_cost = self.cab.get_auto_estimate(l2_dist, req.time)

        total_time = l1_time + m_time + l2_time + 10 # 10 min overhead for entry/exit
        total_cost = l1_cost + m_cost + l2_cost
        total_dist = l1_dist + m_dist + l2_dist

        return {
            "mode": "metro",
            "time": round(total_time, 2),
            "cost": round(total_cost, 2),
            "distance_km": round(total_dist, 2),
            "comfort": 0.6, # Mixed comfort
            "reliability": 0.9, # High reliability
            "is_multimodal": True,
            "segments": [
                {"mode": "auto", "from_loc": "Source", "to_loc": s_metro["name"], "distance_km": round(l1_dist, 2), "duration_min": round(l1_time, 2), "cost": l1_cost},
                {"mode": "metro", "from_loc": s_metro["name"], "to_loc": d_metro["name"], "distance_km": round(m_dist, 2), "duration_min": round(m_time, 2), "cost": m_cost},
                {"mode": "auto", "from_loc": d_metro["name"], "to_loc": "Destination", "distance_km": round(l2_dist, 2), "duration_min": round(l2_time, 2), "cost": l2_cost},
            ]
        }


    def _estimate_cost(self, dist_km: float, mode: str, time_obj: datetime) -> float:
        if mode == "walk": 
            return 0.0
            
        if mode == "metro":
            is_sunday = time_obj.weekday() == 6
            # Delhi Metro Fare Table
            if dist_km <= 2:
                return 11.0
            elif dist_km <= 5:
                return 11.0 if is_sunday else 21.0
            elif dist_km <= 12:
                return 21.0 if is_sunday else 32.0
            elif dist_km <= 21:
                return 32.0 if is_sunday else 43.0
            elif dist_km <= 32:
                return 43.0 if is_sunday else 54.0
            else:
                return 54.0 if is_sunday else 64.0

        if mode == "cab": 
            return max(50.0, dist_km * 25.0)
            
        if mode == "auto": 
            return max(30.0, dist_km * 15.0)
            
        return 0.0

    def _get_comfort_base(self, mode: str) -> float:
        return {"cab": 0.9, "metro": 0.7, "auto": 0.5, "walk": 0.3}.get(mode, 0.5)

    def _get_reliability_base(self, mode: str) -> float:
        return {"metro": 0.95, "cab": 0.7, "auto": 0.6, "walk": 0.9}.get(mode, 0.5)

    def _generate_explanation(self, best, traffic, near_src) -> str:
        if best.mode == "metro":
            msg = "Metro recommended due to "
            if traffic == "HIGH": msg += "heavy traffic and "
            msg += f"proximity to {near_src['name']} station."
            return msg
        
        if traffic == "HIGH" and best.mode != "metro":
            return f"Despite high traffic, {best.mode} is the most balanced option for this distance."
        
        return f"Optimal choice based on time and cost efficiency."
