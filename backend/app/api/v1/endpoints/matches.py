from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.match import JobMatch
from app.models.user import User
from app.schemas.job import JobMatchRead, MatchGenerateRequest
from app.services.matching_service import generate_job_matches

router = APIRouter()


@router.post("/generate", response_model=list[JobMatchRead])
def generate_matches(payload: MatchGenerateRequest | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return generate_job_matches(db, current_user, limit=(payload.limit if payload else 10))


@router.get("", response_model=list[JobMatchRead])
def list_matches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(JobMatch).where(JobMatch.user_id == current_user.id).order_by(JobMatch.overall_score.desc())).all()
