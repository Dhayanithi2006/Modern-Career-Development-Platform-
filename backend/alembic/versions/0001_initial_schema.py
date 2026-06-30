"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-23
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("phone", sa.String(30)),
        sa.Column("location", sa.String(255)),
        sa.Column("education_level", sa.String(100)),
        sa.Column("college", sa.String(255)),
        sa.Column("graduation_year", sa.Integer()),
        sa.Column("target_role", sa.String(255)),
        sa.Column("target_industry", sa.String(255)),
        sa.Column("experience_level", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("raw_text", sa.Text()),
        sa.Column("parsed_summary", sa.JSON()),
        sa.Column("ats_score", sa.Float()),
        sa.Column("resume_score", sa.Float()),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("category", sa.String(120)),
        sa.Column("normalized_name", sa.String(120), nullable=False, index=True),
    )
    op.create_table(
        "student_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("proficiency_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("source", sa.String(80), nullable=False, server_default="manual"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="1"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(255), index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requirements", sa.Text()),
        sa.Column("employment_type", sa.String(100)),
        sa.Column("experience_level", sa.String(100)),
        sa.Column("apply_url", sa.String(700)),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "job_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("required_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("importance_score", sa.Float(), nullable=False, server_default="1"),
    )
    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("semantic_score", sa.Float(), nullable=False),
        sa.Column("skill_match_score", sa.Float(), nullable=False),
        sa.Column("experience_match_score", sa.Float(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("match_explanation", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "skill_gap_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_role", sa.String(255), nullable=False),
        sa.Column("current_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("required_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("missing_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("recommendations", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("readiness_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "roadmaps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("target_role", sa.String(255), nullable=False),
        sa.Column("duration_weeks", sa.Integer(), nullable=False),
        sa.Column("roadmap_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "assistant_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "assistant_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("assistant_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "mock_interviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_role", sa.String(255), nullable=False),
        sa.Column("difficulty", sa.String(50), nullable=False),
        sa.Column("interview_type", sa.String(80), nullable=False),
        sa.Column("overall_score", sa.Float()),
        sa.Column("feedback_summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "mock_interview_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("interview_id", sa.Integer(), sa.ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text()),
        sa.Column("feedback", sa.Text()),
        sa.Column("score", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "readiness_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resume_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("skill_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("job_match_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("interview_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("overall_readiness_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    for table in (
        "readiness_snapshots",
        "mock_interview_questions",
        "mock_interviews",
        "assistant_messages",
        "assistant_sessions",
        "roadmaps",
        "skill_gap_analyses",
        "job_matches",
        "job_skills",
        "jobs",
        "student_skills",
        "skills",
        "resumes",
        "student_profiles",
        "users",
    ):
        op.drop_table(table)
