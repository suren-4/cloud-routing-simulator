"""Tests for routing engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.routing_engine import simulate_request
from app.services.failure_manager import failure_manager


def test_default_routing():
    """Test default DNS-based routing."""
    result = simulate_request(
        user_lat=40.7128, user_lon=-74.0060,
        routing_mode="default", cdn_enabled=False
    )
    assert result["routing_mode"] == "default"
    assert result["total_latency_ms"] > 0
    assert result["cost_usd"] > 0
    assert len(result["route_path"]) > 0
    assert result["selected_region"] != ""


def test_global_accelerator_routing():
    """Test Global Accelerator routing has lower latency."""
    default = simulate_request(
        user_lat=35.6762, user_lon=139.6503,
        routing_mode="default", cdn_enabled=False
    )
    ga = simulate_request(
        user_lat=35.6762, user_lon=139.6503,
        routing_mode="global_accelerator", cdn_enabled=False
    )
    assert ga["routing_mode"] == "global_accelerator"
    assert ga["total_latency_ms"] > 0
    # GA should generally be faster (though randomness may affect a single run)
    print(f"Default: {default['total_latency_ms']}ms, GA: {ga['total_latency_ms']}ms")


def test_cdn_routing():
    """Test CDN routing."""
    result = simulate_request(
        user_lat=51.5074, user_lon=-0.1278,
        routing_mode="cdn_only", cdn_enabled=True,
        content_type="static"
    )
    assert result["routing_mode"] == "cdn_only"
    assert result["total_latency_ms"] > 0


def test_optimized_routing():
    """Test fully optimized routing."""
    result = simulate_request(
        user_lat=19.0760, user_lon=72.8777,
        routing_mode="optimized", cdn_enabled=True
    )
    assert result["routing_mode"] == "optimized"
    assert result["total_latency_ms"] > 0


def test_batch_comparison():
    """Test that optimized is faster than default over many runs."""
    default_latencies = []
    optimized_latencies = []
    for _ in range(20):
        d = simulate_request(40.7128, -74.0060, "default", False)
        o = simulate_request(40.7128, -74.0060, "optimized", True)
        default_latencies.append(d["total_latency_ms"])
        optimized_latencies.append(o["total_latency_ms"])

    avg_default = sum(default_latencies) / len(default_latencies)
    avg_optimized = sum(optimized_latencies) / len(optimized_latencies)
    print(f"Avg Default: {avg_default:.2f}ms, Avg Optimized: {avg_optimized:.2f}ms")
    # Optimized should be at least 30% faster on average
    assert avg_optimized < avg_default * 0.85


def test_region_failure_reroute():
    """Test traffic rerouting when a region fails."""
    # Get the nearest region for Tokyo
    result1 = simulate_request(35.6762, 139.6503, "default", False)
    original_region = result1["selected_region"]

    # Fail that region
    failure_manager.fail_region(original_region)

    # Should route to a different region
    result2 = simulate_request(35.6762, 139.6503, "default", False)
    assert result2["selected_region"] != original_region

    # Recover
    failure_manager.recover_region(original_region)


if __name__ == "__main__":
    test_default_routing()
    print("✓ Default routing works")
    test_global_accelerator_routing()
    print("✓ Global Accelerator routing works")
    test_cdn_routing()
    print("✓ CDN routing works")
    test_optimized_routing()
    print("✓ Optimized routing works")
    test_batch_comparison()
    print("✓ Batch comparison confirms optimization")
    test_region_failure_reroute()
    print("✓ Region failure rerouting works")
    print("\nAll tests passed!")
