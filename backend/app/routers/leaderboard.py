from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/global")
def global_leaderboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = (
        db.query(User)
        .filter(User.is_active == True)
        .order_by(User.total_score.desc(), User.tournaments_completed.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "rank": i + 1,
            "user_id": u.id,
            "username": u.username,
            "avatar_url": u.avatar_url,
            "total_score": u.total_score,
            "tournaments_completed": u.tournaments_completed,
        }
        for i, u in enumerate(users)
    ]
