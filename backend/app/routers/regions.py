"""Region management API routes."""
from fastapi import APIRouter, HTTPException
from app.models.regions import REGIONS, EDGE_LOCATIONS
from app.services.failure_manager import failure_manager

router = APIRouter(prefix="/api/regions", tags=["regions"])


@router.get("")
async def list_regions():
    """List all regions with current status."""
    return {
        "regions": list(REGIONS.values()),
        "edge_locations": EDGE_LOCATIONS,
        "total_regions": len(REGIONS),
        "healthy_regions": sum(
            1 for r in REGIONS.values() if r["status"] == "healthy"
        ),
        "down_regions": sum(
            1 for r in REGIONS.values() if r["status"] == "down"
        ),
    }


@router.post("/{code}/toggle")
async def toggle_region(code: str):
    """Toggle a region between healthy and down."""
    if code not in REGIONS:
        raise HTTPException(status_code=404, detail=f"Region '{code}' not found")
    new_status = failure_manager.toggle_region(code)
    return {
        "code": code,
        "new_status": new_status,
        "region": REGIONS[code],
    }


@router.post("/{code}/degrade")
async def degrade_region(code: str, factor: float = 2.0):
    """Degrade a region with increased latency."""
    if code not in REGIONS:
        raise HTTPException(status_code=404, detail=f"Region '{code}' not found")
    failure_manager.degrade_region(code, factor)
    return {
        "code": code,
        "status": "degraded",
        "degradation_factor": factor,
    }


@router.post("/{code}/recover")
async def recover_region(code: str):
    """Recover a region."""
    if code not in REGIONS:
        raise HTTPException(status_code=404, detail=f"Region '{code}' not found")
    failure_manager.recover_region(code)
    return {
        "code": code,
        "status": "healthy",
    }


@router.get("/{code}/metrics")
async def region_metrics(code: str):
    """Get metrics for a specific region."""
    if code not in REGIONS:
        raise HTTPException(status_code=404, detail=f"Region '{code}' not found")
    return REGIONS[code]


@router.get("/failure-status")
async def failure_status():
    """Get current failure status."""
    return failure_manager.get_status()
