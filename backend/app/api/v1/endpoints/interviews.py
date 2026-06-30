from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.interview import MockInterview, MockInterviewQuestion
from app.models.user import User
from app.schemas.ai import InterviewAnswer, InterviewStart
from app.services.interview_service import evaluate_answer, finish_interview, start_interview as start_interview_service

router = APIRouter()


@router.post("/start")
def start_interview(payload: InterviewStart, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    interview = start_interview_service(db, current_user, payload.target_role, payload.difficulty, payload.interview_type)
    questions = db.scalars(select(MockInterviewQuestion).where(MockInterviewQuestion.interview_id == interview.id)).all()
    return {
        "id": interview.id,
        "user_id": current_user.id,
        "target_role": interview.target_role,
        "difficulty": interview.difficulty,
        "interview_type": interview.interview_type,
        "questions": [{"id": question.id, "question": question.question} for question in questions],
    }


@router.get("")
def list_interviews(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, object]]:
    interviews = db.scalars(select(MockInterview).where(MockInterview.user_id == current_user.id).order_by(MockInterview.created_at.desc())).all()
    return [
        {
            "id": item.id,
            "target_role": item.target_role,
            "difficulty": item.difficulty,
            "interview_type": item.interview_type,
            "overall_score": item.overall_score,
            "feedback_summary": item.feedback_summary,
            "created_at": item.created_at,
        }
        for item in interviews
    ]


@router.get("/{interview_id}")
def get_interview(interview_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    interview = db.get(MockInterview, interview_id)
    if interview is None or interview.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    questions = db.scalars(select(MockInterviewQuestion).where(MockInterviewQuestion.interview_id == interview_id)).all()
    return {
        "id": interview.id,
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "answer": question.answer,
                "feedback": question.feedback,
                "score": question.score,
            }
            for question in questions
        ],
    }


@router.post("/{interview_id}/answer")
def answer_interview_question(interview_id: int, payload: InterviewAnswer, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    interview = db.get(MockInterview, interview_id)
    if interview is None or interview.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    question = db.get(MockInterviewQuestion, payload.question_id)
    if question is None or question.interview_id != interview_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    question = evaluate_answer(db, payload.question_id, payload.answer)
    return {"question_id": question.id, "score": question.score, "feedback": question.feedback}


@router.post("/{interview_id}/finish")
def finish(interview_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        interview = finish_interview(db, interview_id, current_user)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    return {"id": interview.id, "overall_score": interview.overall_score, "feedback_summary": interview.feedback_summary}
