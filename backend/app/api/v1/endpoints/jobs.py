from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobMatchRead, JobRead, MatchGenerateRequest
from app.services.job_service import search_jobs as search_jobs_service
from app.services.matching_service import generate_job_matches

router = APIRouter()


@router.get("/search", response_model=list[JobRead])
def search_jobs(
    q: str | None = None,
    role: str | None = None,
    location: str | None = None,
    experience: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return search_jobs_service(db, role or q, location, experience, max(1, page), min(max(1, page_size), 50))


@router.post("/sync")
def sync_jobs(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Use GET /jobs/search with JSEARCH_API_KEY configured to sync and store jobs."}


@router.post("/match", response_model=list[JobMatchRead])
def match_jobs(payload: MatchGenerateRequest | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = generate_job_matches(db, current_user, limit=(payload.limit if payload else 10))
    result = []
    for match in matches:
        job = db.scalar(select(Job).where(Job.id == match.job_id))
        match_dict = {
            "id": match.id,
            "job_id": match.job_id,
            "job_title": job.title if job else "Unknown Job",
            "company_name": job.company if job else "Unknown Company",
            "semantic_score": match.semantic_score,
            "skill_match_score": match.skill_match_score,
            "experience_match_score": match.experience_match_score,
            "overall_score": match.overall_score,
            "missing_skills": match.missing_skills,
            "match_explanation": match.match_explanation,
        }
        result.append(match_dict)
    return result
