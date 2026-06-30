from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    semantic_score: Mapped[float] = mapped_column(Float)
    skill_match_score: Mapped[float] = mapped_column(Float)
    experience_match_score: Mapped[float] = mapped_column(Float)
    overall_score: Mapped[float] = mapped_column(Float)
    missing_skills: Mapped[list[Any]] = mapped_column(JSON, default=list)
    match_explanation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
