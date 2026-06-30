from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, *, email: str, password_hash: str, full_name: str) -> User:
    user = User(email=email.lower(), password_hash=password_hash, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
