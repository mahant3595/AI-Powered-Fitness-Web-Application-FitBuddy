from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    age: int = Field(..., ge=10, le=100)
    weight: float = Field(..., gt=0)
    fitness_goal: Literal["Weight Loss", "Muscle Gain", "General Wellness"]
    workout_intensity: Literal["low", "medium", "high"]
    experience_level: Literal["Beginner", "Intermediate", "Advanced"] = "Beginner"
    preferred_workout: Literal["Cardio", "Strength Training", "Mixed", "Flexibility", "No Preference"] = "No Preference"
    available_time: Literal[15, 30, 45, 60] = 30

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        return value.strip()

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    weight: float
    fitness_goal: str
    workout_intensity: str
    experience_level: str
    preferred_workout: str
    available_time: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutGenerateRequest(BaseModel):
    user_id: int


class WorkoutRefineRequest(BaseModel):
    user_id: int
    feedback: str = Field(..., min_length=2)


class NutritionTipRequest(BaseModel):
    user_id: int


class WorkoutPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_data: dict
    version: int
    feedback: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class TipResponse(BaseModel):
    goal: str
    tip: str
    disclaimer: str
