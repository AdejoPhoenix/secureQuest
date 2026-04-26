from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.tournament import Tournament, Challenge, UserTournament, UserResponse
from app.schemas.tournament import (
    TournamentCreate, TournamentOut, TournamentUpdate,
    ChallengeCreate, ChallengeOut, UserPerformanceSummary,
)
from app.schemas.user import UserOut
from app.auth.jwt import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Tournaments ───────────────────────────────────────────────────────────────

@router.post("/tournaments", response_model=TournamentOut, status_code=status.HTTP_201_CREATED)
def create_tournament(
    payload: TournamentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    t = Tournament(**payload.model_dump(), created_by=admin.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    out = TournamentOut.model_validate(t)
    out.participant_count = 0
    return out


@router.get("/tournaments", response_model=list[TournamentOut])
def list_all_tournaments(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    tournaments = db.query(Tournament).order_by(Tournament.created_at.desc()).all()
    result = []
    for t in tournaments:
        out = TournamentOut.model_validate(t)
        out.participant_count = db.query(UserTournament).filter(UserTournament.tournament_id == t.id).count()
        result.append(out)
    return result


@router.get("/tournaments/{tournament_id}", response_model=TournamentOut)
def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    t = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")
    out = TournamentOut.model_validate(t)
    out.participant_count = db.query(UserTournament).filter(UserTournament.tournament_id == t.id).count()
    return out


@router.patch("/tournaments/{tournament_id}", response_model=TournamentOut)
def update_tournament(
    tournament_id: int,
    payload: TournamentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    t = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(t, field, value)
    db.commit()
    db.refresh(t)
    out = TournamentOut.model_validate(t)
    out.participant_count = db.query(UserTournament).filter(UserTournament.tournament_id == t.id).count()
    return out


@router.delete("/tournaments/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    t = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")
    db.delete(t)
    db.commit()


# ── Challenges ────────────────────────────────────────────────────────────────

@router.post("/tournaments/{tournament_id}/challenges", response_model=ChallengeOut, status_code=status.HTTP_201_CREATED)
def add_challenge(
    tournament_id: int,
    payload: ChallengeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    t = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")
    challenge = Challenge(**payload.model_dump(), tournament_id=tournament_id)
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


@router.delete("/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    c = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    db.delete(c)
    db.commit()


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}/role")
def set_user_role(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    role: str = Body(..., embed=True),
):
    from app.models.user import UserRole
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        user.role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role '{role}'. Must be one of: {[r.value for r in UserRole]}")
    db.commit()
    return {"message": f"User {user.username} role updated to {role}"}


# ── Reports ───────────────────────────────────────────────────────────────────

@router.get("/reports/users", response_model=list[UserPerformanceSummary])
def user_performance_report(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).filter(User.role == "user").all()
    summaries = []
    for u in users:
        participations = db.query(UserTournament).filter(UserTournament.user_id == u.id).all()
        tournaments_joined = len(participations)
        completed = [p for p in participations if p.is_completed]
        scores = [p.score for p in participations]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        ranks = [p.rank for p in participations if p.rank is not None]
        best_rank = min(ranks) if ranks else None

        total_answers = db.query(UserResponse).filter(UserResponse.user_id == u.id).count()
        correct_answers = db.query(UserResponse).filter(
            UserResponse.user_id == u.id, UserResponse.is_correct == True
        ).count()
        accuracy = (correct_answers / total_answers * 100) if total_answers else 0.0

        summaries.append(UserPerformanceSummary(
            user_id=u.id,
            username=u.username,
            email=u.email,
            total_score=u.total_score,
            tournaments_completed=u.tournaments_completed,
            tournaments_joined=tournaments_joined,
            avg_score=round(avg_score, 2),
            best_rank=best_rank,
            correct_answers=correct_answers,
            total_answers=total_answers,
            accuracy_pct=round(accuracy, 2),
        ))
    return summaries


@router.get("/reports/tournaments/{tournament_id}")
def tournament_report(
    tournament_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    t = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")

    participations = db.query(UserTournament).filter(UserTournament.tournament_id == tournament_id).all()
    total_participants = len(participations)
    completed = sum(1 for p in participations if p.is_completed)
    avg_score = sum(p.score for p in participations) / total_participants if total_participants else 0

    challenge_stats = []
    for c in t.challenges:
        responses = db.query(UserResponse).filter(UserResponse.challenge_id == c.id).all()
        correct = sum(1 for r in responses if r.is_correct)
        challenge_stats.append({
            "challenge_id": c.id,
            "title": c.title,
            "total_attempts": len(responses),
            "correct_attempts": correct,
            "accuracy_pct": round(correct / len(responses) * 100, 2) if responses else 0,
            "avg_time_seconds": round(sum(r.time_taken_seconds for r in responses) / len(responses), 2) if responses else 0,
        })

    return {
        "tournament_id": t.id,
        "name": t.name,
        "difficulty": t.difficulty,
        "total_participants": total_participants,
        "completed_count": completed,
        "completion_rate_pct": round(completed / total_participants * 100, 2) if total_participants else 0,
        "avg_score": round(avg_score, 2),
        "challenge_stats": challenge_stats,
    }
