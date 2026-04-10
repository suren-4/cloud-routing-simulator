"""CloudFront CDN cache simulator."""
import random
import time
from app.config import DEFAULT_CACHE_HIT_RATE, CDN_TTL_SECONDS


class CDNSimulator:
    """Simulates CloudFront edge caching behavior."""

    def __init__(self):
        self._cache: dict[str, dict] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._base_hit_rate = DEFAULT_CACHE_HIT_RATE

    def check_cache(self, content_type: str = "dynamic",
                    edge_code: str = "default") -> bool:
        """Check if content is cached at the edge."""
        cache_key = f"{edge_code}:{content_type}"

        # Check if we have a valid cache entry
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry["timestamp"] < CDN_TTL_SECONDS:
                self._hit_count += 1
                return True
            else:
                # TTL expired
                del self._cache[cache_key]

        # Probabilistic cache simulation
        if content_type == "static":
            hit_probability = min(self._base_hit_rate + 0.15, 0.98)
        else:
            hit_probability = self._base_hit_rate * 0.6  # Dynamic content cached less

        is_hit = random.random() < hit_probability

        if is_hit:
            # Simulate cache population
            self._cache[cache_key] = {
                "timestamp": time.time(),
                "content_type": content_type,
            }
            self._hit_count += 1
        else:
            self._miss_count += 1

        return is_hit

    @property
    def hit_rate(self) -> float:
        total = self._hit_count + self._miss_count
        if total == 0:
            return 0.0
        return round(self._hit_count / total, 4)

    @property
    def stats(self) -> dict:
        return {
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": self.hit_rate,
            "cached_entries": len(self._cache),
        }

    def invalidate(self, edge_code: str = None):
        """Invalidate cache entries."""
        if edge_code:
            keys_to_remove = [k for k in self._cache if k.startswith(edge_code)]
            for k in keys_to_remove:
                del self._cache[k]
        else:
            self._cache.clear()


# Singleton
cdn_simulator = CDNSimulator()
