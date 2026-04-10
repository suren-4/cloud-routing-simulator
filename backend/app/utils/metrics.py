"""Prometheus-style metrics collector."""
import time
from collections import deque
from threading import Lock


class MetricsCollector:
    """Collects and aggregates simulation metrics."""

    def __init__(self, max_history: int = 500):
        self._lock = Lock()
        self._latencies: deque = deque(maxlen=max_history)
        self._costs: deque = deque(maxlen=max_history)
        self._cache_hits: deque = deque(maxlen=max_history)
        self._timestamps: deque = deque(maxlen=max_history)
        self._total_requests = 0
        self._region_requests: dict[str, int] = {}
        self._region_latencies: dict[str, list] = {}
        self._start_time = time.time()
        self._history: deque = deque(maxlen=100)

    def record(self, latency_ms: float, cost_usd: float, cache_hit: bool,
               region: str):
        """Record a single simulation result."""
        with self._lock:
            now = time.time()
            self._latencies.append(latency_ms)
            self._costs.append(cost_usd)
            self._cache_hits.append(1 if cache_hit else 0)
            self._timestamps.append(now)
            self._total_requests += 1
            self._region_requests[region] = self._region_requests.get(region, 0) + 1
            if region not in self._region_latencies:
                self._region_latencies[region] = []
            self._region_latencies[region].append(latency_ms)
            # Keep only last 100 per region
            if len(self._region_latencies[region]) > 100:
                self._region_latencies[region] = self._region_latencies[region][-100:]

    def snapshot(self) -> dict:
        """Get current metrics snapshot."""
        with self._lock:
            if not self._latencies:
                return {
                    "timestamp": time.time(),
                    "total_requests": 0,
                    "avg_latency_ms": 0,
                    "p50_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "p99_latency_ms": 0,
                    "cache_hit_ratio": 0,
                    "total_cost_usd": 0,
                    "requests_per_second": 0,
                    "active_regions": 0,
                    "regions_metrics": [],
                }

            sorted_lat = sorted(self._latencies)
            n = len(sorted_lat)
            elapsed = max(time.time() - self._start_time, 1)

            regions_metrics = []
            for code, count in self._region_requests.items():
                lats = self._region_latencies.get(code, [])
                regions_metrics.append({
                    "code": code,
                    "request_count": count,
                    "avg_latency_ms": round(sum(lats) / len(lats), 2) if lats else 0,
                    "load": round(min(count / max(self._total_requests, 1), 1.0), 3),
                })

            snapshot = {
                "timestamp": time.time(),
                "total_requests": self._total_requests,
                "avg_latency_ms": round(sum(self._latencies) / n, 2),
                "p50_latency_ms": round(sorted_lat[int(n * 0.5)], 2),
                "p95_latency_ms": round(sorted_lat[min(int(n * 0.95), n - 1)], 2),
                "p99_latency_ms": round(sorted_lat[min(int(n * 0.99), n - 1)], 2),
                "cache_hit_ratio": round(sum(self._cache_hits) / len(self._cache_hits), 3) if self._cache_hits else 0,
                "total_cost_usd": round(sum(self._costs), 6),
                "requests_per_second": round(self._total_requests / elapsed, 2),
                "active_regions": len(self._region_requests),
                "regions_metrics": regions_metrics,
            }

            # Save to history
            self._history.append(snapshot)
            return snapshot

    def get_history(self) -> list[dict]:
        """Get historical snapshots."""
        with self._lock:
            return list(self._history)

    def prometheus_format(self) -> str:
        """Export metrics in Prometheus text format."""
        s = self.snapshot()
        lines = [
            f'# HELP routing_sim_total_requests Total simulation requests',
            f'# TYPE routing_sim_total_requests counter',
            f'routing_sim_total_requests {s["total_requests"]}',
            f'# HELP routing_sim_avg_latency_ms Average latency in milliseconds',
            f'# TYPE routing_sim_avg_latency_ms gauge',
            f'routing_sim_avg_latency_ms {s["avg_latency_ms"]}',
            f'# HELP routing_sim_p95_latency_ms P95 latency in milliseconds',
            f'# TYPE routing_sim_p95_latency_ms gauge',
            f'routing_sim_p95_latency_ms {s["p95_latency_ms"]}',
            f'# HELP routing_sim_cache_hit_ratio Cache hit ratio',
            f'# TYPE routing_sim_cache_hit_ratio gauge',
            f'routing_sim_cache_hit_ratio {s["cache_hit_ratio"]}',
            f'# HELP routing_sim_total_cost_usd Total cost in USD',
            f'# TYPE routing_sim_total_cost_usd counter',
            f'routing_sim_total_cost_usd {s["total_cost_usd"]}',
            f'# HELP routing_sim_rps Requests per second',
            f'# TYPE routing_sim_rps gauge',
            f'routing_sim_rps {s["requests_per_second"]}',
        ]
        return '\n'.join(lines)


# Singleton instance
metrics_collector = MetricsCollector()
