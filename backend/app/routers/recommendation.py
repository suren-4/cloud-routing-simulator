"""AI recommendation API routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.ai_recommender import ai_recommender

router = APIRouter(prefix="/api/recommend", tags=["recommendation"])


class RecommendRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    traffic_rps: float = Field(default=100, ge=1, le=10000)


@router.post("")
async def get_recommendation(req: RecommendRequest):
    """Get AI-based routing recommendation."""
    return ai_recommender.analyze_and_recommend(
        req.latitude, req.longitude, req.traffic_rps
    )


@router.get("/savings")
async def predict_savings(rps: float = 100):
    """Predict cost savings for different strategies."""
    return ai_recommender.predict_savings(rps)
