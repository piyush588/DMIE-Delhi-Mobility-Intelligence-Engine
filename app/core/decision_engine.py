from typing import List, Dict
from app.services.routing_service import RoutingService
from app.services.metro_service import MetroService
from app.core.scoring import ScoringEngine
from models.schemas import RouteRequest, RecommendationResponse, RouteOption, MetroStation

class DecisionEngine:
    def __init__(self):
        self.routing = RoutingService()
        self.metro = MetroService()
        self.scoring = ScoringEngine()

    def get_recommendation(self, req: RouteRequest) -> RecommendationResponse:
        # 1. Check Metro Proximity
        near_src = self.metro.get_nearest_station(req.src[0], req.src[1])
        near_dest = self.metro.get_nearest_station(req.dest[0], req.dest[1])
        
        is_metro_feasible = (near_src is not None) and (near_dest is not None)

        # 2. Get Route Stats for different modes
        modes = ["cab", "auto", "walk"]
        if is_metro_feasible:
            modes.append("metro")

        options_raw = []
        for mode in modes:
            stats = self.routing.get_route_stats(req.src, req.dest, mode)
            
            # Simple Cost Heuristics
            cost = self._estimate_cost(stats["distance_km"], mode)
            
            options_raw.append({
                "mode": mode,
                "time": stats["duration_min"],
                "cost": cost,
                "distance_km": stats["distance_km"],
                "comfort": self._get_comfort_base(mode),
                "reliability": self._get_reliability_base(mode)
            })

        # 3. Score Options
        traffic_level = self.scoring.get_traffic_level(req.time)
        
        # Normalize time/cost across options before scoring
        normalized_options = self.scoring.normalize_options(options_raw)
        
        final_options = []
        for opt in normalized_options:
            score = self.scoring.calculate_score(
                opt, 
                traffic_level, 
                is_near_metro=(near_src is not None)
            )
            
            final_options.append(RouteOption(
                mode=opt["mode"],
                time=opt["time"],
                cost=opt["cost"],
                score=score,
                distance_km=opt["distance_km"]
            ))

        # Sort by score descending
        final_options.sort(key=lambda x: x.score, reverse=True)
        best = final_options[0]

        # 4. Generate Explanation
        explanation = self._generate_explanation(best, traffic_level, near_src)

        return RecommendationResponse(
            best_mode=best.mode,
            confidence=best.score, # Score as a proxy for confidence in V1
            explanation=explanation,
            nearest_metro_src=MetroStation(**near_src) if near_src else None,
            nearest_metro_dest=MetroStation(**near_dest) if near_dest else None,
            options=final_options
        )

    def _estimate_cost(self, dist_km: float, mode: str) -> float:
        if mode == "metro": return 40.0
        if mode == "walk": return 0.0
        if mode == "cab": return max(50.0, dist_km * 25.0)
        if mode == "auto": return max(30.0, dist_km * 15.0)
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
