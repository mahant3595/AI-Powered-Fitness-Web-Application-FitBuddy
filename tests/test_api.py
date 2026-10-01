from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
