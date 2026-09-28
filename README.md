# FitBuddy - AI Fitness Plan Generator

FastAPI + Jinja2 + SQLite + SQLAlchemy + Google GenAI application that generates personalized 7-day fitness plans using Gemini AI.

## Features

- **AI Workout Plans**: Generate personalized 7-day workout plans using Google Gemini
- **Nutrition Tips**: Get AI-powered nutrition and recovery advice
- **Feedback System**: Submit feedback to revise workout plans
- **Admin Dashboard**: View all users and their plans (HTTP Basic Auth)
- **REST API**: JSON endpoints for programmatic access
- **Demo Mode**: Works without API key using built-in demo content
- **Responsive UI**: Mobile-friendly web interface

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Google GenAI (Gemini)
- **Templates**: Jinja2
- **Styling**: CSS3

## Project Structure

```
fit buddy_code_file/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Environment configuration
│   ├── database.py       # SQLAlchemy models and DB operations
│   ├── routes.py         # API and HTML routes
│   ├── schemas.py        # Pydantic validation schemas
│   ├── auth.py           # Admin authentication
│   └── gemini_service.py # Google Gemini AI integration
├── templates/
│   ├── index.html        # Home page with input form
│   ├── result.html       # Workout plan display
│   └── all_users.html    # Admin dashboard
├── static/
│   └── style.css         # Application styles
├── tests/
│   └── test_app.py       # Unit tests
├── data/                 # SQLite database directory
├── .env                  # Environment variables (not committed)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Python 3.9+
- pip

## Installation

1. Create a virtual environment:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and set your `GEMINI_API_KEY` for live AI generation.
   Without a key, the app uses demo fallback content.

## Running the Application

```bash
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

- **Home**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Admin**: http://127.0.0.1:8000/view-all-users

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Application name | FitBuddy - AI Fitness Plan Generator |
| `DATABASE_URL` | SQLite database path | `sqlite:///./data/fitbuddy.db` |
| `GEMINI_API_KEY` | Google Gemini API key | (empty — demo mode) |
| `GEMINI_WORKOUT_MODEL` | Model for workout plans | `gemini-3.8-flash` |
| `GEMINI_TIP_MODEL` | Model for nutrition tips | `gemini-3.8-flash` |
| `ADMIN_USERNAME` | Admin dashboard username | `admin` |
| `ADMIN_PASSWORD` | Admin dashboard password | `change-this-password` |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home page (HTML) |
| POST | `/generate-workout` | Generate workout plan (form) |
| POST | `/submit-feedback` | Submit feedback (form) |
| GET | `/view-all-users` | Admin dashboard (HTML) |
| POST | `/api/users` | Create user + plan (JSON) |
| GET | `/api/users/{user_id}` | Get user + plan (JSON) |
| POST | `/api/users/{user_id}/feedback` | Submit feedback (JSON) |
| GET | `/health` | Health check |

## Testing

```bash
python -m pytest tests/ -v
```

## Building for Production

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

- **Port already in use**: Change port with `--port 8001`
- **Gemini API errors**: Check your API key in `.env`
- **Database errors**: Ensure `data/` directory exists and is writable

## Known Limitations

- Demo mode generates generic plans (not personalized)
- No user authentication for regular users (only admin)
- SQLite is not suitable for high-concurrency production use
- No rate limiting on API endpoints

## Security Notes

- Always change default admin credentials in production
- Never commit `.env` files to version control
- Use HTTPS in production
- The admin endpoint uses HTTP Basic Auth — use strong passwords
