from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_workout_plan():
    payload = {
        "name": "Alex",
        "age": 21,
        "weight": 70,
        "fitness_goal": "Muscle Gain",
        "workout_intensity": "medium",
        "experience_level": "Beginner",
        "preferred_workout": "Strength Training",
        "available_time": 45,
    }
    create_response = client.post("/api/users", json=payload)
    user_id = create_response.json()["id"]

    with patch("app.routes.workouts.generate_workout_plan") as mock_generate:
        mock_generate.return_value = {
            "goal": "Muscle Gain",
            "intensity": "medium",
            "days": [
                {"day": "Day 1", "focus": "Upper Body", "exercises": [{"name": "Push-ups", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Good push day."},
                {"day": "Day 2", "focus": "Lower Body", "exercises": [{"name": "Squats", "sets": 3, "reps": 12, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great for lower body strength."},
                {"day": "Day 3", "focus": "Recovery", "exercises": [{"name": "Stretching", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Recovery day."},
                {"day": "Day 4", "focus": "Upper Body", "exercises": [{"name": "Rows", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Back and shoulders."},
                {"day": "Day 5", "focus": "Lower Body", "exercises": [{"name": "Lunges", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Leg focus."},
                {"day": "Day 6", "focus": "Recovery", "exercises": [{"name": "Mobility", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Keep moving."},
                {"day": "Day 7", "focus": "Full Body", "exercises": [{"name": "Circuit", "sets": 3, "reps": 8, "rest_seconds": 60}], "duration_minutes": 40, "rest_period": "60 seconds", "explanation": "Finish strong."},
            ],
        }
        response = client.post("/api/workouts/generate", json={"user_id": user_id})
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
        assert len(data["plan_data"]["days"]) == 7


def test_refine_workout_plan():
    payload = {
        "name": "Alex",
        "age": 21,
        "weight": 70,
        "fitness_goal": "Muscle Gain",
        "workout_intensity": "medium",
        "experience_level": "Beginner",
        "preferred_workout": "Strength Training",
        "available_time": 45,
    }
    create_response = client.post("/api/users", json=payload)
    user_id = create_response.json()["id"]

    with patch("app.routes.workouts.generate_workout_plan") as mock_generate:
        mock_generate.return_value = {
            "goal": "Muscle Gain",
            "intensity": "medium",
            "days": [
                {"day": "Day 1", "focus": "Upper Body", "exercises": [{"name": "Push-ups", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Good push day."},
                {"day": "Day 2", "focus": "Lower Body", "exercises": [{"name": "Squats", "sets": 3, "reps": 12, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great for lower body strength."},
                {"day": "Day 3", "focus": "Recovery", "exercises": [{"name": "Stretching", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Recovery day."},
                {"day": "Day 4", "focus": "Upper Body", "exercises": [{"name": "Rows", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Back and shoulders."},
                {"day": "Day 5", "focus": "Lower Body", "exercises": [{"name": "Lunges", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Leg focus."},
                {"day": "Day 6", "focus": "Recovery", "exercises": [{"name": "Mobility", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Keep moving."},
                {"day": "Day 7", "focus": "Full Body", "exercises": [{"name": "Circuit", "sets": 3, "reps": 8, "rest_seconds": 60}], "duration_minutes": 40, "rest_period": "60 seconds", "explanation": "Finish strong."},
            ],
        }
        client.post("/api/workouts/generate", json={"user_id": user_id})

        with patch("app.routes.workouts.refine_workout_plan") as mock_refine:
            mock_refine.return_value = {
                "goal": "Muscle Gain",
                "intensity": "medium",
                "days": [
                    {"day": "Day 1", "focus": "Upper Body + Cardio", "exercises": [{"name": "Push-ups", "sets": 3, "reps": 12, "rest_seconds": 60}], "duration_minutes": 40, "rest_period": "60 seconds", "explanation": "Added cardio."},
                    {"day": "Day 2", "focus": "Lower Body", "exercises": [{"name": "Squats", "sets": 3, "reps": 12, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great for lower body strength."},
                    {"day": "Day 3", "focus": "Recovery", "exercises": [{"name": "Stretching", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Recovery day."},
                    {"day": "Day 4", "focus": "Upper Body", "exercises": [{"name": "Rows", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Back and shoulders."},
                    {"day": "Day 5", "focus": "Lower Body", "exercises": [{"name": "Lunges", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Leg focus."},
                    {"day": "Day 6", "focus": "Recovery", "exercises": [{"name": "Mobility", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Keep moving."},
                    {"day": "Day 7", "focus": "Full Body", "exercises": [{"name": "Circuit", "sets": 3, "reps": 8, "rest_seconds": 60}], "duration_minutes": 40, "rest_period": "60 seconds", "explanation": "Finish strong."},
                ]
            }
            response = client.post("/api/workouts/refine", json={"user_id": user_id, "feedback": "Add more upper-body exercises and include one additional rest day."})
            assert response.status_code == 200
            data = response.json()
            assert data["feedback"] == "Add more upper-body exercises and include one additional rest day."


def test_get_plan_by_id():
    payload = {
        "name": "Alex",
        "age": 21,
        "weight": 70,
        "fitness_goal": "Muscle Gain",
        "workout_intensity": "medium",
        "experience_level": "Beginner",
        "preferred_workout": "Strength Training",
        "available_time": 45,
    }
    user_response = client.post("/api/users", json=payload)
    user_id = user_response.json()["id"]

    with patch("app.routes.workouts.generate_workout_plan") as mock_generate:
        mock_generate.return_value = {
            "goal": "Muscle Gain",
            "intensity": "medium",
            "days": [
                {"day": "Day 1", "focus": "Upper Body", "exercises": [{"name": "Push-ups", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great plan."},
                {"day": "Day 2", "focus": "Lower Body", "exercises": [{"name": "Squats", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great plan."},
                {"day": "Day 3", "focus": "Recovery", "exercises": [{"name": "Stretching", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Recovery."},
                {"day": "Day 4", "focus": "Upper Body", "exercises": [{"name": "Rows", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great plan."},
                {"day": "Day 5", "focus": "Lower Body", "exercises": [{"name": "Lunges", "sets": 3, "reps": 10, "rest_seconds": 60}], "duration_minutes": 35, "rest_period": "60 seconds", "explanation": "Great plan."},
                {"day": "Day 6", "focus": "Recovery", "exercises": [{"name": "Mobility", "sets": 2, "reps": 10, "rest_seconds": 30}], "duration_minutes": 20, "rest_period": "30 seconds", "explanation": "Recovery."},
                {"day": "Day 7", "focus": "Full Body", "exercises": [{"name": "Circuit", "sets": 3, "reps": 8, "rest_seconds": 60}], "duration_minutes": 40, "rest_period": "60 seconds", "explanation": "Strong finish."},
            ],
        }
        gen = client.post("/api/workouts/generate", json={"user_id": user_id})
        plan_id = gen.json()["id"]
        response = client.get(f"/api/workouts/plan/{plan_id}")
        assert response.status_code == 200
        assert response.json()["id"] == plan_id


def test_nutrition_tip_endpoint():
    payload = {
        "name": "Alex",
        "age": 21,
        "weight": 70,
        "fitness_goal": "Muscle Gain",
        "workout_intensity": "medium",
        "experience_level": "Beginner",
        "preferred_workout": "Strength Training",
        "available_time": 45,
    }
    create_response = client.post("/api/users", json=payload)
    user_id = create_response.json()["id"]

    with patch("app.routes.tips.generate_nutrition_tip") as mock_tip:
        mock_tip.return_value = "Include a protein-rich food in your post-workout meal and stay hydrated to support muscle recovery."
        response = client.post("/api/tips/nutrition", json={"user_id": user_id})
        assert response.status_code == 200
        data = response.json()
        assert "protein" in data["tip"].lower()
