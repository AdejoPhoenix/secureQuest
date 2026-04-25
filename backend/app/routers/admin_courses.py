from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course, CourseModule, CourseEnrollment, ModuleProgress
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut, ModuleCreate, ModuleOut
from app.auth.jwt import require_admin

router = APIRouter(prefix="/admin/courses", tags=["admin-courses"])


def _course_or_404(course_id: int, db: Session) -> Course:
    c = db.query(Course).filter(Course.id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c


# ── Courses CRUD ──────────────────────────────────────────────────────────────

@router.get("/", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return _enrich(courses, db)


@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = Course(**payload.model_dump(), created_by=admin.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    out = CourseOut.model_validate(course)
    out.module_count = 0
    out.enrolled = 0
    return out


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return _enrich([_course_or_404(course_id, db)], db)[0]


@router.patch("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = _course_or_404(course_id, db)
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return _enrich([course], db)[0]


@router.post("/{course_id}/publish", response_model=CourseOut)
def publish_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = _course_or_404(course_id, db)
    if not course.modules:
        raise HTTPException(status_code=400, detail="Add at least one module before publishing")
    course.is_published = True
    db.commit()
    db.refresh(course)
    return _enrich([course], db)[0]


@router.post("/{course_id}/unpublish", response_model=CourseOut)
def unpublish_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = _course_or_404(course_id, db)
    course.is_published = False
    db.commit()
    db.refresh(course)
    return _enrich([course], db)[0]


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = _course_or_404(course_id, db)
    db.delete(course)
    db.commit()


# ── Modules CRUD ──────────────────────────────────────────────────────────────

@router.post("/{course_id}/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
def add_module(course_id: int, payload: ModuleCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    _course_or_404(course_id, db)
    module = CourseModule(**payload.model_dump(), course_id=course_id)
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.patch("/{course_id}/modules/{module_id}", response_model=ModuleOut)
def update_module(course_id: int, module_id: int, payload: ModuleCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    module = db.query(CourseModule).filter_by(id=module_id, course_id=course_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    for k, v in payload.model_dump().items():
        setattr(module, k, v)
    db.commit()
    db.refresh(module)
    return module


@router.delete("/{course_id}/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(course_id: int, module_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    module = db.query(CourseModule).filter_by(id=module_id, course_id=course_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(module)
    db.commit()


# ── Analytics ─────────────────────────────────────────────────────────────────

@router.get("/{course_id}/analytics")
def course_analytics(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = _course_or_404(course_id, db)
    enrollments = db.query(CourseEnrollment).filter_by(course_id=course_id).all()
    total_enrolled = len(enrollments)
    completed = sum(1 for e in enrollments if e.is_completed)

    module_stats = []
    for m in course.modules:
        records = db.query(ModuleProgress).filter_by(module_id=m.id).all()
        passed  = sum(1 for r in records if r.is_completed)
        avg_score = round(sum(r.score for r in records) / len(records), 1) if records else 0
        module_stats.append({
            "module_id": m.id,
            "title": m.title,
            "type": m.type,
            "attempts": len(records),
            "passed": passed,
            "pass_rate_pct": round(passed / len(records) * 100, 1) if records else 0,
            "avg_score": avg_score,
        })

    return {
        "course_id": course_id,
        "name": course.name,
        "is_published": course.is_published,
        "total_enrolled": total_enrolled,
        "completed": completed,
        "completion_rate_pct": round(completed / total_enrolled * 100, 1) if total_enrolled else 0,
        "module_stats": module_stats,
    }


def _enrich(courses, db):
    result = []
    for c in courses:
        out = CourseOut.model_validate(c)
        out.module_count = len(c.modules)
        out.enrolled = db.query(CourseEnrollment).filter_by(course_id=c.id).count()
        result.append(out)
    return result
