"""AWS Global Accelerator simulation."""
from app.utils.geo import find_nearest, haversine_distance
from app.models.regions import EDGE_LOCATIONS, REGIONS
from app.services.latency_calculator import calculate_backbone_latency


class AcceleratorSimulator:
    """Simulates AWS Global Accelerator Anycast routing."""

    def __init__(self):
        self._edge_locations = EDGE_LOCATIONS
        self._health_checks: dict[str, bool] = {
            code: True for code in REGIONS
        }
        self._weights: dict[str, float] = {
            code: 1.0 for code in REGIONS
        }

    def find_nearest_edge(self, lat: float, lon: float) -> dict:
        """Find the nearest AWS edge location (Anycast simulation)."""
        return find_nearest(lat, lon, self._edge_locations)

    def select_optimal_region(self, edge_lat: float, edge_lon: float,
                               exclude_regions: list[str] = None) -> dict:
        """Select the optimal origin region based on health and proximity."""
        exclude = set(exclude_regions or [])
        candidates = []

        for code, region in REGIONS.items():
            if code in exclude:
                continue
            if region.get("status") == "down":
                continue
            if not self._health_checks.get(code, True):
                continue

            distance = haversine_distance(
                edge_lat, edge_lon,
                region["latitude"], region["longitude"]
            )
            weight = self._weights.get(code, 1.0)
            load = region.get("current_load", 0.0)

            # Score: lower is better
            # Weighted by distance, load, and configured weight
            score = distance * (1 + load * 0.5) / weight

            candidates.append({
                "code": code,
                "region": region,
                "distance_km": round(distance, 2),
                "score": round(score, 2),
                "load": load,
            })

        candidates.sort(key=lambda x: x["score"])
        return candidates[0] if candidates else None

    def route_request(self, user_lat: float, user_lon: float,
                      exclude_regions: list[str] = None) -> dict:
        """Route a request via Global Accelerator."""
        # Step 1: Find nearest edge (Anycast)
        edge = self.find_nearest_edge(user_lat, user_lon)

        # Step 2: Select optimal origin region
        optimal = self.select_optimal_region(
            edge["latitude"], edge["longitude"],
            exclude_regions
        )

        if not optimal:
            return {"error": "No healthy regions available"}

        region = optimal["region"]

        # Step 3: Calculate backbone latency
        latency = calculate_backbone_latency(
            user_lat, user_lon,
            edge["latitude"], edge["longitude"],
            region["latitude"], region["longitude"],
        )

        return {
            "edge": edge,
            "region": optimal,
            "latency": latency,
        }

    def set_region_health(self, region_code: str, healthy: bool):
        """Update health check status for a region."""
        self._health_checks[region_code] = healthy

    def set_region_weight(self, region_code: str, weight: float):
        """Set routing weight for a region."""
        self._weights[region_code] = max(0.1, weight)


# Singleton
accelerator_simulator = AcceleratorSimulator()
