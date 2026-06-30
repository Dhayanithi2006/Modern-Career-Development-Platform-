from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import CAREER_ASSISTANT_PROMPT
from app.models.assistant import AssistantMessage, AssistantSession
from app.models.interview import MockInterview
from app.models.match import JobMatch
from app.models.resume import Resume
from app.models.roadmap import Roadmap
from app.models.user import User
from app.services.resume_service import parse_resume_text


def create_session(db: Session, user: User, title: str) -> AssistantSession:
    session = AssistantSession(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _gather_context(db: Session, user: User) -> dict[str, str]:
    """Gather all user context for a personalized assistant response."""
    # Resume
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc()))
    resume_text = (resume.raw_text or "")[:3000] if resume else "No resume uploaded yet."
    parsed = (resume.parsed_summary or parse_resume_text(resume.raw_text or "")) if resume else {}
    skills = ", ".join(str(s) for s in parsed.get("skills", [])) or "Not extracted yet"

    # Roadmap
    roadmap = db.scalar(select(Roadmap).where(Roadmap.user_id == user.id).order_by(Roadmap.created_at.desc()))
    roadmap_text = str(roadmap.roadmap_json)[:2000] if roadmap else "No roadmap generated yet."

    # Matched Jobs
    matches = db.scalars(select(JobMatch).where(JobMatch.user_id == user.id).order_by(JobMatch.overall_score.desc()).limit(5)).all()
    jobs_text = "\n".join(
        f"- Job #{m.job_id} | Score: {m.overall_score}% | Missing: {', '.join(m.missing_skills or [])}"
        for m in matches
    ) or "No job matches yet."

    # Interview History
    interviews = db.scalars(select(MockInterview).where(MockInterview.user_id == user.id).order_by(MockInterview.created_at.desc()).limit(3)).all()
    interviews_text = "\n".join(
        f"- {i.target_role} ({i.difficulty}) | Score: {i.overall_score}"
        for i in interviews
    ) or "No interviews yet."

    return {
        "resume": resume_text,
        "skills": skills,
        "roadmap": roadmap_text,
        "jobs": jobs_text,
        "interviews": interviews_text,
    }


def answer_message(db: Session, user: User, session_id: int, content: str) -> AssistantMessage:
    session = db.get(AssistantSession, session_id)
    if session is None or session.user_id != user.id:
        session = create_session(db, user, "Career Planning")

    # Save user message
    db.add(AssistantMessage(session_id=session.id, role="user", content=content, citations=[]))

    # Gather conversation history
    history_msgs = db.scalars(
        select(AssistantMessage)
        .where(AssistantMessage.session_id == session.id)
        .order_by(AssistantMessage.created_at.desc())
        .limit(10)
    ).all()
    history = "\n".join(f"{m.role}: {m.content[:200]}" for m in reversed(history_msgs))

    # Gather full student context
    context = _gather_context(db, user)

    prompt = CAREER_ASSISTANT_PROMPT.format(
        resume=context["resume"],
        skills=context["skills"],
        roadmap=context["roadmap"],
        jobs=context["jobs"],
        interviews=context["interviews"],
        history=history or "No previous conversations.",
        question=content,
    )

    reply = gemini_client.generate_text(prompt)
    message = AssistantMessage(session_id=session.id, role="assistant", content=reply, citations=[])
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_sessions(db: Session, user: User) -> list[AssistantSession]:
    return db.scalars(select(AssistantSession).where(AssistantSession.user_id == user.id).order_by(AssistantSession.updated_at.desc())).all()
