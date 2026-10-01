from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_user():
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
    response = client.post("/api/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alex"
    assert data["fitness_goal"] == "Muscle Gain"


def test_missing_user_returns_404():
    response = client.get("/api/users/99999")
    assert response.status_code == 404


def test_invalid_user_input():
    payload = {"name": " ", "age": 8, "weight": -1, "fitness_goal": "Invalid", "workout_intensity": "extreme"}
    response = client.post("/api/users", json=payload)
    assert response.status_code == 422
