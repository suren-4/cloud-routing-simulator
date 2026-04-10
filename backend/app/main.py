"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import simulation, regions, monitoring, recommendation

app = FastAPI(
    title="Cloud Routing Simulator API",
    description="Intelligent Multi-Region Load Routing Simulator with Cost Optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(simulation.router)
app.include_router(regions.router)
app.include_router(monitoring.router)
app.include_router(recommendation.router)


@app.get("/")
async def root():
    return {
        "name": "Cloud Routing Simulator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
