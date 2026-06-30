from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pdfplumber
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client
from app.core.config import settings
from app.models.resume import Resume
from app.models.skill import Skill, StudentSkill
from app.models.user import User
from app.services.embedding_service import embedding_service
from app.utils.text import extract_json_object, normalize_skill, simple_token_set
from app.vectorstore.collections import RESUME_CHUNKS, STUDENT_PROFILES

KNOWN_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "node.js",
    "fastapi",
    "django",
    "sql",
    "postgresql",
    "mongodb",
    "docker",
    "kubernetes",
    "aws",
    "git",
    "machine learning",
    "deep learning",
    "nlp",
    "data analysis",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "tailwind",
    "html",
    "css",
}


def _extract_pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()


def _extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _extract_pdf_text(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_resume_text(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email_match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", text)
    phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    lowered = text.lower()
    skills = sorted(skill for skill in KNOWN_SKILLS if skill in lowered)

    sections: dict[str, list[str]] = {"education": [], "projects": [], "experience": [], "certifications": []}
    current: str | None = None
    section_aliases = {
        "education": "education",
        "academic": "education",
        "project": "projects",
        "projects": "projects",
        "experience": "experience",
        "work experience": "experience",
        "certifications": "certifications",
        "certification": "certifications",
    }
    for line in lines:
        key = section_aliases.get(line.lower().strip(":"))
        if key:
            current = key
            continue
        if current and len(sections[current]) < 12:
            sections[current].append(line)

    return {
        "name": lines[0] if lines else None,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "skills": skills,
        "education": sections["education"],
        "projects": sections["projects"],
        "experience": sections["experience"],
        "certifications": sections["certifications"],
    }


def _upsert_student_skills(db: Session, user_id: int, skills: list[str]) -> None:
    for skill_name in skills:
        normalized = normalize_skill(skill_name)
        skill = db.scalar(select(Skill).where(Skill.normalized_name == normalized))
        if skill is None:
            skill = Skill(name=skill_name.title(), normalized_name=normalized, category="resume")
            db.add(skill)
            db.flush()
        exists = db.scalar(select(StudentSkill).where(StudentSkill.user_id == user_id, StudentSkill.skill_id == skill.id))
        if exists is None:
            db.add(StudentSkill(user_id=user_id, skill_id=skill.id, proficiency_level=3, source="resume", confidence_score=0.8))


def upload_and_parse_resume(db: Session, user: User, file: UploadFile) -> Resume:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and TXT resumes are supported")
    data = file.file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Resume file is too large")

    upload_dir = Path(settings.upload_dir) / str(user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "resume").name
    target = upload_dir / safe_name
    target.write_bytes(data)

    raw_text = _extract_text(target)
    if not raw_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not extract text from resume")

    parsed = parse_resume_text(raw_text)
    resume = Resume(user_id=user.id, file_url=str(target), file_name=safe_name, raw_text=raw_text, parsed_summary=parsed)
    db.add(resume)
    db.flush()
    _upsert_student_skills(db, user.id, parsed.get("skills", []))
    db.commit()
    db.refresh(resume)

    embedding_service.add_embedding(
        RESUME_CHUNKS,
        f"resume:{resume.id}",
        raw_text[:8000],
        {"user_id": str(user.id), "resume_id": str(resume.id), "chunk_type": "full_resume"},
    )
    embedding_service.add_embedding(
        STUDENT_PROFILES,
        f"student:{user.id}",
        " ".join(parsed.get("skills", [])) + "\n" + raw_text[:2000],
        {"user_id": str(user.id)},
    )
    return resume


def analyze_resume(db: Session, resume: Resume, target_role: str | None = None) -> dict[str, Any]:
    parsed = resume.parsed_summary or parse_resume_text(resume.raw_text or "")
    prompt = f"""
Analyze this parsed resume for placement readiness as JSON only.
Target role: {target_role or "general software role"}
Resume:
{parsed}

Return keys: ats_score, resume_score, missing_skills, missing_keywords, strengths, improvements.
Scores must be numbers from 0 to 100.
"""
    ai_text = gemini_client.generate_text(prompt)
    ai_json = extract_json_object(ai_text)
    if ai_json is None:
        tokens = simple_token_set(resume.raw_text or "")
        has_email = bool(parsed.get("email"))
        has_projects = bool(parsed.get("projects"))
        has_skills = len(parsed.get("skills", [])) >= 4
        score = min(95, 45 + (15 if has_email else 0) + (20 if has_projects else 0) + (20 if has_skills else 0))
        ai_json = {
            "ats_score": float(score),
            "resume_score": float(max(40, score - 5)),
            "missing_skills": [],
            "missing_keywords": sorted({"impact", "metrics", "deployment", "testing"} - tokens),
            "strengths": ["Resume text was parsed successfully"],
            "improvements": ["Add measurable impact, role-specific keywords, and project outcomes"],
        }
    resume.ats_score = float(ai_json.get("ats_score", 0))
    resume.resume_score = float(ai_json.get("resume_score", 0))
    resume.parsed_summary = {**parsed, "analysis": ai_json}
    db.commit()
    db.refresh(resume)
    return ai_json
