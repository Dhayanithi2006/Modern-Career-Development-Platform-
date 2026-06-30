from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import ROADMAP_GENERATOR_PROMPT
from app.models.resume import Resume
from app.models.roadmap import Roadmap
from app.models.skill import SkillGapAnalysis, StudentSkill, Skill
from app.models.user import User
from app.services.resume_service import parse_resume_text
from app.utils.text import extract_json_object


def generate_roadmap(db: Session, user: User, target_role: str, duration_weeks: int = 4) -> Roadmap:
    # Get user's current skills
    student_skills = db.scalars(
        select(Skill).join(StudentSkill).where(StudentSkill.user_id == user.id)
    ).all()
    current_skills = ", ".join(s.name for s in student_skills) if student_skills else "Not extracted yet"

    # Get missing skills from latest skill gap analysis
    latest_gap = db.scalar(
        select(SkillGapAnalysis).where(SkillGapAnalysis.user_id == user.id).order_by(SkillGapAnalysis.created_at.desc())
    )
    missing = ", ".join(latest_gap.missing_skills) if latest_gap and latest_gap.missing_skills else "None identified"

    prompt = ROADMAP_GENERATOR_PROMPT.format(
        target_role=target_role,
        skills=current_skills,
        missing_skills=missing,
    )

    parsed = extract_json_object(gemini_client.generate_text(prompt))
    roadmap_json: dict[str, Any] = parsed if parsed and isinstance(parsed.get("weeks"), list) else {"weeks": _fallback_weeks(latest_gap.missing_skills if latest_gap else [], duration_weeks)}

    roadmap = Roadmap(
        user_id=user.id,
        title=f"{target_role} Roadmap",
        target_role=target_role,
        duration_weeks=duration_weeks,
        roadmap_json=roadmap_json,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap


def _fallback_weeks(missing: list[str], duration_weeks: int) -> list[dict[str, Any]]:
    skills = missing or ["core concepts", "projects", "interview practice", "deployment"]
    weeks = []
    for index in range(duration_weeks):
        skill = skills[index % len(skills)]
        weeks.append(
            {
                "week": index + 1,
                "learning_goals": [f"Learn {skill}", "Document progress"],
                "projects": [f"Build a portfolio task using {skill}"],
                "courses": [],
                "practice_websites": [],
                "interview_preparation": [],
                "certifications": [],
            }
        )
    return weeks
