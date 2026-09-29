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
        "GEMINI_FLASH_MODEL",
        "gemini-3.5-flash-lite"
    )


def generate_nutrition_tip_with_flash(goal):
    client = _client()

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Fitness goal: {goal}

Give one concise, practical nutrition or recovery tip appropriate for this goal.

Where useful, mention examples such as:
- chicken
- fish
- beans
- Greek yogurt
- vegetables
- fruits
- whole grains
- adequate hydration

Keep it short and actionable.
Do not diagnose medical conditions or prescribe medication.
"""

    response = client.models.generate_content(
        model=_model_name(),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.6,
            max_output_tokens=700
        )
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")

    return response.text