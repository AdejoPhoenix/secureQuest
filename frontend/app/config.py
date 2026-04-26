import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    SESSION_PERMANENT = False
