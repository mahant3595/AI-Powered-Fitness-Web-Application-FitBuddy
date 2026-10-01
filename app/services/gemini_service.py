from __future__ import annotations

import json
import os
import warnings
from typing import Any

from dotenv import load_dotenv

try:
    from google import genai as google_genai
except ImportError:  # pragma: no cover - compatibility for older environments
    google_genai = None

if google_genai is None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, module="google")
        try:
            from google import generativeai as genai
        except ImportError:  # pragma: no cover - compatibility for newer environments
            genai = None
else:
    genai = None

from app.models import User

load_dotenv()

GEMINI_MODEL_OPTIONS = {
    "gemini-2.0-flash": "Best for fast, responsive plan generation and lower-latency user interactions.",
    "gemini-1.5-flash": "Balanced default with strong structured output and broad compatibility.",
    "gemini-2.5-flash": "Good for richer reasoning and more nuanced coaching feedback.",
    "gemini-2.5-pro": "Best for deep reasoning and complex prompt chains, but slower and more expensive.",
}


def get_selected_gemini_model() -> str:
    configured = (os.getenv("GEMINI_MODEL") or os.getenv("GOOGLE_GENAI_MODEL") or "gemini-1.5-flash").strip()
    normalized = configured.lower()
    if normalized in GEMINI_MODEL_OPTIONS:
        return normalized
    if normalized.startswith("gemini-"):
        return normalized
    return "gemini-1.5-flash"


def _fallback_nutrition_tip(goal: str) -> str:
    tips = {
        "Weight Loss": "Include a lean protein and plenty of vegetables in your meals, stay hydrated, and prioritize consistent sleep to support recovery and fat loss.",
        "Muscle Gain": "Add a protein-rich food to your post-workout meal, keep hydration steady, and aim for quality sleep to support muscle repair and growth.",
        "General Wellness": "Focus on balanced meals, regular hydration, daily movement, and restorative sleep to support long-term energy and well-being.",
    }
    return tips.get(goal, tips["General Wellness"])


def _fallback_workout_plan(user: User, feedback: str | None = None) -> dict[str, Any]:
    goal = user.fitness_goal
    intensity = user.workout_intensity
    duration = user.available_time
    focus_map = {
        "Weight Loss": [
            "Cardio Conditioning",
            "Lower Body Burn",
            "Core & Mobility",
            "Full Body Circuit",
            "HIIT Recovery",
            "Strength + Cardio",
            "Recovery & Mobility",
        ],
        "Muscle Gain": [
            "Upper Body Strength",
            "Lower Body Power",
            "Push + Pull",
            "Leg Day",
            "Full Body Hypertrophy",
            "Back & Core",
            "Recovery & Mobility",
        ],
        "General Wellness": [
            "Balanced Movement",
            "Strength Stability",
            "Cardio Flow",
            "Core & Mobility",
            "Full Body Circuit",
            "Recovery & Mobility",
            "Mindful Recovery",
        ],
    }
    exercise_map = {
        "Weight Loss": [
            ["Brisk Walk", "Bodyweight Squats", "Mountain Climbers"],
            ["Lunges", "Jump Rope", "Plank"],
            ["Step-ups", "Burpees", "Glute Bridges"],
            ["Cycling Intervals", "Push-ups", "Dead Bug"],
            ["Fast Marching", "Split Squats", "Bear Crawls"],
            ["Kettlebell Swings", "Rowing", "Reverse Lunges"],
            ["Stretching Flow", "Breathing Exercises", "Light Walk"],
        ],
        "Muscle Gain": [
            ["Push-ups", "Dumbbell Rows", "Shoulder Press"],
            ["Goblet Squats", "Romanian Deadlifts", "Walking Lunges"],
            ["Bench Press or Incline Push-ups", "Lat Pulldown", "Planks"],
            ["Deadlifts", "Bulgarian Split Squats", "Hollow Holds"],
            ["Pull-ups", "Overhead Press", "Farmer Carries"],
            ["Leg Press", "Bent-over Rows", "Side Planks"],
            ["Light Stretching", "Band Work", "Mobility Flow"],
        ],
        "General Wellness": [
            ["Brisk Walk", "Bodyweight Squats", "Wall Slides"],
            ["Resistance Band Rows", "Reverse Lunges", "Bird Dogs"],
            ["Light Cardio", "Push-ups", "Stretching"],
            ["Step-ups", "Plank", "Hip Openers"],
            ["Bodyweight Circuit", "Mobility Flow", "Shadow Boxing"],
            ["Pilates Core", "Gentle Rows", "Hamstring Stretch"],
            ["Yoga Flow", "Breathing", "Recovery Walk"],
        ],
    }

    days = []
    for idx, focus in enumerate(focus_map[goal], start=1):
        exercises = []
        for name in exercise_map[goal][idx - 1]:
            sets = 3 if intensity in {"medium", "high"} else 2
            reps = 8 if goal == "Muscle Gain" else 10
            exercises.append({
                "name": name,
                "sets": sets,
                "reps": reps,
                "rest_seconds": 60 if intensity != "low" else 75,
            })
        workout_minutes = duration if duration in {15, 30, 45, 60} else 30
        if intensity == "low":
            workout_minutes = min(workout_minutes, 30)
        elif intensity == "medium":
            workout_minutes = max(30, min(workout_minutes, 45))
        else:
            workout_minutes = max(30, min(workout_minutes, 60))
        explanation = "This session supports your recovery and training quality while keeping the workload sustainable."
        if feedback:
            explanation = f"Updated based on your feedback: {feedback}."
        days.append({
            "day": f"Day {idx}",
            "focus": focus,
            "exercises": exercises,
            "duration_minutes": workout_minutes,
            "rest_period": "60 seconds between sets",
            "explanation": explanation,
        })

    return {"goal": goal, "intensity": intensity, "days": days}


def _clean_response_text(raw: str) -> str:
    if not raw:
        return ""
    text = raw.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _parse_json_response(raw: str) -> dict:
    cleaned = _clean_response_text(raw)
    if not cleaned:
        raise ValueError("AI response was empty.")
    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise ValueError("AI response was not a JSON object.")
    return payload


def _call_gemini(prompt: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    model_name = get_selected_gemini_model()

    if google_genai is not None:
        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"temperature": 0.4, "top_p": 0.9},
        )
        if hasattr(response, "text"):
            return response.text
        if hasattr(response, "candidates"):
            first = response.candidates[0]
            if hasattr(first, "content") and hasattr(first.content, "parts"):
                return "".join(part.text for part in first.content.parts if hasattr(part, "text"))
        return ""

    if genai is None:
        raise RuntimeError("Google AI SDK is not available.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt, generation_config={"temperature": 0.4, "top_p": 0.9})
    return getattr(response, "text", "") or ""


def generate_workout_plan(user: User, feedback: str | None = None) -> dict:
    prompt = f"""
    You are a helpful fitness coach. Generate a structured 7-day fitness plan in valid JSON only.
    Goal: {user.fitness_goal}
    Intensity: {user.workout_intensity}
    Experience: {user.experience_level}
    Preferred workout: {user.preferred_workout}
    Available time: {user.available_time} minutes
    Requirements:
    - Return a JSON object with keys: goal, intensity, days.
    - Exactly 7 days.
    - Each day must have: day, focus, exercises, duration_minutes, rest_period, explanation.
    - Every exercise must include: name, sets, reps, rest_seconds.
    - Include rest/recovery days where appropriate.
    - Keep the plan realistic for the user's experience and the selected intensity.
    - Use no Markdown fences and no extra text.
    """
    if feedback:
        prompt += f"\nUser feedback: {feedback}. Preserve useful parts of the original plan and improve according to the feedback."

    try:
        response_text = _call_gemini(prompt)
        payload = _parse_json_response(response_text)
        if not isinstance(payload.get("days"), list) or len(payload["days"]) != 7:
            raise ValueError("Invalid 7-day structure.")
        return payload
    except Exception:
        return _fallback_workout_plan(user, feedback=feedback)


def generate_nutrition_tip(goal: str) -> str:
    prompt = f"""
    Give a concise, practical nutrition and recovery tip for a user with the goal '{goal}'.
    Keep it to 1-2 sentences and avoid extreme diet advice or medical advice.
    Use plain language and include hydration and recovery guidance.
    """
    try:
        response_text = _call_gemini(prompt)
        if response_text.strip():
            return response_text.strip().replace("```", "").strip()
    except Exception:
        pass
    return _fallback_nutrition_tip(goal)


def refine_workout_plan(user: User, current_plan: dict, feedback: str) -> dict:
    prompt = f"""
    You are a fitness coach revising a 7-day workout plan using the user's feedback.
    Goal: {user.fitness_goal}
    Intensity: {user.workout_intensity}
    Feedback: {feedback}
    Current plan: {json.dumps(current_plan, ensure_ascii=False)}
    Requirement: return valid JSON with keys goal, intensity, and a 7-day list under 'days'.
    Preserve useful parts of the original plan while making targeted changes.
    """
    try:
        response_text = _call_gemini(prompt)
        payload = _parse_json_response(response_text)
        if not isinstance(payload.get("days"), list) or len(payload["days"]) != 7:
            raise ValueError("Refined plan response was invalid.")
        return payload
    except Exception:
        return _fallback_workout_plan(user, feedback=feedback)
