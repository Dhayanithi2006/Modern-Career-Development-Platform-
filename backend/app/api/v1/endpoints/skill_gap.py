from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.skill import SkillGapAnalysis
from app.models.user import User
from app.services.skill_gap_service import analyze_skill_gap as analyze_skill_gap_service

router = APIRouter()


class SkillGapRequest(BaseModel):
    target_role: str
    job_id: int | None = None


@router.post("/analyze")
def analyze_skill_gap(payload: SkillGapRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    analysis = analyze_skill_gap_service(db, current_user, payload.target_role, payload.job_id)
    return {
        "id": analysis.id,
        "user_id": current_user.id,
        "target_role": analysis.target_role,
        "current_skills": analysis.current_skills,
        "required_skills": analysis.required_skills,
        "missing_skills": analysis.missing_skills,
        "recommendations": analysis.recommendations,
        "readiness_score": analysis.readiness_score,
    }


@router.get("/latest")
def latest_skill_gap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object] | None:
    analysis = db.scalar(
        select(SkillGapAnalysis).where(SkillGapAnalysis.user_id == current_user.id).order_by(SkillGapAnalysis.created_at.desc())
    )
    if analysis is None:
        return None
    return {
        "id": analysis.id,
        "target_role": analysis.target_role,
        "missing_skills": analysis.missing_skills,
        "recommendations": analysis.recommendations,
        "readiness_score": analysis.readiness_score,
    }


@router.get("/history")
def skill_gap_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, object]]:
    rows = db.scalars(
        select(SkillGapAnalysis).where(SkillGapAnalysis.user_id == current_user.id).order_by(SkillGapAnalysis.created_at.desc())
    ).all()
    return [
        {
            "id": analysis.id,
            "target_role": analysis.target_role,
            "missing_skills": analysis.missing_skills,
            "readiness_score": analysis.readiness_score,
            "created_at": analysis.created_at,
        }
        for analysis in rows
    ]
