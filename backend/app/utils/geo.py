"""Geographic utility functions."""
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth in km."""
    R = 6371.0  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_nearest(lat: float, lon: float, locations: list[dict]) -> dict:
    """Find the nearest location from a list of locations."""
    nearest = None
    min_dist = float('inf')
    for loc in locations:
        dist = haversine_distance(lat, lon, loc["latitude"], loc["longitude"])
        if dist < min_dist:
            min_dist = dist
            nearest = loc
    return {**nearest, "distance_km": min_dist}


def find_nearest_healthy(lat: float, lon: float, locations: list[dict]) -> dict:
    """Find nearest location that is not 'down'."""
    healthy = [l for l in locations if l.get("status", "healthy") != "down"]
    if not healthy:
        healthy = locations  # fallback to all if all are down
    return find_nearest(lat, lon, healthy)
