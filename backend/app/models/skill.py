from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str | None] = mapped_column(String(120))
    normalized_name: Mapped[str] = mapped_column(String(120), index=True)


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    proficiency_level: Mapped[int] = mapped_column(default=1)
    source: Mapped[str] = mapped_column(String(80), default="manual")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_role: Mapped[str] = mapped_column(String(255))
    current_skills: Mapped[list[Any]] = mapped_column(JSON, default=list)
    required_skills: Mapped[list[Any]] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list[Any]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[Any]] = mapped_column(JSON, default=list)
    readiness_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
