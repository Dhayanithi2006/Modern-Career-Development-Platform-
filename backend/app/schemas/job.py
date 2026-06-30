from datetime import datetime

from pydantic import BaseModel


class JobRead(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    description: str
    requirements: str | None
    employment_type: str | None
    experience_level: str | None
    apply_url: str | None
    source: str
    posted_at: datetime | None

    model_config = {"from_attributes": True}


class JobMatchRead(BaseModel):
    id: int
    job_id: int
    job_title: str | None = None
    company_name: str | None = None
    semantic_score: float
    skill_match_score: float
    experience_match_score: float
    overall_score: float
    missing_skills: list[str]
    match_explanation: str | None

    model_config = {"from_attributes": True}


class MatchGenerateRequest(BaseModel):
    limit: int = 10
