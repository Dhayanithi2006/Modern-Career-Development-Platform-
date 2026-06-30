from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    location: Mapped[str | None] = mapped_column(String(255))
    education_level: Mapped[str | None] = mapped_column(String(100))
    college: Mapped[str | None] = mapped_column(String(255))
    graduation_year: Mapped[int | None]
    target_role: Mapped[str | None] = mapped_column(String(255))
    target_industry: Mapped[str | None] = mapped_column(String(255))
    experience_level: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
