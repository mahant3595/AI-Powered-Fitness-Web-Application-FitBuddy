from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WorkoutPlan
from app.schemas import WorkoutGenerateRequest, WorkoutPlanResponse, WorkoutRefineRequest
from app.services.gemini_service import generate_workout_plan, refine_workout_plan

router = APIRouter(prefix="/api", tags=["workouts"])


@router.post(
    "/workouts/generate",
    response_model=WorkoutPlanResponse,
    summary="Generate a personalized workout plan",
    description="Create a new 7-day workout plan using the user's fitness profile and AI-generated guidance.")
def generate_plan(payload: WorkoutGenerateRequest, db: Session = Depends(get_db)) -> WorkoutPlan:
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    plan_data = generate_workout_plan(user)
    latest = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).order_by(WorkoutPlan.version.desc()).first()
    version = (latest.version if latest else 0) + 1
    new_plan = WorkoutPlan(user_id=user.id, plan_data=plan_data, version=version, feedback=None)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


@router.get(
    "/workouts/{user_id}",
    response_model=WorkoutPlanResponse,
    summary="Get the latest workout plan",
    description="Retrieve the newest workout plan a user has generated or refined.")
def get_current_plan(user_id: int, db: Session = Depends(get_db)) -> WorkoutPlan:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.version.desc(), WorkoutPlan.updated_at.desc()).first()
    if not plan:
        raise HTTPException(status_code=404, detail="No workout plan found for this user.")
    return plan


@router.get(
    "/workouts/{user_id}/history",
    response_model=list[WorkoutPlanResponse],
    summary="List all workout plans",
    description="Return the full version history of workout plans for a user.")
def get_plan_history(user_id: int, db: Session = Depends(get_db)) -> list[WorkoutPlan]:
    plans = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.version.desc()).all()
    return plans


@router.post(
    "/workouts/refine",
    response_model=WorkoutPlanResponse,
    summary="Refine a workout plan with feedback",
    description="Use the user's feedback to generate an updated 7-day plan while preserving useful parts of the current version.")
def refine_plan(payload: WorkoutRefineRequest, db: Session = Depends(get_db)) -> WorkoutPlan:
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    current = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).order_by(WorkoutPlan.version.desc(), WorkoutPlan.updated_at.desc()).first()
    if not current:
        raise HTTPException(status_code=404, detail="No workout plan to refine.")

    refreshed_plan = refine_workout_plan(user, current.plan_data, payload.feedback)
    new_plan = WorkoutPlan(user_id=user.id, plan_data=refreshed_plan, version=current.version + 1, feedback=payload.feedback)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan
