from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import User, WorkoutPlan
from app.routes.tips import router as tips_router
from app.routes.users import router as users_router
from app.routes.workouts import router as workouts_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FitBuddy",
    description="AI-powered fitness assistant for personalized workouts and wellness guidance.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(users_router)
app.include_router(workouts_router)
app.include_router(tips_router)

env = Environment(loader=FileSystemLoader("app/templates"))


def render_template(name: str, **context):
    template = env.get_template(name)
    return HTMLResponse(template.render(**context))


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok", "message": "FitBuddy is running."}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render_template("index.html", request=request)


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return render_template("profile.html", request=request)


@app.get("/dashboard/{user_id}", response_class=HTMLResponse)
async def dashboard_page(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    latest_plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.version.desc(), WorkoutPlan.updated_at.desc()).first()
    history = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.version.desc()).all()

    user_data = {
        "id": user.id,
        "name": user.name,
        "fitness_goal": user.fitness_goal,
        "workout_intensity": user.workout_intensity,
        "created_at": user.created_at,
    }
    plan_data = latest_plan.plan_data if latest_plan else None
    history_data = [
        {"version": item.version, "created_at": item.created_at, "feedback": item.feedback}
        for item in history
    ]

    return render_template(
        "dashboard.html",
        request=request,
        user=user_data,
        plan={"plan_data": plan_data} if plan_data else None,
        history=history_data,
    )


@app.get("/history/{user_id}", response_class=HTMLResponse)
async def history_page(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    history = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.version.desc()).all()
    user_data = {"id": user.id, "name": user.name}
    history_data = [
        {"version": item.version, "created_at": item.created_at, "feedback": item.feedback}
        for item in history
    ]
    return render_template("history.html", request=request, user=user_data, history=history_data)
