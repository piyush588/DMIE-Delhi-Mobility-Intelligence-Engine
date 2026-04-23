from datetime import datetime
from typing import List, Dict

class ScoringEngine:
    def __init__(self):
        # Weights for different factors
        self.weights = {
            "time": 0.4,
            "cost": 0.3,
            "comfort": 0.2,
            "reliability": 0.1
        }

    def get_traffic_level(self, time_obj: datetime) -> str:
        hour = time_obj.hour
        # Peak Hours: 8-11 AM and 5-9 PM (17-21)
        if 8 <= hour <= 11 or 17 <= hour <= 21:
            return "HIGH"
        return "NORMAL"

    def calculate_score(self, mode_data: Dict, traffic_level: str, is_near_metro: bool) -> float:
        """
        Calculates a score for a transport mode.
        Higher is better.
        """
        # 1. Base Scores (assume normalized 0-1)
        # Time score: 1 - (time / max_expected_time)
        time_score = mode_data.get("normalized_time", 0.5)
        cost_score = mode_data.get("normalized_cost", 0.5)
        comfort_score = mode_data.get("comfort", 0.5)
        reliability = mode_data.get("reliability", 0.5)

        # 2. Heuristics & Penalties
        mode = mode_data.get("mode", "").lower()
        
        # Peak Hour Penalty for road transport
        if traffic_level == "HIGH" and mode in ["cab", "auto", "car"]:
            time_score *= 0.6  # Significant penalty to perceived time
            reliability *= 0.7 # Unreliable due to traffic

        # Metro Bonus
        if mode == "metro" and is_near_metro:
            comfort_score += 0.2
            reliability += 0.2
            # Metro is highly reliable during peak hours compared to road
            if traffic_level == "HIGH":
                reliability += 0.1

        # 3. Final Weighted Score
        final_score = (
            self.weights["time"] * time_score +
            self.weights["cost"] * cost_score +
            self.weights["comfort"] * min(comfort_score, 1.0) +
            self.weights["reliability"] * min(reliability, 1.0)
        )

        return round(final_score, 3)

    def normalize_options(self, options: List[Dict]) -> List[Dict]:
        """
        Normalizes time and cost across a set of options.
        """
        if not options:
            return []

        max_time = max(opt["time"] for opt in options) or 1
        max_cost = max(opt["cost"] for opt in options) or 1
        
        for opt in options:
            # For time/cost, smaller is better, so we subtract from 1
            opt["normalized_time"] = 1 - (opt["time"] / (max_time * 1.2))
            opt["normalized_cost"] = 1 - (opt["cost"] / (max_cost * 1.2))
            
        return options
