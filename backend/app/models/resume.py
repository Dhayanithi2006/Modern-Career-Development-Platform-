from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    file_url: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str | None] = mapped_column(Text)
    parsed_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    ats_score: Mapped[float | None] = mapped_column(Float)
    resume_score: Mapped[float | None] = mapped_column(Float)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
