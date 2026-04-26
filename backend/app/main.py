import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, tournaments, admin, leaderboard
from app.routers import courses
from app.routers import admin_courses
import app.models  # ensure all models are registered

app = FastAPI(
    title="Security Awareness Game API",
    version="1.0.0",
    description="Gamified security awareness platform — backend API",
)

_frontend_url = os.getenv("FRONTEND_URL", "")
allow_origins = [
    "http://localhost:5000",
    "http://localhost:5001",
    "http://frontend:5000",
]
if _frontend_url:
    allow_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(tournaments.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(leaderboard.router, prefix=API_PREFIX)
app.include_router(courses.router, prefix=API_PREFIX)
app.include_router(admin_courses.router, prefix=API_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok"}
