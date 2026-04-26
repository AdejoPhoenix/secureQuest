from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole, SSOProvider
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.auth.jwt import hash_password, verify_password, create_access_token, get_current_user
from app.auth.oauth import get_google_auth_url, exchange_google_code

router = APIRouter(prefix="/auth", tags=["auth"])


def _limiter():
    from app.main import limiter
    return limiter


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@_limiter().limit("10/minute")
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        sso_provider=SSOProvider.local,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
@_limiter().limit("20/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login/form", response_model=Token)
@_limiter().limit("20/minute")
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """OAuth2 form-compatible endpoint for Swagger UI."""
    user = db.query(User).filter(User.email == username).first()
    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/google")
def google_login():
    import secrets
    state = secrets.token_urlsafe(16)
    return RedirectResponse(get_google_auth_url(state=state))


@router.get("/google/callback", response_model=Token)
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        google_user = await exchange_google_code(code)
    except Exception:
        raise HTTPException(status_code=400, detail="Google OAuth failed")

    google_id = google_user["id"]
    email = google_user["email"]

    user = db.query(User).filter(User.sso_id == google_id, User.sso_provider == SSOProvider.google).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.sso_id = google_id
            user.sso_provider = SSOProvider.google
        else:
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            user = User(
                email=email,
                username=username,
                sso_provider=SSOProvider.google,
                sso_id=google_id,
                avatar_url=google_user.get("picture"),
            )
            db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
