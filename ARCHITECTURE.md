# Architecture Documentation

## System Architecture

### High-Level Overview

```
                        ┌─────────────────────────────────┐
                        │          User Browser            │
                        │     (React SPA Dashboard)        │
                        └──────────────┬──────────────────┘
                                       │ HTTP/REST
                        ┌──────────────▼──────────────────┐
                        │      Nginx Reverse Proxy         │
                        │   (Serves static + proxies API)  │
                        └──────────────┬──────────────────┘
                                       │ /api/*
                        ┌──────────────▼──────────────────┐
                        │     FastAPI Backend Server        │
                        │        (Uvicorn ASGI)            │
                        ├──────────────────────────────────┤
                        │  ┌─────────┐  ┌──────────────┐  │
                        │  │ Routing  │  │ Latency      │  │
                        │  │ Engine   │  │ Calculator   │  │
                        │  └────┬────┘  └──────────────┘  │
                        │  ┌────▼────┐  ┌──────────────┐  │
                        │  │   CDN   │  │    Cost      │  │
                        │  │  Sim    │  │   Engine     │  │
                        │  └────┬────┘  └──────────────┘  │
                        │  ┌────▼────┐  ┌──────────────┐  │
                        │  │   GA    │  │     AI       │  │
                        │  │  Sim    │  │ Recommender  │  │
                        │  └─────────┘  └──────────────┘  │
                        └──────────────────────────────────┘
```

## Component Details

### Frontend Architecture

The frontend is a React 18 SPA built with Vite, following a component-based architecture:

| Component | Purpose | Key Libraries |
|-----------|---------|---------------|
| `WorldMap` | Interactive SVG map with region markers and route paths | react-simple-maps, framer-motion |
| `Controls` | Routing mode selection, toggles, action buttons | Native React |
| `LatencyChart` | Real-time latency comparison charts | Recharts |
| `ComparisonView` | Side-by-side routing mode comparison table | Native React |
| `MonitoringDash` | Prometheus-style metrics dashboard | Recharts |
| `FailureSimulator` | Region failure toggle + AI recommendations | framer-motion |

### Backend Architecture

The FastAPI backend follows a clean service-oriented architecture:

```
app/
├── main.py              # App entry, middleware, router registration
├── config.py            # All constants and configuration
├── routers/             # HTTP endpoint handlers
│   ├── simulation.py    # /api/simulate endpoints
│   ├── regions.py       # /api/regions management
│   ├── monitoring.py    # /api/metrics export
│   └── recommendation.py # /api/recommend AI engine
├── services/            # Business logic (pure Python, no HTTP concerns)
│   ├── routing_engine.py     # Orchestrates all routing modes
│   ├── latency_calculator.py # Distance-based latency models
│   ├── cost_engine.py        # AWS cost models
│   ├── cdn_simulator.py      # CloudFront cache behavior
│   ├── accelerator_sim.py    # Global Accelerator Anycast sim
│   ├── failure_manager.py    # Region outage management
│   └── ai_recommender.py     # Weighted scoring recommendation
├── models/              # Data models
│   ├── schemas.py       # Pydantic request/response models
│   └── regions.py       # Region & edge location data
└── utils/               # Shared utilities
    ├── geo.py           # Haversine distance, nearest-location
    └── metrics.py       # Prometheus-compatible metrics collector
```

### Simulation Model

#### Latency Calculation

1. **Default DNS Routing**:
   `latency = distance_km × 0.012 + jitter(0-18ms) + processing(8ms) + hop_penalty(15ms)`

2. **Global Accelerator**:
   `latency = edge_hop(distance × 0.006 + jitter) + backbone(distance × 0.005 + jitter) + processing(11ms) + hop_penalty(3ms)`

3. **CDN Cache Hit**:
   `latency = 2-12ms + edge_distance × 0.002`

4. **CDN Cache Miss**:
   `latency = edge_hop + origin_fetch(backbone) + processing`

#### Cost Model

- **Compute**: $0.0000004/request (Lambda-equivalent)
- **Data Transfer**: $0.09/GB
- **CDN**: $0.085/GB (but saves 60% on data transfer when cached)
- **Global Accelerator**: $0.015/GB premium
- **ALB**: $0.008/LCU-hour

### Infrastructure Architecture

#### AWS Deployment (via Terraform)

```
Internet → Global Accelerator (Anycast IPs)
    ↓
CloudFront Distribution (Edge Caching)
    ↓
Application Load Balancer (Health-based routing)
    ↓
ECS Fargate Cluster (Auto-scaling containers)
    ↓
VPC (Public + Private subnets across 2 AZs)
```

#### Docker Compose (Local Development)

```
docker-compose.yml
├── frontend (Nginx:80 → port 3000)
├── backend (Uvicorn:8000)
├── prometheus (:9090) → scrapes backend metrics
└── grafana (:3001) → visualizes prometheus data
```

## Data Flow

1. User selects location + routing mode in the frontend
2. Frontend sends `POST /api/simulate` with parameters
3. Backend routing engine:
   a. Determines nearest region (Haversine distance)
   b. Calculates latency based on routing mode
   c. Checks CDN cache (probabilistic model)
   d. Computes cost breakdown
   e. Builds route path (list of hops with coordinates)
   f. Records metrics
4. Response sent back with full route path, latency, cost
5. Frontend renders animated path on map, updates charts
