"""Monitoring and metrics API routes."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.utils.metrics import metrics_collector

router = APIRouter(prefix="/api/metrics", tags=["monitoring"])


@router.get("")
async def get_metrics():
    """Get current metrics snapshot."""
    return metrics_collector.snapshot()


@router.get("/history")
async def get_metrics_history():
    """Get historical metrics snapshots."""
    return {"history": metrics_collector.get_history()}


@router.get("/prometheus", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Export metrics in Prometheus text format."""
    return metrics_collector.prometheus_format()
