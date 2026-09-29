# FitBuddy - AI Fitness Plan Generator

## Stack
- FastAPI
- Jinja2
- SQLite
- SQLAlchemy
- Google GenAI Python SDK (`google-genai`)
- Gemini Pro-role model for workout generation and plan revision
- Gemini Flash model for nutrition/recovery tips

## Run on Windows

```powershell
python -m venv fitbuddy-env
fitbuddy-env\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Google Gemini API key.

Then:

```powershell
uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000

API docs:

http://127.0.0.1:8000/docs

## Main routes

GET /
POST /generate-workout
POST /submit-feedback
GET /view-all-users
POST /delete-user/{user_id}

## AI configuration

The model names are controlled from `.env` so they can be changed without modifying Python code.

Current defaults:
- GEMINI_PRO_MODEL=gemini-3.1-pro-preview
- GEMINI_FLASH_MODEL=gemini-3.8-flash
