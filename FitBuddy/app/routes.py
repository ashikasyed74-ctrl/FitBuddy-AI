from typing import Literal

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import (
    delete_user,
    get_all_users,
    get_db,
    get_original_plan,
    get_user,
    get_user_plan,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: Literal[
        "weight loss",
        "muscle gain",
        "general wellness",
        "flexibility"
    ]
    intensity: Literal["low", "medium", "high"]


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    feedback: str = Field(min_length=1, max_length=2000)


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": None}
    )


@router.post("/generate-workout")
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username.strip(),
            user_id=user_id.strip(),
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        if get_user(db, data.user_id):
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "User ID already exists. Please use another User ID."
                },
            )

        workout_plan = generate_workout_gemini(
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )

        nutrition_tip = generate_nutrition_tip_with_flash(data.goal)

        save_user(
            db,
            data.user_id,
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )

        save_plan(
            db,
            data.user_id,
            workout_plan,
            nutrition_tip,
        )

        user = get_user(db, data.user_id)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "message": None,
            },
        )

    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
        )


@router.post("/submit-feedback")
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(
            user_id=user_id.strip(),
            feedback=feedback.strip(),
        )

        user = get_user(db, data.user_id)

        if not user:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"error": "User ID not found."},
            )

        original_plan = get_original_plan(db, data.user_id)

        if not original_plan:
            raise RuntimeError("Original workout plan was not found.")

        revised_plan = update_workout_plan(
            original_plan,
            data.feedback,
        )

        new_tip = generate_nutrition_tip_with_flash(user.goal)

        update_plan(
            db,
            data.user_id,
            revised_plan,
            new_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": revised_plan,
                "nutrition_tip": new_tip,
                "message": "Your workout plan has been updated successfully.",
            },
        )

    except Exception as exc:
        user = get_user(db, user_id)
        plan = get_user_plan(db, user_id)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": plan.original_plan if plan else "",
                "nutrition_tip": plan.nutrition_tip if plan else "",
                "message": f"Unable to update the plan: {exc}",
            },
        )


@router.get("/view-all-users")
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    users = get_all_users(db)

    user_plans = {
        user.user_id: get_user_plan(db, user.user_id)
        for user in users
    }

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "user_plans": user_plans,
        },
    )


@router.post("/delete-user/{user_id}")
def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    delete_user(db, user_id)
    return RedirectResponse(
        url="/view-all-users",
        status_code=303,
    )
