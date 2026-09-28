# FitBuddy - AI Fitness Plan Generator

FastAPI + Jinja2 + SQLite + SQLAlchemy + Google GenAI application.

## Windows setup

py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload

Open http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs
Admin: http://127.0.0.1:8000/view-all-users
Default admin username: admin
Default admin password: change-this-password

For live Gemini generation, copy .env.example to .env and set GEMINI_API_KEY.
Without a key, the application uses demo fallback content.

Run tests:
python -m pytest -q
