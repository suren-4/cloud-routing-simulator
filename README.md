# Intelligent Multi-Region Load Routing Simulator

<div align="center">

🌐 **Cloud Routing Simulator** — An interactive platform demonstrating multi-region traffic routing optimization using AWS Global Accelerator and CloudFront CDN.

[![CI](https://github.com/user/cloud-routing-simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/user/cloud-routing-simulator/actions/workflows/ci.yml)
[![CD](https://github.com/user/cloud-routing-simulator/actions/workflows/cd.yml/badge.svg)](https://github.com/user/cloud-routing-simulator/actions/workflows/cd.yml)

</div>

---

## 🎯 Overview

This platform simulates how global user traffic is routed across multiple cloud regions, comparing:

- **Default DNS routing** — Standard internet-based routing
- **AWS Global Accelerator** — Anycast routing via AWS private backbone (45-60% latency reduction)
- **CloudFront CDN** — Edge caching for static content (2-12ms response time on cache hits)
- **Fully Optimized** — Combined CDN + Global Accelerator (best performance & cost)

### Key Results
| Metric | Without Optimization | With Full Optimization |
|--------|---------------------|----------------------|
| Avg Latency | ~180ms | ~65ms (64% reduction) |
| Cost per 1K requests | $9.40 | $6.11 (35% savings) |
| Cache Hit Rate | 0% | 78% |

---

## 🏗️ Architecture

```
User Request
    ↓
[Global Accelerator] → Anycast routing to nearest AWS edge
    ↓
[CloudFront Edge] → Cache check (hit → return immediately)
    ↓ (miss)
[AWS Backbone] → Private network to optimal region
    ↓
[Application Load Balancer] → Health-based routing
    ↓
[Backend Server] → Process and respond
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18, Vite, Recharts, react-simple-maps, Framer Motion |
| Backend | Python FastAPI, Uvicorn, Pydantic |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| IaC | Terraform (AWS), Kubernetes manifests |
| Monitoring | Prometheus, Grafana |

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** >= 18
- **Python** >= 3.11
- **Docker** & **Docker Compose** (for containerized setup)

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/user/cloud-routing-simulator.git
cd cloud-routing-simulator

# Start the backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

### Option 2: Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Access:
# Frontend:   http://localhost:3000
# Backend:    http://localhost:8000/docs
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3001 (admin/admin)
```

### Option 3: Kubernetes

```bash
# Apply manifests
kubectl apply -f infrastructure/kubernetes/

# Check status
kubectl get pods -l app=routing-sim
```

---

## 📡 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulate` | Run single routing simulation |
| `POST` | `/api/simulate/batch` | Compare all 4 routing modes |
| `POST` | `/api/simulate/traffic-spike` | Simulate traffic surge |
| `GET` | `/api/regions` | List all regions & edge locations |
| `POST` | `/api/regions/{code}/toggle` | Toggle region up/down |
| `GET` | `/api/metrics` | Current metrics snapshot |
| `GET` | `/api/metrics/prometheus` | Prometheus-format metrics |
| `POST` | `/api/recommend` | Get AI routing recommendation |

---

## 🗺️ Features

### Interactive World Map
- Visualize AWS regions and CloudFront edge locations
- Animated routing path from user → edge → server
- Color-coded region health status
- Click to select user location

### Real-time Comparison
- Side-by-side latency and cost comparison across all 4 routing modes
- Latency reduction percentage (up to 64%)
- Cost savings analysis

### Monitoring Dashboard
- Prometheus-compatible metrics export
- Grafana dashboard included
- Real-time latency P50/P95/P99
- Cache hit ratio tracking
- Per-region load visualization

### AI Recommendations
- Weighted scoring engine analyzing traffic patterns
- Recommends optimal routing strategy
- Predicts cost savings
- Confidence-scored reasoning

### Failure Simulation
- Toggle any region on/off
- Watch automatic traffic rerouting
- Degradation mode (increased latency)

### Traffic Spike Simulation
- Configure spike multiplier
- See auto-scaling response
- Compare latency during vs after scaling

---

## 📂 Project Structure

```
cloud-routing-simulator/
├── frontend/              # React + Vite application
├── backend/               # Python FastAPI service
├── infrastructure/
│   ├── terraform/         # AWS IaC (VPC, ALB, CloudFront, GA, ECS)
│   └── kubernetes/        # K8s deployment manifests
├── monitoring/
│   ├── prometheus/        # Scrape configuration
│   └── grafana/           # Dashboard definitions
├── .github/workflows/     # CI/CD pipelines
├── docker-compose.yml     # Full stack orchestration
└── docs/                  # Project documentation
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend build verification
cd frontend
npm run build
```

---

## 🔧 Infrastructure as Code

### Terraform Modules

| Module | Description |
|--------|-------------|
| `vpc` | VPC with public/private subnets across 2 AZs |
| `alb` | Application Load Balancer with health checks |
| `cloudfront` | CloudFront CDN distribution |
| `global-accelerator` | AWS Global Accelerator with endpoint groups |
| `ecs` | ECS Fargate service with circuit breaker deployment |

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

---

## 📊 CI/CD Pipeline

### CI (on Pull Request)
1. ✅ Python lint (ruff) + tests (pytest)
2. ✅ Node.js build verification
3. ✅ Docker image build test

### CD (on merge to main)
1. 🔨 Build Docker images
2. 📦 Push to GHCR
3. 🚀 Rolling deployment
4. ❤️ Health check verification
5. 🔄 Automatic rollback on failure

---

## 📝 License

This project is developed for educational and demonstration purposes.

---

<div align="center">
  Built with ❤️ for DevOps excellence
</div>
