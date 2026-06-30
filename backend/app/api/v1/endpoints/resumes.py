from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeAnalysis, ResumeAnalyzeRequest, ResumeRead
from app.services.resume_service import analyze_resume as analyze_resume_service
from app.services.resume_service import upload_and_parse_resume

router = APIRouter()


@router.post("/upload", response_model=ResumeRead)
def upload_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return upload_and_parse_resume(db, current_user, file)


@router.get("", response_model=list[ResumeRead])
def list_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc())).all()


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysis)
def analyze_resume(resume_id: int, target_role: str | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    from app.orchestrator.graph import career_orchestrator
    
    initial_state = {
        "user_id": current_user.id,
        "resume_text": resume.raw_text or "",
        "ats_score": 0.0,
        "ats_feedback": "",
        "extracted_skills": [],
        "matched_jobs": [],
        "missing_skills": [],
        "roadmap": [],
        "messages": []
    }
    
    # Run the orchestrator pipeline
    result_state = career_orchestrator.invoke(initial_state)
    
    return ResumeAnalysis(
        resume_id=resume_id,
        ats_score=float(result_state.get("ats_score", 0)),
        resume_score=float(result_state.get("ats_score", 0)),
        missing_skills=result_state.get("missing_skills", []),
        missing_keywords=[],
        strengths=["Skills extracted successfully"],
        improvements=[result_state.get("ats_feedback", "")],
        extracted_skills=result_state.get("extracted_skills", []),
        resume_analysis_data=result_state.get("resume_analysis", {})
    )


@router.post("/analyze", response_model=ResumeAnalysis)
def analyze_latest_resume(payload: ResumeAnalyzeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.get(Resume, payload.resume_id) if payload.resume_id else db.scalar(
        select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc())
    )
    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return analyze_resume(resume.id, payload.target_role, current_user, db)
