from fastapi.testclient import TestClient

from app.main import app
from app.services.gemini_service import get_selected_gemini_model

client = TestClient(app)


def test_selected_gemini_model_defaults_to_balanced_option():
    assert get_selected_gemini_model() in {"gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"}


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_page_loads():
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
    response = client.get(f"/dashboard/{user_id}")
    assert response.status_code == 200


def test_result_and_admin_pages_load():
    payload = {
        "name": "Jordan",
        "age": 28,
        "weight": 75,
        "fitness_goal": "General Wellness",
        "workout_intensity": "low",
        "experience_level": "Intermediate",
        "preferred_workout": "Cardio",
        "available_time": 30,
    }
    create_response = client.post("/api/users", json=payload)
    user_id = create_response.json()["id"]

    result_response = client.get(f"/result/{user_id}")
    assert result_response.status_code == 200

    admin_response = client.get("/admin/users")
    assert admin_response.status_code == 200
