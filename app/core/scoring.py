from datetime import datetime
from typing import List, Dict

class ScoringEngine:
    def __init__(self):
        # Base weights for different factors (used as defaults)
        self.default_weights = {
            "time": 0.4,
            "cost": 0.3,
            "comfort": 0.3
        }
        
        # Mode-specific weights
        self.mode_weights = {
            "metro": {"time": 0.5, "cost": 0.2, "comfort": 0.3},
            "cab": {"time": 0.6, "cost": 0.3, "comfort": 0.1},
            "auto": {"time": 0.5, "cost": 0.4, "comfort": 0.1},
            "walk": {"time": 0.7, "cost": 0.1, "comfort": 0.2}
        }

    def get_traffic_level(self, time_obj: datetime) -> str:
        hour = time_obj.hour
        # Peak Hours: 8-11 AM and 5-9 PM (17-21)
        if 8 <= hour <= 11 or 17 <= hour <= 21:
            return "HIGH"
        return "NORMAL"

    def calculate_score(self, mode_data: Dict, traffic_level: str, is_near_metro: bool, time_obj: datetime) -> float:
        """
        Calculates a score using the improved formula:
        score = (base_score + bonus - penalty) * reliability
        """
        mode = mode_data.get("mode", "").lower()
        weights = self.mode_weights.get(mode, self.default_weights)
        
        # 1. Base Score (Weighted linear combination of normalized factors)
        time_score = mode_data.get("normalized_time", 0.5)
        cost_score = mode_data.get("normalized_cost", 0.5)
        comfort_score = mode_data.get("comfort", 0.5)
        reliability = mode_data.get("reliability", 0.5)
        
        base_score = (
            weights["time"] * time_score +
            weights["cost"] * cost_score +
            weights["comfort"] * comfort_score
        )

        # 2. Bonus & Penalty System
        bonus = 0.0
        penalty = 0.0
        
        # Peak Hour Penalty for road transport
        if traffic_level == "HIGH" and mode in ["cab", "auto", "car"]:
            penalty += 0.3

        # Short distance convenience bonus for Autos (the "Delhi Favorite" for <3km)
        # Note: We'll use distance_km from mode_data if available
        dist = mode_data.get("distance_km", 0)
        if mode == "auto" and 0.5 <= dist <= 3.0:
            bonus += 0.2

        # Late Night Adjustments (22:00 - 05:00)
        is_late_night = time_obj.hour >= 22 or time_obj.hour <= 5
        if is_late_night:
            if mode in ["cab", "auto"]:
                bonus += 0.4 # Significant preference at night
                reliability = min(1.0, reliability + 0.3)
            if mode == "metro":
                penalty += 0.4 # Heavy penalty due to frequency & last-mile

        # Metro Bonus for proximity
        if mode == "metro" and is_near_metro:
            bonus += 0.2
            if traffic_level == "HIGH":
                bonus += 0.1

        # 3. Reliability Multiplier (Dominant factor)
        if traffic_level == "HIGH" and mode in ["cab", "auto", "car"]:
            reliability *= 0.7 # Drop reliability significantly in traffic

        # Final non-linear formula
        final_score = (base_score + bonus - penalty) * reliability
        
        # Clamp between 0 and 1
        return round(max(0, min(1.0, final_score)), 3)

    def normalize_options(self, options: List[Dict]) -> List[Dict]:
        """
        Performs relative normalization across all options for a single query.
        Higher value = Better (so for time/cost, lower absolute values get higher normalized scores).
        """
        if not options:
            return []

        # Find max/min to normalize relatively
        max_time = max(opt["time"] for opt in options) or 1
        max_cost = max(opt["cost"] for opt in options) or 1
        
        for opt in options:
            # Time: Lower is better. Linear inverse: 1 - (opt_time / max_time)
            # We add a small buffer so the worst option isn't exactly 0
            opt["normalized_time"] = 1 - (opt["time"] / (max_time * 1.1))
            
            # Cost: Lower is better.
            opt["normalized_cost"] = 1 - (opt["cost"] / (max_cost * 1.1))
            
        return options
