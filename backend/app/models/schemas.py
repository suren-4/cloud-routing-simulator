"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RoutingMode(str, Enum):
    DEFAULT = "default"
    GLOBAL_ACCELERATOR = "global_accelerator"
    CDN_ONLY = "cdn_only"
    OPTIMIZED = "optimized"  # CDN + Global Accelerator


class RegionStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class UserLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    label: Optional[str] = "User"


class SimulationRequest(BaseModel):
    user_location: UserLocation
    routing_mode: RoutingMode = RoutingMode.DEFAULT
    cdn_enabled: bool = False
    num_requests: int = Field(default=1, ge=1, le=1000)
    content_type: str = Field(default="dynamic", pattern="^(static|dynamic)$")


class RouteHop(BaseModel):
    name: str
    type: str  # "user", "edge", "accelerator", "alb", "server"
    latitude: float
    longitude: float
    latency_ms: float
    cumulative_latency_ms: float


class SimulationResponse(BaseModel):
    routing_mode: RoutingMode
    total_latency_ms: float
    cost_usd: float
    route_path: list[RouteHop]
    selected_region: str
    cache_hit: bool
    cache_hit_rate: float
    data_transfer_cost: float
    compute_cost: float
    cdn_cost: float
    accelerator_cost: float
    distance_km: float
    num_hops: int
    latency_breakdown: dict


class BatchSimulationResponse(BaseModel):
    default: SimulationResponse
    global_accelerator: SimulationResponse
    cdn_only: SimulationResponse
    optimized: SimulationResponse
    latency_reduction_pct: float
    cost_savings_pct: float


class RegionInfo(BaseModel):
    code: str
    name: str
    city: str
    latitude: float
    longitude: float
    status: RegionStatus = RegionStatus.HEALTHY
    current_load: float = 0.0
    request_count: int = 0
    avg_latency_ms: float = 0.0


class EdgeLocation(BaseModel):
    code: str
    city: str
    latitude: float
    longitude: float


class MetricsSnapshot(BaseModel):
    timestamp: float
    total_requests: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cache_hit_ratio: float
    total_cost_usd: float
    requests_per_second: float
    active_regions: int
    regions_metrics: list[dict]


class RecommendationResponse(BaseModel):
    recommended_strategy: RoutingMode
    confidence: float
    predicted_latency_ms: float
    predicted_cost_usd: float
    latency_savings_pct: float
    cost_savings_pct: float
    reasoning: list[str]
    alternatives: list[dict]


class TrafficSpikeRequest(BaseModel):
    user_location: UserLocation
    spike_multiplier: float = Field(default=5.0, ge=1.0, le=20.0)
    duration_seconds: int = Field(default=30, ge=5, le=300)


class TrafficSpikeResponse(BaseModel):
    peak_rps: float
    auto_scaled: bool
    scale_up_regions: list[str]
    latency_during_spike: float
    latency_after_scaling: float
    cost_during_spike: float
    cost_normal: float
