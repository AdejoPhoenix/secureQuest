from datetime import datetime
from pydantic import BaseModel
from app.models.tournament import Difficulty, ChallengeType


class ChallengeCreate(BaseModel):
    title: str
    description: str
    type: ChallengeType = ChallengeType.quiz
    points: int = 10
    difficulty_level: Difficulty = Difficulty.easy
    order: int = 0
    options: dict | None = None
    correct_answer: str
    explanation: str | None = None
    hints: list[str] | None = None


class ChallengeOut(ChallengeCreate):
    id: int
    tournament_id: int
    model_config = {"from_attributes": True}


class ChallengePublic(BaseModel):
    """Challenge without the correct answer — sent to players."""
    id: int
    tournament_id: int
    title: str
    description: str
    type: ChallengeType
    points: int
    difficulty_level: Difficulty
    order: int
    options: dict | None
    explanation: str | None
    hints: list[str] | None
    model_config = {"from_attributes": True}


class TournamentCreate(BaseModel):
    name: str
    description: str | None = None
    difficulty: Difficulty = Difficulty.easy
    timer_seconds: int = 300
    total_timer_seconds: int = 3600
    start_time: datetime | None = None
    end_time: datetime | None = None
    is_active: bool = False
    max_participants: int = 100


class TournamentOut(TournamentCreate):
    id: int
    created_by: int
    created_at: datetime
    challenges: list[ChallengeOut] = []
    participant_count: int = 0
    model_config = {"from_attributes": True}


class TournamentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    difficulty: Difficulty | None = None
    timer_seconds: int | None = None
    total_timer_seconds: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    is_active: bool | None = None
    max_participants: int | None = None


class SubmitAnswer(BaseModel):
    challenge_id: int
    response: str
    time_taken_seconds: int = 0


class UserTournamentOut(BaseModel):
    id: int
    user_id: int
    tournament_id: int
    score: int
    rank: int | None
    challenges_completed: int
    time_taken_seconds: int
    is_completed: bool
    started_at: datetime
    completed_at: datetime | None
    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    avatar_url: str | None
    score: int
    challenges_completed: int
    time_taken_seconds: int
    is_completed: bool


class UserPerformanceSummary(BaseModel):
    user_id: int
    username: str
    email: str
    total_score: int
    tournaments_completed: int
    tournaments_joined: int
    avg_score: float
    best_rank: int | None
    correct_answers: int
    total_answers: int
    accuracy_pct: float
