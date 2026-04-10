"""Core routing engine — orchestrates all routing modes."""
import random
from app.models.regions import REGIONS, EDGE_LOCATIONS
from app.models.schemas import RoutingMode, RouteHop
from app.utils.geo import find_nearest, find_nearest_healthy, haversine_distance
from app.services.latency_calculator import (
    calculate_internet_latency, calculate_backbone_latency, calculate_cdn_latency
)
from app.services.cost_engine import calculate_cost
from app.services.cdn_simulator import cdn_simulator
from app.services.accelerator_sim import accelerator_simulator
from app.services.failure_manager import failure_manager
from app.utils.metrics import metrics_collector


def simulate_request(
    user_lat: float, user_lon: float,
    routing_mode: str, cdn_enabled: bool,
    content_type: str = "dynamic",
    num_requests: int = 1,
) -> dict:
    """Run a full routing simulation for a single request."""

    down_regions = failure_manager.get_down_regions()
    regions_list = [
        r for code, r in REGIONS.items()
        if code not in down_regions
    ]

    if routing_mode == "default":
        return _simulate_default(
            user_lat, user_lon, regions_list,
            cdn_enabled, content_type, num_requests
        )
    elif routing_mode == "global_accelerator":
        return _simulate_global_accelerator(
            user_lat, user_lon, cdn_enabled=False,
            content_type=content_type, num_requests=num_requests
        )
    elif routing_mode == "cdn_only":
        return _simulate_cdn_only(
            user_lat, user_lon, regions_list,
            content_type, num_requests
        )
    elif routing_mode == "optimized":
        return _simulate_optimized(
            user_lat, user_lon,
            content_type, num_requests
        )
    else:
        return _simulate_default(
            user_lat, user_lon, regions_list,
            cdn_enabled, content_type, num_requests
        )


def _simulate_default(user_lat, user_lon, regions_list,
                       cdn_enabled, content_type, num_requests):
    """Default DNS-based routing — route to nearest region over public internet."""
    nearest = find_nearest(user_lat, user_lon, regions_list)
    region = nearest

    latency_info = calculate_internet_latency(
        user_lat, user_lon, region["latitude"], region["longitude"]
    )

    # Check CDN if enabled
    cache_hit = False
    if cdn_enabled:
        nearest_edge = find_nearest(user_lat, user_lon, EDGE_LOCATIONS)
        cache_hit = cdn_simulator.check_cache(content_type, nearest_edge["code"])
        if cache_hit:
            cdn_lat = calculate_cdn_latency(
                user_lat, user_lon,
                nearest_edge["latitude"], nearest_edge["longitude"],
                True
            )
            latency_info["total_ms"] = cdn_lat["total_ms"]

    cost_info = calculate_cost("default", cache_hit, cdn_enabled, num_requests)
    degradation = failure_manager.get_degradation_factor(region["code"])
    final_latency = latency_info["total_ms"] * degradation

    # Build route path
    route_path = [
        RouteHop(
            name="User", type="user",
            latitude=user_lat, longitude=user_lon,
            latency_ms=0, cumulative_latency_ms=0
        ),
    ]

    if cdn_enabled and cache_hit:
        nearest_edge = find_nearest(user_lat, user_lon, EDGE_LOCATIONS)
        route_path.append(RouteHop(
            name=f"CloudFront Edge ({nearest_edge['city']})",
            type="edge",
            latitude=nearest_edge["latitude"],
            longitude=nearest_edge["longitude"],
            latency_ms=final_latency,
            cumulative_latency_ms=final_latency,
        ))
    else:
        route_path.extend([
            RouteHop(
                name="DNS Resolver", type="alb",
                latitude=user_lat + 0.5, longitude=user_lon + 0.5,
                latency_ms=5, cumulative_latency_ms=5,
            ),
            RouteHop(
                name=f"ALB ({region['city']})", type="alb",
                latitude=region["latitude"], longitude=region["longitude"],
                latency_ms=latency_info["total_ms"] * 0.7,
                cumulative_latency_ms=latency_info["total_ms"] * 0.7 + 5,
            ),
            RouteHop(
                name=f"Server ({region['city']})", type="server",
                latitude=region["latitude"] + 0.1,
                longitude=region["longitude"] + 0.1,
                latency_ms=latency_info["total_ms"] * 0.3,
                cumulative_latency_ms=final_latency,
            ),
        ])

    # Update region metrics
    _update_region_metrics(region["code"], final_latency)

    result = {
        "routing_mode": "default",
        "total_latency_ms": round(final_latency, 2),
        "cost_usd": cost_info["total_usd"],
        "route_path": [hop.model_dump() for hop in route_path],
        "selected_region": region["code"],
        "cache_hit": cache_hit,
        "cache_hit_rate": cdn_simulator.hit_rate,
        "data_transfer_cost": cost_info["data_transfer_cost"],
        "compute_cost": cost_info["compute_cost"],
        "cdn_cost": cost_info["cdn_cost"],
        "accelerator_cost": 0.0,
        "distance_km": nearest.get("distance_km", 0),
        "num_hops": len(route_path),
        "latency_breakdown": latency_info,
    }

    metrics_collector.record(final_latency, cost_info["total_usd"],
                             cache_hit, region["code"])
    return result


def _simulate_global_accelerator(user_lat, user_lon, cdn_enabled,
                                  content_type, num_requests):
    """Global Accelerator — Anycast routing via AWS backbone."""
    ga_result = accelerator_simulator.route_request(user_lat, user_lon)

    if "error" in ga_result:
        return {"error": ga_result["error"]}

    edge = ga_result["edge"]
    region = ga_result["region"]["region"]
    latency_info = ga_result["latency"]

    cache_hit = False
    cost_info = calculate_cost("global_accelerator", cache_hit, False, num_requests)

    degradation = failure_manager.get_degradation_factor(region["code"])
    final_latency = latency_info["total_ms"] * degradation

    route_path = [
        RouteHop(
            name="User", type="user",
            latitude=user_lat, longitude=user_lon,
            latency_ms=0, cumulative_latency_ms=0,
        ),
        RouteHop(
            name=f"Global Accelerator Edge ({edge['city']})",
            type="accelerator",
            latitude=edge["latitude"], longitude=edge["longitude"],
            latency_ms=latency_info["edge_latency_ms"],
            cumulative_latency_ms=latency_info["edge_latency_ms"],
        ),
        RouteHop(
            name=f"AWS Backbone", type="accelerator",
            latitude=(edge["latitude"] + region["latitude"]) / 2,
            longitude=(edge["longitude"] + region["longitude"]) / 2,
            latency_ms=latency_info["backbone_latency_ms"],
            cumulative_latency_ms=latency_info["edge_latency_ms"] + latency_info["backbone_latency_ms"],
        ),
        RouteHop(
            name=f"ALB ({region['city']})", type="alb",
            latitude=region["latitude"], longitude=region["longitude"],
            latency_ms=3,
            cumulative_latency_ms=final_latency - latency_info["processing_ms"],
        ),
        RouteHop(
            name=f"Server ({region['city']})", type="server",
            latitude=region["latitude"] + 0.1,
            longitude=region["longitude"] + 0.1,
            latency_ms=latency_info["processing_ms"],
            cumulative_latency_ms=final_latency,
        ),
    ]

    _update_region_metrics(region["code"], final_latency)

    result = {
        "routing_mode": "global_accelerator",
        "total_latency_ms": round(final_latency, 2),
        "cost_usd": cost_info["total_usd"],
        "route_path": [hop.model_dump() for hop in route_path],
        "selected_region": region["code"],
        "cache_hit": False,
        "cache_hit_rate": cdn_simulator.hit_rate,
        "data_transfer_cost": cost_info["data_transfer_cost"],
        "compute_cost": cost_info["compute_cost"],
        "cdn_cost": 0.0,
        "accelerator_cost": cost_info["accelerator_cost"],
        "distance_km": latency_info.get("total_distance_km", 0),
        "num_hops": len(route_path),
        "latency_breakdown": latency_info,
    }

    metrics_collector.record(final_latency, cost_info["total_usd"],
                             False, region["code"])
    return result


def _simulate_cdn_only(user_lat, user_lon, regions_list,
                        content_type, num_requests):
    """CDN-only routing — serve from CloudFront edge when possible."""
    nearest_edge = find_nearest(user_lat, user_lon, EDGE_LOCATIONS)
    nearest_region = find_nearest(user_lat, user_lon, regions_list)

    cache_hit = cdn_simulator.check_cache(content_type, nearest_edge["code"])

    cdn_lat = calculate_cdn_latency(
        user_lat, user_lon,
        nearest_edge["latitude"], nearest_edge["longitude"],
        cache_hit,
        nearest_region["latitude"], nearest_region["longitude"],
    )

    cost_info = calculate_cost("cdn_only", cache_hit, True, num_requests)
    final_latency = cdn_lat["total_ms"]

    route_path = [
        RouteHop(
            name="User", type="user",
            latitude=user_lat, longitude=user_lon,
            latency_ms=0, cumulative_latency_ms=0,
        ),
        RouteHop(
            name=f"CloudFront Edge ({nearest_edge['city']})",
            type="edge",
            latitude=nearest_edge["latitude"],
            longitude=nearest_edge["longitude"],
            latency_ms=final_latency * 0.3,
            cumulative_latency_ms=final_latency * 0.3,
        ),
    ]

    if not cache_hit:
        route_path.extend([
            RouteHop(
                name=f"Origin ({nearest_region['city']})", type="server",
                latitude=nearest_region["latitude"],
                longitude=nearest_region["longitude"],
                latency_ms=final_latency * 0.7,
                cumulative_latency_ms=final_latency,
            ),
        ])

    region_code = nearest_region["code"]
    _update_region_metrics(region_code, final_latency)

    result = {
        "routing_mode": "cdn_only",
        "total_latency_ms": round(final_latency, 2),
        "cost_usd": cost_info["total_usd"],
        "route_path": [hop.model_dump() for hop in route_path],
        "selected_region": region_code,
        "cache_hit": cache_hit,
        "cache_hit_rate": cdn_simulator.hit_rate,
        "data_transfer_cost": cost_info["data_transfer_cost"],
        "compute_cost": cost_info["compute_cost"],
        "cdn_cost": cost_info["cdn_cost"],
        "accelerator_cost": 0.0,
        "distance_km": nearest_edge.get("distance_km", 0),
        "num_hops": len(route_path),
        "latency_breakdown": cdn_lat,
    }

    metrics_collector.record(final_latency, cost_info["total_usd"],
                             cache_hit, region_code)
    return result


def _simulate_optimized(user_lat, user_lon, content_type, num_requests):
    """Fully optimized — Global Accelerator + CloudFront CDN."""
    nearest_edge = find_nearest(user_lat, user_lon, EDGE_LOCATIONS)

    # Check CDN first
    cache_hit = cdn_simulator.check_cache(content_type, nearest_edge["code"])

    if cache_hit:
        # Serve directly from edge
        cdn_lat = calculate_cdn_latency(
            user_lat, user_lon,
            nearest_edge["latitude"], nearest_edge["longitude"],
            True
        )
        final_latency = cdn_lat["total_ms"]

        cost_info = calculate_cost("optimized", True, True, num_requests)

        route_path = [
            RouteHop(
                name="User", type="user",
                latitude=user_lat, longitude=user_lon,
                latency_ms=0, cumulative_latency_ms=0,
            ),
            RouteHop(
                name=f"CloudFront Edge ({nearest_edge['city']})",
                type="edge",
                latitude=nearest_edge["latitude"],
                longitude=nearest_edge["longitude"],
                latency_ms=final_latency,
                cumulative_latency_ms=final_latency,
            ),
        ]

        region_code = nearest_edge.get("code", "edge")
    else:
        # Cache miss — use Global Accelerator for origin fetch
        ga_result = accelerator_simulator.route_request(user_lat, user_lon)
        if "error" in ga_result:
            return {"error": ga_result["error"]}

        edge = ga_result["edge"]
        region = ga_result["region"]["region"]
        latency_info = ga_result["latency"]

        # Add small CDN overhead for cache miss processing
        final_latency = latency_info["total_ms"] + random.uniform(2, 5)

        cost_info = calculate_cost("optimized", False, True, num_requests)

        route_path = [
            RouteHop(
                name="User", type="user",
                latitude=user_lat, longitude=user_lon,
                latency_ms=0, cumulative_latency_ms=0,
            ),
            RouteHop(
                name=f"CloudFront Edge ({nearest_edge['city']})",
                type="edge",
                latitude=nearest_edge["latitude"],
                longitude=nearest_edge["longitude"],
                latency_ms=5,
                cumulative_latency_ms=5,
            ),
            RouteHop(
                name=f"Global Accelerator ({edge['city']})",
                type="accelerator",
                latitude=edge["latitude"],
                longitude=edge["longitude"],
                latency_ms=latency_info["edge_latency_ms"],
                cumulative_latency_ms=5 + latency_info["edge_latency_ms"],
            ),
            RouteHop(
                name=f"AWS Backbone", type="accelerator",
                latitude=(edge["latitude"] + region["latitude"]) / 2,
                longitude=(edge["longitude"] + region["longitude"]) / 2,
                latency_ms=latency_info["backbone_latency_ms"],
                cumulative_latency_ms=(
                    5 + latency_info["edge_latency_ms"] +
                    latency_info["backbone_latency_ms"]
                ),
            ),
            RouteHop(
                name=f"Server ({region['city']})", type="server",
                latitude=region["latitude"],
                longitude=region["longitude"],
                latency_ms=latency_info["processing_ms"],
                cumulative_latency_ms=final_latency,
            ),
        ]
        region_code = region["code"]

    _update_region_metrics(
        region_code if not region_code.startswith("edge") else "us-east-1",
        final_latency
    )

    result = {
        "routing_mode": "optimized",
        "total_latency_ms": round(final_latency, 2),
        "cost_usd": cost_info["total_usd"],
        "route_path": [hop.model_dump() for hop in route_path],
        "selected_region": region_code,
        "cache_hit": cache_hit,
        "cache_hit_rate": cdn_simulator.hit_rate,
        "data_transfer_cost": cost_info["data_transfer_cost"],
        "compute_cost": cost_info["compute_cost"],
        "cdn_cost": cost_info["cdn_cost"],
        "accelerator_cost": cost_info["accelerator_cost"],
        "distance_km": nearest_edge.get("distance_km", 0),
        "num_hops": len(route_path),
        "latency_breakdown": {},
    }

    metrics_collector.record(final_latency, cost_info["total_usd"],
                             cache_hit, region_code)
    return result


def _update_region_metrics(region_code: str, latency: float):
    """Update in-memory region tracking."""
    if region_code in REGIONS:
        r = REGIONS[region_code]
        r["request_count"] = r.get("request_count", 0) + 1
        prev_avg = r.get("avg_latency_ms", 0.0)
        count = r["request_count"]
        r["avg_latency_ms"] = round(
            (prev_avg * (count - 1) + latency) / count, 2
        )
        r["current_load"] = min(r.get("current_load", 0) + 0.01, 1.0)
