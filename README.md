# SecureQuest — Gamified Security Awareness Platform

## Stack
| Layer | Technology |
|-------|-----------|
| Database | PostgreSQL 16 |
| Backend API | Python FastAPI |
| Frontend | Python Flask + Jinja2 |
| Auth | JWT + Google OAuth2 |
| Container | Docker Compose |

## Quick Start

### 1. Configure environment
```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, FLASK_SECRET_KEY, and Google OAuth credentials
```

### 2. Start with Docker
```bash
docker-compose up --build
```

### 3. Seed the database (first run)
```bash
docker-compose exec backend python seed.py
```

This creates:
- Admin account: `admin@securequest.local` / `Admin1234!`
- Sample tournament with 5 challenges

### 4. Open the app
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Running without Docker (local dev)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Set DATABASE_URL in .env to point to your local Postgres
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

---

## Project Structure
```
GAME1/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, router wiring
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── user.py       # User, UserRole, SSOProvider
│   │   │   └── tournament.py # Tournament, Challenge, UserTournament, UserResponse
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── auth/
│   │   │   ├── jwt.py        # JWT creation, hashing, dependencies
│   │   │   └── oauth.py      # Google OAuth2 helpers
│   │   └── routers/
│   │       ├── auth.py       # /register /login /google /me
│   │       ├── tournaments.py# player tournament + challenge endpoints
│   │       ├── admin.py      # admin CRUD + reports
│   │       └── leaderboard.py# global rankings
│   ├── alembic/              # DB migrations
│   └── seed.py               # Demo data seeder
│
└── frontend/
    ├── app/
    │   ├── __init__.py       # Flask app factory
    │   ├── routes/
    │   │   ├── auth.py       # login / register / google / logout
    │   │   ├── main.py       # dashboard / tournaments / play / leaderboard
    │   │   └── admin.py      # admin interface routes
    │   ├── templates/
    │   │   ├── base.html     # nav, flash messages, Bootstrap 5
    │   │   ├── auth/         # login.html, register.html
    │   │   ├── main/         # dashboard, tournaments, play, leaderboard
    │   │   └── admin/        # dashboard, tournaments, reports, edit, add_challenge
    │   └── static/
    │       ├── css/main.css  # dark theme, difficulty badges, animations
    │       └── js/main.js    # alert auto-dismiss, nav highlighting
    └── run.py
```

## Features

### Players
- Sign up with email/password or Google SSO
- Browse and join active tournaments
- Play timed challenges (quiz, phishing detection, scenario, password)
- Real-time per-challenge countdown + global tournament timer
- Instant feedback with explanations after each answer
- Global + per-tournament leaderboards

### Admin
- Create tournaments with name, difficulty, per-challenge timer, total timer, start/end dates
- Add challenges of four types: Quiz, Phishing Detection, Scenario, Password
- Activate/deactivate tournaments
- View per-tournament performance reports (accuracy, avg time, completion rate)
- View full user performance summary (score, accuracy, best rank)

## Google OAuth Setup
1. Go to https://console.cloud.google.com → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Add `http://localhost:8000/api/v1/auth/google/callback` as Authorized redirect URI
4. Copy Client ID and Secret into `.env`
