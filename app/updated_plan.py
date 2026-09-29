import os
import time

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
        "gemini-3.5-flash-lite"
    )


def update_workout_plan(original_plan, feedback):
    client = _client()

    prompt = f"""
You are FitBuddy.

Original 7-day workout plan:
---------------------------
{original_plan}
---------------------------

User feedback:
{feedback}

Create a revised 7-day plan based on the feedback.

Requirements:
- Preserve useful parts of the original plan.
- Apply reasonable requested changes.
- Keep all 7 days.
- Include warm-up, main workout, sets/reps or duration,
  rest intervals and cooldown/recovery.
- Add rest/recovery when appropriate.
- Do not diagnose medical conditions.
- Do not prescribe medication.
- Do not recommend dangerous or extreme exercise.

Return only the revised fitness plan.
"""

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=_model_name(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=5000
                )
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty updated plan."
                )

            return response.text

        except Exception as error:
            error_text = str(error)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < max_attempts - 1:
                    wait_time = 5 * (attempt + 1)
                    time.sleep(wait_time)
                    continue

            raise RuntimeError(
                f"Gemini updated-plan generation failed: {error}"
            )

    raise RuntimeError(
        "Gemini updated-plan generation failed after retries."
    )