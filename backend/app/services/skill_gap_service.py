from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.models.job import Job
from app.models.skill import Skill, SkillGapAnalysis, StudentSkill
from app.models.user import User
from app.utils.text import extract_json_object, simple_token_set


def analyze_skill_gap(db: Session, user: User, target_role: str, job_id: int | None = None) -> SkillGapAnalysis:
    current_rows = db.execute(
        select(Skill).join(StudentSkill, StudentSkill.skill_id == Skill.id).where(StudentSkill.user_id == user.id)
    ).scalars().all()
    current = sorted({skill.normalized_name for skill in current_rows})
    job_text = ""
    if job_id:
        job = db.get(Job, job_id)
        job_text = f"{job.title} {job.description} {job.requirements or ''}" if job else ""
    required = sorted(
        simple_token_set(f"{target_role} {job_text}")
        & {"python", "java", "javascript", "typescript", "react", "sql", "docker", "aws", "fastapi", "testing", "git"}
    )
    if not required:
        required = ["git", "sql", "project building", "communication"]
    missing = [skill for skill in required if skill not in current]
    recommendations = _ai_recommendations(target_role, current, missing)
    score = round(((len(required) - len(missing)) / max(1, len(required))) * 100, 2)
    analysis = SkillGapAnalysis(
        user_id=user.id,
        target_role=target_role,
        current_skills=current,
        required_skills=required,
        missing_skills=missing,
        recommendations=recommendations,
        readiness_score=score,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def _ai_recommendations(target_role: str, current: list[str], missing: list[str]) -> list[dict[str, Any]]:
    prompt = f"""
Return JSON with key recommendations as an array. Each item has skill, priority, learning_action.
Target role: {target_role}
Current skills: {current}
Missing skills: {missing}
"""
    parsed = extract_json_object(gemini_client.generate_text(prompt))
    if parsed and isinstance(parsed.get("recommendations"), list):
        return parsed["recommendations"]
    return [{"skill": skill, "priority": index + 1, "learning_action": f"Build a small project using {skill}"} for index, skill in enumerate(missing)]
