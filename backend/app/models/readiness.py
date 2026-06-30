from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReadinessSnapshot(Base):
    __tablename__ = "readiness_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    resume_score: Mapped[float] = mapped_column(Float, default=0)
    skill_score: Mapped[float] = mapped_column(Float, default=0)
    job_match_score: Mapped[float] = mapped_column(Float, default=0)
    interview_score: Mapped[float] = mapped_column(Float, default=0)
    overall_readiness_score: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
