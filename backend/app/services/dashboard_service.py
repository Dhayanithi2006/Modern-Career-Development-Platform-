from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.interview import MockInterview
from app.models.match import JobMatch
from app.models.readiness import ReadinessSnapshot
from app.models.resume import Resume
from app.models.skill import SkillGapAnalysis
from app.models.user import User


def get_dashboard_summary(db: Session, user: User) -> dict[str, object]:
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc()))
    match_score = db.scalar(select(func.max(JobMatch.overall_score)).where(JobMatch.user_id == user.id)) or 0
    gap = db.scalar(select(SkillGapAnalysis).where(SkillGapAnalysis.user_id == user.id).order_by(SkillGapAnalysis.created_at.desc()))
    interview_score = db.scalar(select(func.max(MockInterview.overall_score)).where(MockInterview.user_id == user.id)) or 0
    resume_score = resume.resume_score if resume and resume.resume_score is not None else 0
    ats_score = resume.ats_score if resume and resume.ats_score is not None else 0
    skill_score = gap.readiness_score if gap else 0
    overall = round((ats_score * 0.2) + (resume_score * 0.2) + (match_score * 0.25) + (skill_score * 0.2) + (interview_score * 0.15), 2)
    actions = []
    if not resume:
        actions.append("Upload and analyze your resume")
    if skill_score < 70:
        actions.append("Run skill gap analysis for your target role")
    if match_score < 70:
        actions.append("Sync jobs and generate semantic matches")
    if interview_score < 70:
        actions.append("Complete a mock interview")
    # Compute dynamic learning time based on activity count
    activity_count = (1 if resume else 0) + (1 if gap else 0) + (1 if match_score > 0 else 0) + (1 if interview_score > 0 else 0)
    base_hours = activity_count * 2
    base_minutes = (activity_count * 15) % 60
    
    return {
        "user_id": user.id,
        "ats_score": ats_score,
        "resume_score": resume_score,
        "job_match_score": match_score,
        "skill_score": skill_score,
        "interview_score": interview_score,
        "overall_readiness_score": overall,
        "skill_gap_summary": gap.missing_skills if gap else [],
        "roadmap_progress": 0,
        "learning_hours": base_hours,
        "learning_minutes": base_minutes,
        "next_actions": actions or ["Keep applying and practicing interviews"],
    }


def create_snapshot(db: Session, user: User) -> ReadinessSnapshot:
    summary = get_dashboard_summary(db, user)
    snapshot = ReadinessSnapshot(
        user_id=user.id,
        resume_score=float(summary["resume_score"]),
        skill_score=float(summary["skill_score"]),
        job_match_score=float(summary["job_match_score"]),
        interview_score=float(summary["interview_score"]),
        overall_readiness_score=float(summary["overall_readiness_score"]),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
