"""initial schema

Revision ID: 18c250de2c13
Revises:
Create Date: 2026-04-26

"""
from alembic import op
import sqlalchemy as sa

revision = "18c250de2c13"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("role", sa.Enum("admin", "user", name="userrole"), nullable=False, server_default="user"),
        sa.Column("sso_provider", sa.Enum("google", "local", name="ssoprovider"), nullable=False, server_default="local"),
        sa.Column("sso_id", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tournaments_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "tournaments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Enum("easy", "medium", "hard", "expert", name="difficulty"), nullable=False, server_default="easy"),
        sa.Column("timer_seconds", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("total_timer_seconds", sa.Integer(), nullable=False, server_default="3600"),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("max_participants", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("tournament_id", sa.Integer(), sa.ForeignKey("tournaments.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", sa.Enum("quiz", "phishing", "scenario", "password", name="challengetype"), nullable=False, server_default="quiz"),
        sa.Column("points", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("difficulty_level", sa.Enum("easy", "medium", "hard", "expert", name="difficulty"), nullable=False, server_default="easy"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("correct_answer", sa.String(255), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("hints", sa.JSON(), nullable=True),
    )

    op.create_table(
        "user_tournaments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tournament_id", sa.Integer(), sa.ForeignKey("tournaments.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("challenges_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("time_taken_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "user_responses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id"), nullable=False),
        sa.Column("tournament_id", sa.Integer(), sa.ForeignKey("tournaments.id"), nullable=False),
        sa.Column("response", sa.String(255), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("points_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("time_taken_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("answered_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.Enum("phishing", "passwords", "social_engineering", "malware", "network_security", "general", name="coursecategory"), nullable=False, server_default="general"),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="easy"),
        sa.Column("thumbnail_color", sa.String(20), nullable=False, server_default="#ffc107"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "course_modules",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("type", sa.Enum("lesson", "quiz", "scenario", "dragdrop", name="moduletype"), nullable=False, server_default="lesson"),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("pass_score", sa.Integer(), nullable=False, server_default="70"),
    )

    op.create_table(
        "course_enrollments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("xp_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enrolled_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "module_progress",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("course_modules.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("module_progress")
    op.drop_table("course_enrollments")
    op.drop_table("course_modules")
    op.drop_table("courses")
    op.drop_table("user_responses")
    op.drop_table("user_tournaments")
    op.drop_table("challenges")
    op.drop_table("tournaments")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS moduletype")
    op.execute("DROP TYPE IF EXISTS coursecategory")
    op.execute("DROP TYPE IF EXISTS challengetype")
    op.execute("DROP TYPE IF EXISTS difficulty")
    op.execute("DROP TYPE IF EXISTS ssoprovider")
    op.execute("DROP TYPE IF EXISTS userrole")
