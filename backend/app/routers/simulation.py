"""Simulation API routes."""
import random
from fastapi import APIRouter
from app.models.schemas import SimulationRequest, TrafficSpikeRequest
from app.services.routing_engine import simulate_request
from app.services.failure_manager import failure_manager
from app.models.regions import REGIONS

router = APIRouter(prefix="/api/simulate", tags=["simulation"])


@router.post("")
async def run_simulation(req: SimulationRequest):
    """Run a single routing simulation."""
    result = simulate_request(
        user_lat=req.user_location.latitude,
        user_lon=req.user_location.longitude,
        routing_mode=req.routing_mode.value,
        cdn_enabled=req.cdn_enabled,
        content_type=req.content_type,
        num_requests=req.num_requests,
    )
    return result


@router.post("/batch")
async def run_batch_simulation(req: SimulationRequest):
    """Run simulation across all routing modes for comparison."""
    results = {}
    modes = ["default", "global_accelerator", "cdn_only", "optimized"]

    for mode in modes:
        cdn = mode in ("cdn_only", "optimized")
        result = simulate_request(
            user_lat=req.user_location.latitude,
            user_lon=req.user_location.longitude,
            routing_mode=mode,
            cdn_enabled=cdn,
            content_type=req.content_type,
            num_requests=req.num_requests,
        )
        results[mode] = result

    # Calculate improvements
    default_latency = results["default"]["total_latency_ms"]
    optimized_latency = results["optimized"]["total_latency_ms"]
    default_cost = results["default"]["cost_usd"]
    optimized_cost = results["optimized"]["cost_usd"]

    latency_reduction = 0
    if default_latency > 0:
        latency_reduction = round(
            (1 - optimized_latency / default_latency) * 100, 2
        )

    cost_savings = 0
    if default_cost > 0:
        cost_savings = round(
            (1 - optimized_cost / default_cost) * 100, 2
        )

    return {
        **results,
        "latency_reduction_pct": latency_reduction,
        "cost_savings_pct": cost_savings,
    }


@router.post("/traffic-spike")
async def simulate_traffic_spike(req: TrafficSpikeRequest):
    """Simulate a traffic spike with auto-scaling."""
    base_rps = 100
    peak_rps = base_rps * req.spike_multiplier

    # Simulate normal latency
    normal_result = simulate_request(
        user_lat=req.user_location.latitude,
        user_lon=req.user_location.longitude,
        routing_mode="optimized",
        cdn_enabled=True,
        num_requests=1,
    )

    # During spike: latency increases due to load
    spike_latency = normal_result["total_latency_ms"] * (1 + req.spike_multiplier * 0.15)
    spike_cost = normal_result["cost_usd"] * req.spike_multiplier

    # Auto-scaling kicks in
    auto_scaled = req.spike_multiplier > 3.0
    scale_up_regions = []
    if auto_scaled:
        available = [
            code for code, r in REGIONS.items()
            if r["status"] != "down" and r.get("current_load", 0) < 0.5
        ]
        scale_up_regions = random.sample(available, min(2, len(available)))
        # After scaling, latency normalizes
        after_scaling_latency = normal_result["total_latency_ms"] * 1.1
    else:
        after_scaling_latency = spike_latency * 0.8

    return {
        "peak_rps": round(peak_rps, 2),
        "auto_scaled": auto_scaled,
        "scale_up_regions": scale_up_regions,
        "latency_during_spike": round(spike_latency, 2),
        "latency_after_scaling": round(after_scaling_latency, 2),
        "cost_during_spike": round(spike_cost, 8),
        "cost_normal": normal_result["cost_usd"],
    }
