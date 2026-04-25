import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CourseCategory(str, enum.Enum):
    phishing            = "phishing"
    passwords           = "passwords"
    social_engineering  = "social_engineering"
    malware             = "malware"
    network_security    = "network_security"
    general             = "general"


class ModuleType(str, enum.Enum):
    lesson   = "lesson"    # rich formatted text + callouts
    quiz     = "quiz"      # inline multi-question quiz
    scenario = "scenario"  # branching decision with outcomes
    dragdrop = "dragdrop"  # drag items into categories


class Course(Base):
    __tablename__ = "courses"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    name:             Mapped[str]           = mapped_column(String(255), nullable=False)
    description:      Mapped[str | None]    = mapped_column(Text, nullable=True)
    category:         Mapped[CourseCategory]= mapped_column(Enum(CourseCategory), default=CourseCategory.general)
    difficulty:       Mapped[str]           = mapped_column(String(20), default="easy")
    thumbnail_color:  Mapped[str]           = mapped_column(String(20), default="#ffc107")
    is_published:     Mapped[bool]          = mapped_column(Boolean, default=False)
    xp_reward:        Mapped[int]           = mapped_column(Integer, default=100)
    created_by:       Mapped[int]           = mapped_column(Integer, ForeignKey("users.id"))
    created_at:       Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:       Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    modules     = relationship("CourseModule",    back_populates="course", order_by="CourseModule.order", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")


class CourseModule(Base):
    __tablename__ = "course_modules"

    id:          Mapped[int]        = mapped_column(Integer, primary_key=True, index=True)
    course_id:   Mapped[int]        = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    title:       Mapped[str]        = mapped_column(String(255), nullable=False)
    type:        Mapped[ModuleType] = mapped_column(Enum(ModuleType), default=ModuleType.lesson)
    content:     Mapped[dict]       = mapped_column(JSON, nullable=False, default=dict)
    order:       Mapped[int]        = mapped_column(Integer, default=0)
    xp_reward:   Mapped[int]        = mapped_column(Integer, default=20)
    is_required: Mapped[bool]       = mapped_column(Boolean, default=True)
    pass_score:  Mapped[int]        = mapped_column(Integer, default=70)  # % needed to pass quiz/dragdrop

    course    = relationship("Course",        back_populates="modules")
    progress  = relationship("ModuleProgress", back_populates="module", cascade="all, delete-orphan")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    user_id:      Mapped[int]           = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    course_id:    Mapped[int]           = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    is_completed: Mapped[bool]          = mapped_column(Boolean, default=False)
    xp_earned:    Mapped[int]           = mapped_column(Integer, default=0)
    enrolled_at:  Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime|None] = mapped_column(DateTime, nullable=True)

    course = relationship("Course", back_populates="enrollments")


class ModuleProgress(Base):
    __tablename__ = "module_progress"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    user_id:      Mapped[int]           = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    module_id:    Mapped[int]           = mapped_column(Integer, ForeignKey("course_modules.id"), nullable=False)
    course_id:    Mapped[int]           = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    is_completed: Mapped[bool]          = mapped_column(Boolean, default=False)
    score:        Mapped[int]           = mapped_column(Integer, default=0)  # 0-100
    attempts:     Mapped[int]           = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime|None] = mapped_column(DateTime, nullable=True)

    module = relationship("CourseModule", back_populates="progress")
