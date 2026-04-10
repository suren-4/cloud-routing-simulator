"""Latency calculator using distance-based models."""
import random
from app.utils.geo import haversine_distance
from app.config import (
    INTERNET_SPEED_FACTOR, BACKBONE_SPEED_FACTOR,
    BASE_PROCESSING_LATENCY, EDGE_PROCESSING_LATENCY,
    JITTER_RANGE_INTERNET, JITTER_RANGE_BACKBONE,
    HOP_PENALTY_INTERNET, HOP_PENALTY_BACKBONE,
    CACHE_HIT_LATENCY_RANGE,
)


def calculate_internet_latency(
    src_lat: float, src_lon: float,
    dst_lat: float, dst_lon: float,
    congestion_factor: float = 1.0
) -> dict:
    """Calculate latency over public internet."""
    distance_km = haversine_distance(src_lat, src_lon, dst_lat, dst_lon)
    propagation = distance_km * INTERNET_SPEED_FACTOR
    jitter = random.uniform(*JITTER_RANGE_INTERNET)
    processing = BASE_PROCESSING_LATENCY
    hop_penalty = HOP_PENALTY_INTERNET * congestion_factor
    total = propagation + jitter + processing + hop_penalty

    return {
        "total_ms": round(total, 2),
        "propagation_ms": round(propagation, 2),
        "jitter_ms": round(jitter, 2),
        "processing_ms": round(processing, 2),
        "hop_penalty_ms": round(hop_penalty, 2),
        "distance_km": round(distance_km, 2),
    }


def calculate_backbone_latency(
    src_lat: float, src_lon: float,
    edge_lat: float, edge_lon: float,
    dst_lat: float, dst_lon: float,
) -> dict:
    """Calculate latency via AWS backbone (Global Accelerator)."""
    # User → nearest edge (internet)
    edge_distance = haversine_distance(src_lat, src_lon, edge_lat, edge_lon)
    edge_latency = edge_distance * INTERNET_SPEED_FACTOR * 0.5 + random.uniform(2, 8)

    # Edge → destination region (AWS backbone, much faster)
    backbone_distance = haversine_distance(edge_lat, edge_lon, dst_lat, dst_lon)
    backbone_latency = backbone_distance * BACKBONE_SPEED_FACTOR + random.uniform(*JITTER_RANGE_BACKBONE)

    processing = EDGE_PROCESSING_LATENCY + BASE_PROCESSING_LATENCY
    hop_penalty = HOP_PENALTY_BACKBONE
    total = edge_latency + backbone_latency + processing + hop_penalty

    return {
        "total_ms": round(total, 2),
        "edge_latency_ms": round(edge_latency, 2),
        "backbone_latency_ms": round(backbone_latency, 2),
        "processing_ms": round(processing, 2),
        "hop_penalty_ms": round(hop_penalty, 2),
        "edge_distance_km": round(edge_distance, 2),
        "backbone_distance_km": round(backbone_distance, 2),
        "total_distance_km": round(edge_distance + backbone_distance, 2),
    }


def calculate_cdn_latency(
    src_lat: float, src_lon: float,
    edge_lat: float, edge_lon: float,
    cache_hit: bool,
    origin_lat: float = 0, origin_lon: float = 0,
) -> dict:
    """Calculate latency for CDN (CloudFront) access."""
    edge_distance = haversine_distance(src_lat, src_lon, edge_lat, edge_lon)

    if cache_hit:
        # Served from edge — very fast
        latency = random.uniform(*CACHE_HIT_LATENCY_RANGE) + edge_distance * 0.002
        return {
            "total_ms": round(latency, 2),
            "edge_distance_km": round(edge_distance, 2),
            "cache_hit": True,
            "origin_fetch_ms": 0,
        }
    else:
        # Cache miss — must fetch from origin
        edge_latency = edge_distance * INTERNET_SPEED_FACTOR * 0.5
        origin_distance = haversine_distance(edge_lat, edge_lon, origin_lat, origin_lon)
        origin_fetch = origin_distance * BACKBONE_SPEED_FACTOR + BASE_PROCESSING_LATENCY
        total = edge_latency + origin_fetch + random.uniform(3, 10)
        return {
            "total_ms": round(total, 2),
            "edge_distance_km": round(edge_distance, 2),
            "cache_hit": False,
            "origin_fetch_ms": round(origin_fetch, 2),
        }
