from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WorkoutPlan
from app.schemas import UserCreate, UserResponse, WorkoutPlanResponse

router = APIRouter(prefix="/api", tags=["users"])


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user profile",
    description="Create a user profile with the goals, workout preferences, and training details used to generate their personalized plan.")
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    db_user = User(
        name=user.name,
        age=user.age,
        weight=user.weight,
        fitness_goal=user.fitness_goal,
        workout_intensity=user.workout_intensity,
        experience_level=user.experience_level,
        preferred_workout=user.preferred_workout,
        available_time=user.available_time,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a user profile",
    description="Fetch the stored profile and preferences for a single user.")
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get(
    "/users/{user_id}/plans",
    response_model=list[WorkoutPlanResponse],
    summary="List a user's workout plans",
    description="Return every saved workout plan for the selected user, ordered from newest to oldest.")
def get_user_plan_history(user_id: int, db: Session = Depends(get_db)) -> list[WorkoutPlan]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.version.desc()).all()
