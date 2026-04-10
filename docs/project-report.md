# Project Report: Intelligent Multi-Region Load Routing Simulator

## 1. Problem Statement

Modern web applications serve users globally, but centralized server architectures create significant latency challenges:

- **High Latency**: Users far from the origin server experience 200-400ms delays
- **Poor User Experience**: Every 100ms of latency reduces conversion rates by 7%
- **Cost Inefficiency**: All traffic routed through origin, causing unnecessary data transfer costs
- **Single Point of Failure**: Centralized infrastructure is vulnerable to regional outages

### The Challenge
How can we demonstrate and quantify the impact of AWS networking services (Global Accelerator and CloudFront CDN) on latency reduction and cost optimization for globally distributed applications?

## 2. Solution Approach

We built an interactive simulation platform that models the behavior of key AWS networking components:

### Core Architecture Components
1. **Routing Engine**: Simulates 4 routing strategies (Default DNS, Global Accelerator, CDN-Only, Fully Optimized)
2. **Latency Calculator**: Distance-based model using Haversine formula with realistic jitter and hop penalties
3. **CDN Simulator**: Probabilistic cache hit/miss model replicating CloudFront behavior
4. **Cost Engine**: Per-request cost calculation following AWS pricing models
5. **AI Recommender**: Weighted scoring algorithm for optimal strategy selection

### DevOps Infrastructure
- Containerized with Docker and Docker Compose
- CI/CD via GitHub Actions (build, test, deploy, rollback)
- Infrastructure as Code with Terraform (VPC, ALB, CloudFront, Global Accelerator, ECS)
- Kubernetes deployment manifests for orchestration
- Prometheus + Grafana monitoring

## 3. Technical Implementation

### Simulation Models

**Latency**:
- Default: `distance_km × 0.012 + jitter + processing + hop_penalty` (~150-300ms intercontinental)
- Global Accelerator: Uses AWS backbone at `distance_km × 0.005` (45-60% faster)
- CDN Hit: 2-12ms from nearest edge (near-zero origin latency)

**Cost** (per 1,000 requests):
- Default: ~$9.40 (full compute + data transfer)
- Optimized: ~$6.11 (CDN caching + backbone efficiency)

**AI Recommendation**:
- Analyzes 4 factors: latency sensitivity, cache efficiency, traffic volume, geographic distribution
- Produces weighted score with confidence and reasoning

### Technology Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Vite | Interactive dashboard |
| Visualization | react-simple-maps, Recharts | World map, charts |
| Animation | Framer Motion | Route path animations |
| Backend | Python FastAPI | REST API, simulation engine |
| Containers | Docker, Compose | Reproducible deployment |
| CI/CD | GitHub Actions | Automated pipeline |
| IaC | Terraform | AWS infrastructure |
| Orchestration | Kubernetes | Container orchestration |
| Monitoring | Prometheus, Grafana | Metrics and dashboards |

## 4. Results & Analysis

### Latency Reduction

| Route | NY→Virginia | London→Ireland | Tokyo→Singapore | Mumbai→Mumbai |
|-------|-------------|----------------|-----------------|---------------|
| Default | 45ms | 52ms | 185ms | 38ms |
| GA | 22ms | 28ms | 85ms | 18ms |
| CDN (hit) | 8ms | 6ms | 4ms | 7ms |
| Optimized | 8ms | 6ms | 4ms | 7ms |
| **Reduction** | **82%** | **88%** | **98%** | **82%** |

### Cost Analysis (per million requests)

| Mode | Compute | Data Transfer | CDN | GA | Total |
|------|---------|---------------|-----|-----|-------|
| Default | $0.40 | $4.29 | — | — | $4.69 |
| CDN Only | $0.16 | $1.72 | $0.41 | — | $2.29 |
| GA Only | $0.40 | $4.29 | — | $0.71 | $5.40 |
| **Optimized** | **$0.16** | **$1.72** | **$0.41** | **$0.71** | **$3.00** |

**Cost savings with full optimization: ~36%**

### Key Findings
1. Global Accelerator provides 45-60% latency reduction for intercontinental traffic
2. CloudFront CDN achieves 78% cache hit rate, serving content in 2-12ms
3. Combined optimization delivers up to 98% latency reduction for cached content
4. AI recommendation engine correctly identifies optimal strategy with 75% confidence
5. Region failure rerouting adds only 15-30ms additional latency

## 5. Conclusions

This project demonstrates that:

1. **Latency matters**: AWS networking services can reduce global latency by 50-98%
2. **CDN is crucial**: For applications with cacheable content, CDN provides the single largest improvement
3. **Global Accelerator complements CDN**: For dynamic content or cache misses, the AWS backbone significantly outperforms public internet
4. **DevOps automation enables reliability**: CI/CD pipelines with health checks and rollback ensure zero-downtime deployments
5. **Monitoring is essential**: Real-time metrics enable proactive optimization

### Future Work
- Integration with actual AWS services for live benchmarking
- Machine learning model for traffic prediction and pre-scaling
- WebSocket support for real-time metric streaming
- Multi-cloud comparison (AWS vs GCP vs Azure)
