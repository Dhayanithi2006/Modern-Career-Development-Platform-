from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.job import Job
from app.services.embedding_service import embedding_service
from app.vectorstore.collections import JOB_DESCRIPTIONS


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _normalize_jsearch_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_id": item.get("job_id"),
        "title": item.get("job_title") or "Untitled Role",
        "company": item.get("employer_name") or "Unknown Company",
        "location": item.get("job_city") or item.get("job_country") or item.get("job_location"),
        "description": item.get("job_description") or "",
        "requirements": "\n".join(item.get("job_required_skills") or []),
        "employment_type": item.get("job_employment_type"),
        "experience_level": str(item.get("job_required_experience", {}).get("required_experience_in_months") or "") if isinstance(item.get("job_required_experience"), dict) else None,
        "apply_url": item.get("job_apply_link"),
        "source": "jsearch",
        "posted_at": _parse_date(item.get("job_posted_at_datetime_utc")),
    }


def search_jobs(db: Session, role: str | None, location: str | None, experience: str | None, page: int, page_size: int) -> list[Job]:
    if settings.jsearch_api_key and role:
        _sync_from_jsearch(db, role, location, page, page_size)

    statement = select(Job)
    if role:
        statement = statement.where(Job.title.ilike(f"%{role}%"))
    if location:
        statement = statement.where(Job.location.ilike(f"%{location}%"))
    if experience:
        statement = statement.where(Job.experience_level.ilike(f"%{experience}%"))
    jobs = db.scalars(statement.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    
    if not jobs and not settings.jsearch_api_key and page == 1:
        # Seed dummy jobs for the hackathon demo if no real jobs exist
        upsert_job(db, {"title": "Frontend Developer", "company": "Tech Innovators Inc", "location": "Remote", "description": "Looking for a skilled React developer to build modern UIs.", "requirements": "React, TypeScript, TailwindCSS", "source": "dummy"})
        upsert_job(db, {"title": "AI Engineer", "company": "Future Corp", "location": "New York, NY", "description": "Build agentic AI workflows and LLM pipelines.", "requirements": "Python, LangGraph, Gemini API", "source": "dummy"})
        upsert_job(db, {"title": "Backend Developer", "company": "Cloud Systems", "location": "San Francisco, CA", "description": "Develop scalable APIs using FastAPI.", "requirements": "Python, FastAPI, PostgreSQL", "source": "dummy"})
        db.commit()
        jobs = db.scalars(statement.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
        
    return jobs

def _sync_from_jsearch(db: Session, role: str, location: str | None, page: int, page_size: int) -> None:
    headers = {"X-RapidAPI-Key": settings.jsearch_api_key, "X-RapidAPI-Host": settings.jsearch_api_host}
    query = f"{role} in {location}" if location else role
    with httpx.Client(timeout=20) as client:
        response = client.get(
            f"https://{settings.jsearch_api_host}/search",
            headers=headers,
            params={"query": query, "page": page, "num_pages": 1, "date_posted": "month"},
        )
        response.raise_for_status()
    for item in response.json().get("data", [])[:page_size]:
        upsert_job(db, _normalize_jsearch_item(item))
    db.commit()


def upsert_job(db: Session, data: dict[str, Any]) -> Job:
    job = None
    if data.get("external_id"):
        job = db.scalar(select(Job).where(Job.external_id == data["external_id"], Job.source == data.get("source", "jsearch")))
    if job is None:
        job = Job(**data)
        db.add(job)
        db.flush()
    else:
        for key, value in data.items():
            setattr(job, key, value)
    embedding_service.add_embedding(
        JOB_DESCRIPTIONS,
        f"job:{job.id}",
        f"{job.title}\n{job.company}\n{job.description}\n{job.requirements or ''}",
        {"job_id": str(job.id), "title": job.title, "company": job.company, "source": job.source},
    )
    return job
