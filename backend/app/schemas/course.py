from datetime import datetime
from pydantic import BaseModel
from app.models.course import CourseCategory, ModuleType


# ── Module schemas ────────────────────────────────────────────────────────────

class ModuleCreate(BaseModel):
    title:       str
    type:        ModuleType  = ModuleType.lesson
    content:     dict        = {}
    order:       int         = 0
    xp_reward:   int         = 20
    is_required: bool        = True
    pass_score:  int         = 70


class ModuleOut(ModuleCreate):
    id:        int
    course_id: int
    model_config = {"from_attributes": True}


class ModuleProgressOut(BaseModel):
    module_id:    int
    is_completed: bool
    score:        int
    attempts:     int
    completed_at: datetime | None
    model_config = {"from_attributes": True}


# ── Course schemas ────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    name:            str
    description:     str | None      = None
    category:        CourseCategory  = CourseCategory.general
    difficulty:      str             = "easy"
    thumbnail_color: str             = "#ffc107"
    xp_reward:       int             = 100
    is_published:    bool            = False


class CourseUpdate(BaseModel):
    name:            str | None            = None
    description:     str | None            = None
    category:        CourseCategory | None = None
    difficulty:      str | None            = None
    thumbnail_color: str | None            = None
    xp_reward:       int | None            = None
    is_published:    bool | None           = None


class CourseOut(CourseCreate):
    id:           int
    created_by:   int
    created_at:   datetime
    modules:      list[ModuleOut] = []
    module_count: int             = 0
    enrolled:     int             = 0
    model_config = {"from_attributes": True}


class EnrollmentOut(BaseModel):
    id:           int
    user_id:      int
    course_id:    int
    is_completed: bool
    xp_earned:    int
    enrolled_at:  datetime
    completed_at: datetime | None
    model_config = {"from_attributes": True}


class CompleteModuleRequest(BaseModel):
    score: int = 100   # 0-100; for lessons always 100


class CourseProgressSummary(BaseModel):
    course_id:            int
    course_name:          str
    total_modules:        int
    completed_modules:    int
    progress_pct:         float
    is_completed:         bool
    xp_earned:            int
    module_progress:      list[ModuleProgressOut]
