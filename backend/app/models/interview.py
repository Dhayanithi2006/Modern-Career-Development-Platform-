from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_role: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[str] = mapped_column(String(50))
    interview_type: Mapped[str] = mapped_column(String(80))
    overall_score: Mapped[float | None] = mapped_column(Float)
    feedback_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MockInterviewQuestion(Base):
    __tablename__ = "mock_interview_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("mock_interviews.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    feedback: Mapped[str | None] = mapped_column(Text)
    score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
