from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .auth import require_admin
from .database import get_all_users, get_db, get_latest_plan, get_user, save_plan, save_user, update_plan
from .gemini_service import generate_nutrition_tip_with_flash, generate_workout_gemini, update_workout_plan
from .schemas import FeedbackRequest, UserInput

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
router = APIRouter()


def user_dict(u):
    return {
        "user_id": u.user_id,
        "name": u.name,
        "age": u.age,
        "weight": u.weight,
        "goal": u.goal,
        "intensity": u.intensity,
        "created_at": u.created_at.isoformat(),
    }


def plan_dict(p):
    return {
        "id": p.id,
        "original_plan": p.original_plan,
        "updated_plan": p.updated_plan,
        "nutrition_tip": p.nutrition_tip,
        "feedback": p.feedback,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_form(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(user_id=user_id, name=name, age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "error": str(exc)})
    try:
        workout = generate_workout_gemini(data.name, data.age, data.weight, data.goal, data.intensity)
        tip = generate_nutrition_tip_with_flash(data.goal)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "error": "Gemini request failed: " + str(exc)})
    user = save_user(db, data.model_dump())
    plan = save_plan(db, user, workout, tip)
    return templates.TemplateResponse(request=request, name="result.html", context={"request": request, "user": user, "plan": plan})


@router.post("/submit-feedback", response_class=HTMLResponse)
def feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id.strip())
    if not user:
        return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "error": "User ID not found. Generate a plan first."})
    plan = get_latest_plan(db, user)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found")
    try:
        data = FeedbackRequest(feedback=feedback)
        revised = update_workout_plan(plan.original_plan, data.feedback, user.goal, user.intensity)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="result.html", context={"request": request, "user": user, "plan": plan, "message": "Could not update the plan: " + str(exc)})
    update_plan(db, plan, revised, data.feedback)
    return templates.TemplateResponse(request=request, name="result.html", context={"request": request, "user": user, "plan": plan, "message": "Your workout plan was updated."})


@router.get("/view-all-users", response_class=HTMLResponse)
def admin(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    rows = [(u, get_latest_plan(db, u)) for u in get_all_users(db)]
    return templates.TemplateResponse(request=request, name="all_users.html", context={"request": request, "rows": rows})


@router.post("/api/users")
def api_create(data: UserInput, db: Session = Depends(get_db)):
    try:
        workout = generate_workout_gemini(data.name, data.age, data.weight, data.goal, data.intensity)
        tip = generate_nutrition_tip_with_flash(data.goal)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    user = save_user(db, data.model_dump())
    plan = save_plan(db, user, workout, tip)
    return {"user": user_dict(user), "plan": plan_dict(plan)}


@router.get("/api/users/{user_id}")
def api_get(user_id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    plan = get_latest_plan(db, user)
    return {"user": user_dict(user), "plan": plan_dict(plan) if plan else None}


@router.post("/api/users/{user_id}/feedback")
def api_feedback(user_id: str, data: FeedbackRequest, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    plan = get_latest_plan(db, user)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found")
    revised = update_workout_plan(plan.original_plan, data.feedback, user.goal, user.intensity)
    update_plan(db, plan, revised, data.feedback)
    return {"user": user_dict(user), "plan": plan_dict(plan)}
