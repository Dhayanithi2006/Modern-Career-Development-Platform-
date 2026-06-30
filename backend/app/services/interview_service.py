from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import INTERVIEW_GENERATOR_PROMPT, INTERVIEW_EVALUATE_PROMPT
from app.models.interview import MockInterview, MockInterviewQuestion
from app.models.resume import Resume
from app.models.user import User
from app.services.resume_service import parse_resume_text
from app.utils.text import extract_json_object


def start_interview(db: Session, user: User, target_role: str, difficulty: str, interview_type: str) -> MockInterview:
    interview = MockInterview(user_id=user.id, target_role=target_role, difficulty=difficulty, interview_type=interview_type)
    db.add(interview)
    db.flush()

    # Gather user skills from latest resume
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc()))
    parsed = (resume.parsed_summary or parse_resume_text(resume.raw_text or "")) if resume else {}
    skills_list = ", ".join(str(s) for s in parsed.get("skills", [])) or "General"

    for question in _generate_questions(target_role, difficulty, interview_type, skills_list):
        db.add(MockInterviewQuestion(interview_id=interview.id, question=question))
    db.commit()
    db.refresh(interview)
    return interview


def _generate_questions(target_role: str, difficulty: str, interview_type: str, skills: str) -> list[str]:
    prompt = INTERVIEW_GENERATOR_PROMPT.format(
        role=target_role,
        difficulty=difficulty,
        skills=skills,
    )
    parsed = extract_json_object(gemini_client.generate_text(prompt))
    if parsed and isinstance(parsed.get("questions"), list):
        return [
            q.get("question", str(q)) if isinstance(q, dict) else str(q)
            for q in parsed["questions"][:22]
        ]
    return [
        f"Tell me about your background for a {target_role} role.",
        f"What core skills are important for {target_role}?",
        "Describe a project where you solved a difficult technical problem.",
        "How do you test and debug your work?",
        "Tell me about a time you handled feedback.",
        "Why should this company hire you?",
    ]


def evaluate_answer(db: Session, question_id: int, answer: str) -> MockInterviewQuestion:
    question = db.get(MockInterviewQuestion, question_id)
    if question is None:
        raise ValueError("Question not found")

    interview = db.get(MockInterview, question.interview_id)
    role = interview.target_role if interview else "Software Engineer"

    prompt = INTERVIEW_EVALUATE_PROMPT.format(
        role=role,
        question=question.question,
        answer=answer,
    )
    parsed = extract_json_object(gemini_client.generate_text(prompt)) or {}
    scores = [
        float(parsed.get(key, 70))
        for key in ("technical_score", "communication_score", "confidence_score", "grammar_score")
    ]
    question.answer = answer
    question.score = round(sum(scores) / len(scores), 2)
    question.feedback = parsed.get("feedback", "Good start. Add more specifics, metrics, and tradeoffs.")
    db.commit()
    db.refresh(question)
    return question


def finish_interview(db: Session, interview_id: int, user: User) -> MockInterview:
    interview = db.get(MockInterview, interview_id)
    if interview is None or interview.user_id != user.id:
        raise ValueError("Interview not found")
    questions = db.scalars(select(MockInterviewQuestion).where(MockInterviewQuestion.interview_id == interview_id)).all()
    scores = [question.score for question in questions if question.score is not None]
    interview.overall_score = round(sum(scores) / len(scores), 2) if scores else 0
    interview.feedback_summary = "Review low-scoring answers and practice concise STAR-format responses."
    db.commit()
    db.refresh(interview)
    return interview
