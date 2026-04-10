"""Cost engine for computing infrastructure costs per request."""
from app.config import (
    COST_COMPUTE_PER_REQUEST, COST_DATA_TRANSFER_PER_GB,
    COST_CDN_PER_GB, COST_GLOBAL_ACCELERATOR_PER_GB,
    COST_ALB_PER_LCU_HOUR, AVG_REQUEST_SIZE_KB,
    CDN_COST_SAVINGS_FACTOR,
)


def calculate_cost(
    routing_mode: str,
    cache_hit: bool,
    cdn_enabled: bool,
    num_requests: int = 1
) -> dict:
    """Calculate the cost for a routing simulation."""
    request_size_gb = (AVG_REQUEST_SIZE_KB * num_requests) / (1024 * 1024)

    # Base compute cost
    compute_cost = COST_COMPUTE_PER_REQUEST * num_requests

    # Data transfer cost
    if cache_hit and cdn_enabled:
        # Cache hit: reduced data transfer from origin
        data_transfer_cost = COST_DATA_TRANSFER_PER_GB * request_size_gb * (1 - CDN_COST_SAVINGS_FACTOR)
    else:
        data_transfer_cost = COST_DATA_TRANSFER_PER_GB * request_size_gb

    # CDN cost 
    cdn_cost = 0.0
    if cdn_enabled:
        cdn_cost = COST_CDN_PER_GB * request_size_gb
        if cache_hit:
            # Cached content uses less origin data
            compute_cost *= 0.4  # 60% compute savings 

    # Global Accelerator cost
    accelerator_cost = 0.0
    if routing_mode in ("global_accelerator", "optimized"):
        accelerator_cost = COST_GLOBAL_ACCELERATOR_PER_GB * request_size_gb

    # ALB cost (always present)
    alb_cost = COST_ALB_PER_LCU_HOUR * (num_requests / 3600)  # pro-rated per request

    total = compute_cost + data_transfer_cost + cdn_cost + accelerator_cost + alb_cost

    return {
        "total_usd": round(total, 8),
        "compute_cost": round(compute_cost, 8),
        "data_transfer_cost": round(data_transfer_cost, 8),
        "cdn_cost": round(cdn_cost, 8),
        "accelerator_cost": round(accelerator_cost, 8),
        "alb_cost": round(alb_cost, 8),
    }


def compare_costs(num_requests: int = 1000) -> dict:
    """Compare costs across routing modes."""
    default = calculate_cost("default", False, False, num_requests)
    cdn_only = calculate_cost("cdn_only", True, True, num_requests)
    ga_only = calculate_cost("global_accelerator", False, False, num_requests)
    optimized = calculate_cost("optimized", True, True, num_requests)

    savings_pct = 0.0
    if default["total_usd"] > 0:
        savings_pct = round(
            (1 - optimized["total_usd"] / default["total_usd"]) * 100, 2
        )

    return {
        "default": default,
        "cdn_only": cdn_only,
        "global_accelerator": ga_only,
        "optimized": optimized,
        "savings_pct": savings_pct,
    }
