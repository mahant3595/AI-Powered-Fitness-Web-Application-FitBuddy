from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import NutritionTipRequest
from app.services.gemini_service import generate_nutrition_tip

router = APIRouter(prefix="/api", tags=["tips"])


@router.post(
    "/tips/nutrition",
    summary="Generate a nutrition and recovery tip",
    description="Create a concise, goal-based nutrition and recovery recommendation based on the user's selected fitness objective.")
def generate_tip(payload: NutritionTipRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "goal": user.fitness_goal,
        "tip": generate_nutrition_tip(user.fitness_goal),
        "disclaimer": "FitBuddy provides general fitness and wellness information for educational purposes. It is not a substitute for advice from a qualified healthcare or fitness professional. Consider your individual health conditions and consult a professional when appropriate.",
    }
