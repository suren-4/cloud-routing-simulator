"""Region failure manager for simulating outages and rerouting."""
import time
from app.models.regions import REGIONS


class FailureManager:
    """Manages region failures and automatic rerouting."""

    def __init__(self):
        self._failures: dict[str, dict] = {}
        self._degradations: dict[str, float] = {}

    def fail_region(self, region_code: str):
        """Mark a region as completely down."""
        if region_code in REGIONS:
            REGIONS[region_code]["status"] = "down"
            REGIONS[region_code]["current_load"] = 0.0
            self._failures[region_code] = {
                "failed_at": time.time(),
                "type": "complete",
            }

    def degrade_region(self, region_code: str, factor: float = 2.0):
        """Mark a region as degraded (increased latency)."""
        if region_code in REGIONS:
            REGIONS[region_code]["status"] = "degraded"
            self._degradations[region_code] = factor

    def recover_region(self, region_code: str):
        """Restore a region to healthy status."""
        if region_code in REGIONS:
            REGIONS[region_code]["status"] = "healthy"
            self._failures.pop(region_code, None)
            self._degradations.pop(region_code, None)

    def get_degradation_factor(self, region_code: str) -> float:
        """Get the latency multiplier for a degraded region."""
        return self._degradations.get(region_code, 1.0)

    def get_down_regions(self) -> list[str]:
        """Get list of all currently failed regions."""
        return [code for code, r in REGIONS.items() if r["status"] == "down"]

    def get_status(self) -> dict:
        """Get failure status summary."""
        return {
            "down_regions": self.get_down_regions(),
            "degraded_regions": {
                code: factor for code, factor in self._degradations.items()
            },
            "failures": self._failures,
        }

    def toggle_region(self, region_code: str) -> str:
        """Toggle region between healthy and down."""
        if region_code not in REGIONS:
            return "unknown"
        current = REGIONS[region_code]["status"]
        if current == "down":
            self.recover_region(region_code)
            return "healthy"
        else:
            self.fail_region(region_code)
            return "down"


# Singleton
failure_manager = FailureManager()
