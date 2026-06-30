from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ResumeRead(BaseModel):
    id: int
    file_url: str
    file_name: str
    parsed_summary: dict[str, Any] | None
    ats_score: float | None
    resume_score: float | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class ResumeAnalysis(BaseModel):
    resume_id: int
    ats_score: float
    resume_score: float
    missing_skills: list[str] = []
    missing_keywords: list[str] = []
    strengths: list[str] = []
    improvements: list[str] = []
    extracted_skills: list[dict[str, Any]] = []
    resume_analysis_data: dict[str, Any] = {}


class ResumeAnalyzeRequest(BaseModel):
    resume_id: int | None = None
    target_role: str | None = None
