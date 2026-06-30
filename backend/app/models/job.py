from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)
    employment_type: Mapped[str | None] = mapped_column(String(100))
    experience_level: Mapped[str | None] = mapped_column(String(100))
    apply_url: Mapped[str | None] = mapped_column(String(700))
    source: Mapped[str] = mapped_column(String(100))
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    required_level: Mapped[int] = mapped_column(default=1)
    importance_score: Mapped[float] = mapped_column(Float, default=1.0)
