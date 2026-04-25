from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.tournament import Tournament, Challenge, UserTournament, UserResponse
from app.schemas.tournament import (
    TournamentOut, ChallengePublic, SubmitAnswer,
    UserTournamentOut, LeaderboardEntry,
)
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


def _tournament_or_404(tournament_id: int, db: Session) -> Tournament:
    t = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return t


@router.get("/", response_model=list[TournamentOut])
def list_tournaments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tournaments = db.query(Tournament).order_by(Tournament.created_at.desc()).all()
    result = []
    for t in tournaments:
        out = TournamentOut.model_validate(t)
        out.participant_count = db.query(UserTournament).filter(UserTournament.tournament_id == t.id).count()
        result.append(out)
    return result


@router.get("/{tournament_id}", response_model=TournamentOut)
def get_tournament(tournament_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = _tournament_or_404(tournament_id, db)
    out = TournamentOut.model_validate(t)
    out.participant_count = db.query(UserTournament).filter(UserTournament.tournament_id == t.id).count()
    return out


@router.get("/{tournament_id}/challenges", response_model=list[ChallengePublic])
def get_challenges(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _tournament_or_404(tournament_id, db)
    participation = db.query(UserTournament).filter(
        UserTournament.user_id == current_user.id,
        UserTournament.tournament_id == tournament_id,
    ).first()
    if not participation:
        raise HTTPException(status_code=403, detail="Join the tournament first")
    challenges = db.query(Challenge).filter(Challenge.tournament_id == tournament_id).order_by(Challenge.order).all()
    return challenges


@router.post("/{tournament_id}/join", response_model=UserTournamentOut, status_code=status.HTTP_201_CREATED)
def join_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = _tournament_or_404(tournament_id, db)
    if not t.is_active:
        raise HTTPException(status_code=400, detail="Tournament is not active")

    existing = db.query(UserTournament).filter(
        UserTournament.user_id == current_user.id,
        UserTournament.tournament_id == tournament_id,
    ).first()
    if existing:
        return existing

    count = db.query(UserTournament).filter(UserTournament.tournament_id == tournament_id).count()
    if count >= t.max_participants:
        raise HTTPException(status_code=400, detail="Tournament is full")

    participation = UserTournament(user_id=current_user.id, tournament_id=tournament_id)
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return participation


@router.post("/{tournament_id}/submit", response_model=dict)
def submit_answer(
    tournament_id: int,
    payload: SubmitAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    participation = db.query(UserTournament).filter(
        UserTournament.user_id == current_user.id,
        UserTournament.tournament_id == tournament_id,
    ).first()
    if not participation:
        raise HTTPException(status_code=403, detail="Not a participant")
    if participation.is_completed:
        raise HTTPException(status_code=400, detail="Tournament already completed")

    challenge = db.query(Challenge).filter(
        Challenge.id == payload.challenge_id,
        Challenge.tournament_id == tournament_id,
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    already = db.query(UserResponse).filter(
        UserResponse.user_id == current_user.id,
        UserResponse.challenge_id == payload.challenge_id,
    ).first()
    if already:
        raise HTTPException(status_code=400, detail="Already answered this challenge")

    is_correct = payload.response.strip().lower() == challenge.correct_answer.strip().lower()
    points = challenge.points if is_correct else 0

    response = UserResponse(
        user_id=current_user.id,
        challenge_id=challenge.id,
        tournament_id=tournament_id,
        response=payload.response,
        is_correct=is_correct,
        points_earned=points,
        time_taken_seconds=payload.time_taken_seconds,
    )
    db.add(response)

    participation.score += points
    participation.challenges_completed += 1
    participation.time_taken_seconds += payload.time_taken_seconds

    total_challenges = db.query(Challenge).filter(Challenge.tournament_id == tournament_id).count()
    if participation.challenges_completed >= total_challenges:
        participation.is_completed = True
        participation.completed_at = datetime.utcnow()
        current_user.tournaments_completed += 1

    current_user.total_score += points
    db.commit()

    return {
        "is_correct": is_correct,
        "points_earned": points,
        "explanation": challenge.explanation,
        "correct_answer": challenge.correct_answer if not is_correct else None,
    }


@router.get("/{tournament_id}/leaderboard", response_model=list[LeaderboardEntry])
def tournament_leaderboard(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _tournament_or_404(tournament_id, db)
    participations = (
        db.query(UserTournament)
        .filter(UserTournament.tournament_id == tournament_id)
        .order_by(UserTournament.score.desc(), UserTournament.time_taken_seconds.asc())
        .all()
    )
    entries = []
    for rank, p in enumerate(participations, start=1):
        entries.append(LeaderboardEntry(
            rank=rank,
            user_id=p.user_id,
            username=p.user.username,
            avatar_url=p.user.avatar_url,
            score=p.score,
            challenges_completed=p.challenges_completed,
            time_taken_seconds=p.time_taken_seconds,
            is_completed=p.is_completed,
        ))
    return entries
