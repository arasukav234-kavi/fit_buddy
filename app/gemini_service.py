import logging
from .config import GEMINI_API_KEY, GEMINI_WORKOUT_MODEL, GEMINI_TIP_MODEL

logger = logging.getLogger(__name__)
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def _call(model: str, prompt: str):
    if not GEMINI_API_KEY or genai is None:
        raise RuntimeError("Gemini API is not configured.")
    cfg = types.GenerateContentConfig(temperature=0.5, max_output_tokens=5000) if types else None
    response = genai.Client(api_key=GEMINI_API_KEY).models.generate_content(
        model=model, contents=prompt, config=cfg
    )
    text = getattr(response, "text", "")
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()


def demo_workout(name, age, weight, goal, intensity):
    return f"""FITBUDDY 7-DAY PLAN FOR {name.upper()}

Age: {age}
Weight: {weight} kg
Goal: {goal.title()}
Intensity: {intensity.title()}

DAY 1 - FULL BODY
Squats 3x10; incline push-ups 3x8; glute bridges 3x12; plank 3x20-30 sec.

DAY 2 - CARDIO + CORE
Brisk walking/cycling 25 min; dead bug 3x10 each side; bird dog 3x10 each side.

DAY 3 - RECOVERY
Easy walking 20-30 min and gentle mobility.

DAY 4 - STRENGTH
Lunges 3x8 each side; rows 3x10; hip hinge 3x10; side plank 2x20 sec.

DAY 5 - CARDIO
25-35 minutes moderate walking, cycling or light jogging.

DAY 6 - FULL BODY
Sit-to-stand 3x12; wall push-ups 3x10; step-ups 3x8 each side; plank 3x20 sec.

DAY 7 - REST / ACTIVE RECOVERY
Easy walking, gentle mobility and stretching.

SAFETY
Stop if you experience sharp pain, dizziness, chest pain or unusual shortness of breath."""


def generate_workout_gemini(name, age, weight, goal, intensity):
    prompt = f"""Create a practical personalized 7-day workout plan.
Name: {name}; Age: {age}; Weight: {weight} kg; Goal: {goal}; Intensity: {intensity}.
Return Day 1 through Day 7. Include focus, warm-up, main workout, sets/reps or duration, rest and cooldown. Include a recovery/rest day. Do not diagnose conditions or prescribe medical treatment."""
    try:
        return _call(GEMINI_WORKOUT_MODEL, prompt)
    except Exception as exc:
        logger.warning("Gemini workout generation failed: %s", exc)
        if GEMINI_API_KEY:
            raise
        return demo_workout(name, age, weight, goal, intensity)


def demo_tip(goal):
    return {
        "weight loss": "Build meals around vegetables, protein, high-fiber carbohydrates and water. Avoid extreme restriction.",
        "muscle gain": "Include a protein source in regular meals and stay hydrated. Pair strength training with enough food and recovery.",
        "general wellness": "Aim for balanced meals, adequate fluids, varied fruits and vegetables, and consistent sleep.",
        "flexibility": "Choose varied whole foods and stay hydrated. Sleep and gentle mobility can complement flexibility work."
    }.get(goal.lower(), "Choose balanced meals, enough water, and consistent sleep and recovery.")


def generate_nutrition_tip_with_flash(goal):
    prompt = f"Give one concise 3-5 sentence practical general nutrition or recovery tip for this fitness goal: {goal}. No diagnosis, extreme diets, or medical treatment claims."
    try:
        return _call(GEMINI_TIP_MODEL, prompt)
    except Exception as exc:
        logger.warning("Gemini nutrition generation failed: %s", exc)
        if GEMINI_API_KEY:
            raise
        return demo_tip(goal)


def update_workout_plan(original_plan, feedback, goal, intensity):
    prompt = f"""Revise this complete 7-day fitness plan using user feedback.
Goal: {goal}
Intensity: {intensity}

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Return a complete revised Day 1-Day 7 plan, include warm-up/cooldown and at least one rest day.
Do not diagnose or provide medical treatment."""

    try:
        return _call(GEMINI_WORKOUT_MODEL, prompt)
    except Exception as exc:
        logger.warning("Gemini plan update failed: %s", exc)
        if GEMINI_API_KEY:
            raise
        return original_plan + "\n\nUPDATED FROM FEEDBACK - DEMO MODE\n" + feedback
