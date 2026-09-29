import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def _client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. Add your Gemini API key to .env."
        )

    return genai.Client(
        api_key=api_key,
       http_options={"api_version": "v1beta"}
    )


def _model_name():
    return os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-3.1-pro-preview"
    )


def generate_workout_gemini(username, age, weight, goal, intensity):
    client = _client()

    prompt = f"""
You are FitBuddy, an AI fitness plan generator.

Create a personalized 7-day fitness plan for:

Name: {username}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}

Requirements:
- Provide all 7 days.
- Give each day a clear fitness focus.
- Include warm-up.
- Include main workout exercises.
- Include sets/repetitions or duration.
- Include rest intervals.
- Include cooldown/recovery.
- Include appropriate rest/recovery days.
- Keep the plan practical and easy to understand.
- Do not diagnose medical conditions.
- Do not prescribe medication.
- Do not recommend dangerous or extreme exercise.

Use this format:

DAY 1 - FOCUS
Warm-up:
Main Workout:
1. Exercise - sets/reps/duration
2. Exercise - sets/reps/duration
Rest:
Cooldown/Recovery:

Repeat through DAY 7.

Return only the fitness plan.
"""

    response = client.models.generate_content(
        model=_model_name(),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=5000
        )
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty workout plan.")

    return response.text
