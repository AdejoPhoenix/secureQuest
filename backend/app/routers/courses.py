from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course, CourseModule, CourseEnrollment, ModuleProgress
from app.schemas.course import CourseOut, EnrollmentOut, CompleteModuleRequest, CourseProgressSummary, ModuleProgressOut
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])


def _published_or_404(course_id: int, db: Session) -> Course:
    c = db.query(Course).filter(Course.id == course_id, Course.is_published == True).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c


@router.get("/", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    courses = db.query(Course).filter(Course.is_published == True).order_by(Course.created_at.desc()).all()
    return _enrich(courses, db)


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = _published_or_404(course_id, db)
    return _enrich([course], db)[0]


@router.post("/{course_id}/enroll", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _published_or_404(course_id, db)
    existing = db.query(CourseEnrollment).filter_by(user_id=current_user.id, course_id=course_id).first()
    if existing:
        return existing
    enrollment = CourseEnrollment(user_id=current_user.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/{course_id}/progress", response_model=CourseProgressSummary)
def get_progress(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = _published_or_404(course_id, db)
    enrollment = db.query(CourseEnrollment).filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled")

    total = len(course.modules)
    prog_records = db.query(ModuleProgress).filter_by(user_id=current_user.id, course_id=course_id).all()
    completed = sum(1 for p in prog_records if p.is_completed)
    pct = round(completed / total * 100, 1) if total else 0.0

    return CourseProgressSummary(
        course_id=course_id,
        course_name=course.name,
        total_modules=total,
        completed_modules=completed,
        progress_pct=pct,
        is_completed=enrollment.is_completed,
        xp_earned=enrollment.xp_earned,
        module_progress=[ModuleProgressOut.model_validate(p) for p in prog_records],
    )


@router.post("/{course_id}/modules/{module_id}/complete")
def complete_module(
    course_id: int,
    module_id: int,
    payload: CompleteModuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _published_or_404(course_id, db)
    module = db.query(CourseModule).filter_by(id=module_id, course_id=course_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    enrollment = db.query(CourseEnrollment).filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled")

    prog = db.query(ModuleProgress).filter_by(user_id=current_user.id, module_id=module_id).first()
    passed = payload.score >= module.pass_score

    if prog:
        prog.attempts += 1
        prog.score = max(prog.score, payload.score)
        if passed and not prog.is_completed:
            prog.is_completed = True
            prog.completed_at = datetime.utcnow()
    else:
        prog = ModuleProgress(
            user_id=current_user.id,
            module_id=module_id,
            course_id=course_id,
            is_completed=passed,
            score=payload.score,
            attempts=1,
            completed_at=datetime.utcnow() if passed else None,
        )
        db.add(prog)

    xp_gained = 0
    if passed:
        xp_gained = module.xp_reward

    # Check overall course completion
    db.flush()
    total = len(course.modules)
    required = [m for m in course.modules if m.is_required]
    completed_required = db.query(ModuleProgress).filter(
        ModuleProgress.user_id == current_user.id,
        ModuleProgress.course_id == course_id,
        ModuleProgress.is_completed == True,
        ModuleProgress.module_id.in_([m.id for m in required]),
    ).count()

    course_just_completed = False
    if completed_required >= len(required) and not enrollment.is_completed:
        enrollment.is_completed = True
        enrollment.completed_at = datetime.utcnow()
        enrollment.xp_earned += course.xp_reward
        current_user.total_score += course.xp_reward
        xp_gained += course.xp_reward
        course_just_completed = True
    else:
        enrollment.xp_earned += xp_gained
        current_user.total_score += xp_gained

    db.commit()

    return {
        "passed": passed,
        "score": payload.score,
        "xp_gained": xp_gained,
        "course_completed": course_just_completed,
        "course_xp_bonus": course.xp_reward if course_just_completed else 0,
    }


def _enrich(courses: list, db: Session) -> list:
    result = []
    for c in courses:
        out = CourseOut.model_validate(c)
        out.module_count = len(c.modules)
        out.enrolled = db.query(CourseEnrollment).filter_by(course_id=c.id).count()
        result.append(out)
    return result
