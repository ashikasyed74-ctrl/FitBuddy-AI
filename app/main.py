from fastapi import FastAPI
from app.database import Base, engine
from app.routes import router

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI-powered personalized fitness plans using Gemini."
)

Base.metadata.create_all(bind=engine)
app.include_router(router)
