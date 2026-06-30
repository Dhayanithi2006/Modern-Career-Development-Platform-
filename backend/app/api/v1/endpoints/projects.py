from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import PROJECT_RECOMMENDATION_PROMPT
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resume import Resume
from app.models.skill import SkillGapAnalysis, StudentSkill, Skill
from app.models.user import User
from app.services.resume_service import parse_resume_text
from app.utils.text import extract_json_object

router = APIRouter()


class ProjectRequest(BaseModel):
    target_role: str = "Software Engineer"


@router.post("/recommend")
def recommend_projects(
    payload: ProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    # Get user's current skills
    student_skills = db.scalars(
        select(Skill).join(StudentSkill).where(StudentSkill.user_id == current_user.id)
    ).all()
    current_skills = ", ".join(s.name for s in student_skills) if student_skills else "Not extracted"

    # Get missing skills
    latest_gap = db.scalar(
        select(SkillGapAnalysis)
        .where(SkillGapAnalysis.user_id == current_user.id)
        .order_by(SkillGapAnalysis.created_at.desc())
    )
    missing = ", ".join(latest_gap.missing_skills) if latest_gap and latest_gap.missing_skills else "None identified"

    prompt = PROJECT_RECOMMENDATION_PROMPT.format(
        role=payload.target_role,
        skills=current_skills,
        missing_skills=missing,
    )

    data = extract_json_object(gemini_client.generate_text(prompt)) or {}
    projects = data.get("projects", [])

    return {"target_role": payload.target_role, "projects": projects}
