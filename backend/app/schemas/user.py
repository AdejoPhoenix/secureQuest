from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, SSOProvider


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: str  # plain str so any stored email format is accepted at login
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    sso_provider: SSOProvider
    avatar_url: str | None
    is_active: bool
    total_score: int
    tournaments_completed: int
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserUpdate(BaseModel):
    username: str | None = None
    avatar_url: str | None = None
