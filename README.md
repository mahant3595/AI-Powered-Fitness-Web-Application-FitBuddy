# FitBuddy

FitBuddy is an AI-powered fitness assistant that creates personalized 7-day workout plans, suggests nutrition and recovery guidance, and refines plans based on user feedback.

## Features

- Personalized 7-day workout plans based on user profile inputs
- Goal-based fitness planning for weight loss, muscle gain, or general wellness
- Feedback-driven workout refinement
- Nutrition and recovery tips tailored to the selected goal
- Persistent SQLite data storage
- FastAPI REST API documentation at /docs
- Responsive HTML/CSS/JavaScript fitness dashboard

## Technology Stack

- Python
- FastAPI
- Google Gemini AI
- SQLite
- SQLAlchemy
- Pydantic
- HTML
- CSS
- JavaScript

## Gemini Model Selection Strategy

FitBuddy supports selecting the Gemini model through the `GEMINI_MODEL` environment variable so the app can balance latency, reasoning quality, and cost for different tasks.

Recommended defaults:

- `gemini-1.5-flash`: best default for FitBuddy; low latency and strong structured output for plan generation and nutrition recommendations.
- `gemini-2.0-flash`: strong option when the app needs very quick responses for dashboard interactions and iterative plan refinements.
- `gemini-2.5-flash`: useful for more nuanced coaching logic when plan updates need deeper reasoning.
- `gemini-2.5-pro`: best for highly complex coaching prompts, but slower and more expensive than the flash variants.

Core selection guidance:

- Workout plan generation: prefer `gemini-1.5-flash` or `gemini-2.0-flash`
- Feedback-based plan refinement: use `gemini-2.0-flash` or `gemini-2.5-flash`
- Nutrition/recovery guidance: `gemini-1.5-flash` is typically sufficient and cost-efficient

Example:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

## Installation

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy the example file and set your API key:

```bash
copy .env.example .env
```

```env
GEMINI_API_KEY=your_api_key_here
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

Open the app at:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Disclaimer

FitBuddy provides general fitness and wellness information for educational purposes only. It is not a substitute for advice from a qualified healthcare or fitness professional.
