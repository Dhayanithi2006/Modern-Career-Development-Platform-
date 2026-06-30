from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import JOB_MATCHING_PROMPT, EXPLAINABLE_AI_PROMPT
from app.models.job import Job
from app.models.match import JobMatch
from app.models.resume import Resume
from app.models.user import User
from app.services.resume_service import parse_resume_text
from app.utils.text import extract_json_object, simple_token_set
from app.vectorstore.collections import JOB_DESCRIPTIONS
from app.services.embedding_service import embedding_service


def generate_job_matches(db: Session, user: User, limit: int = 10) -> list[JobMatch]:
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc()))
    if resume is None:
        return []
    parsed = resume.parsed_summary or parse_resume_text(resume.raw_text or "")
    resume_text = resume.raw_text or ""

    # Try vector search first, fall back to DB scan
    query = f"{parsed.get('skills', [])}\n{resume_text}"[:4000]
    try:
        vector_results = embedding_service.search_embedding(JOB_DESCRIPTIONS, query, limit=limit)
        ids = [int(value.split(":")[1]) for value in vector_results.get("ids", [[]])[0] if ":" in value]
        jobs = db.scalars(select(Job).where(Job.id.in_(ids))).all() if ids else []
    except Exception:
        jobs = []

    if not jobs:
        jobs = db.scalars(select(Job).limit(limit)).all()

    matches: list[JobMatch] = []
    for job in jobs:
        match_data = score_job_match_with_ai(resume_text, parsed, job)
        existing = db.scalar(select(JobMatch).where(JobMatch.user_id == user.id, JobMatch.job_id == job.id))
        if existing is None:
            existing = JobMatch(user_id=user.id, job_id=job.id, **match_data)
            db.add(existing)
        else:
            for key, value in match_data.items():
                setattr(existing, key, value)
        matches.append(existing)
    db.commit()
    return matches


def score_job_match_with_ai(resume_text: str, parsed_resume: dict[str, Any], job: Job) -> dict[str, Any]:
    """Use the AI Job Matching prompt for detailed, explainable scoring."""
    job_desc = f"{job.title}\n{job.company}\n{job.description}\n{job.requirements or ''}"

    prompt = JOB_MATCHING_PROMPT.format(
        resume=resume_text[:4000],
        job_description=job_desc[:3000],
    )

    ai_result = extract_json_object(gemini_client.generate_text(prompt))

    if ai_result and ai_result.get("match_score") is not None:
        matching_skills = ai_result.get("matching_skills", [])
        missing_skills = ai_result.get("missing_skills", [])
        match_score = float(ai_result.get("match_score", 0))

        return {
            "semantic_score": match_score,
            "skill_match_score": match_score,
            "experience_match_score": 70.0,
            "overall_score": min(100, match_score),
            "missing_skills": missing_skills if isinstance(missing_skills, list) else [],
            "match_explanation": (
                f"Matching: {', '.join(matching_skills) if isinstance(matching_skills, list) else str(matching_skills)}. "
                f"Should apply: {ai_result.get('should_apply', 'Unknown')}. "
                f"{ai_result.get('why_suitable', '')}"
            ),
        }

    # Fallback to heuristic scoring
    return _fallback_score(parsed_resume, job)


def _fallback_score(parsed_resume: dict[str, Any], job: Job) -> dict[str, Any]:
    """Heuristic fallback when AI is unavailable."""
    resume_skills = {str(skill).lower() for skill in parsed_resume.get("skills", [])}
    job_tokens = simple_token_set(f"{job.title} {job.description} {job.requirements or ''}")
    matching = sorted(resume_skills & job_tokens)
    missing = sorted((job_tokens & {"python", "java", "javascript", "typescript", "react", "sql", "docker", "aws", "fastapi"}) - resume_skills)
    skill_score = (len(matching) / max(1, len(matching) + len(missing))) * 100
    semantic_score = min(100, 50 + skill_score / 2)
    overall = round((semantic_score * 0.55) + (skill_score * 0.35) + 10, 2)
    return {
        "semantic_score": round(semantic_score, 2),
        "skill_match_score": round(skill_score, 2),
        "experience_match_score": 70.0,
        "overall_score": min(100, overall),
        "missing_skills": missing,
        "match_explanation": f"Matched skills: {', '.join(matching) if matching else 'none detected yet'}.",
    }


def explain_match_with_ai(resume_text: str, job: Job, score: float) -> str:
    """Generate an Explainable AI explanation for a job match."""
    prompt = EXPLAINABLE_AI_PROMPT.format(
        resume=resume_text[:3000],
        job=f"{job.title} at {job.company}\n{job.description[:2000]}",
        score=score,
    )
    return gemini_client.generate_text(prompt)
