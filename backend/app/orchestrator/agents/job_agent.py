from app.orchestrator.state import CareerState
from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import JOB_MATCHING_PROMPT, EXPLAINABLE_AI_PROMPT
from app.utils.text import extract_json_object
import json


def match_jobs(state: CareerState) -> dict:
    """
    Job Agent: Compares the user's resume against seeded/fetched jobs.
    Uses the Job Matching prompt for detailed scoring and the
    Explainable AI prompt for user-friendly explanations.
    """
    resume_text = state.get("resume_text", "")
    extracted_skills = state.get("extracted_skills", [])
    if not resume_text and not extracted_skills:
        return {}

    # Build a skills summary string for matching
    skills_list = ", ".join([s.get("skill", "") for s in extracted_skills])

    # Use Job Matching prompt against a generic Software Engineer job description
    # In production this would iterate over real jobs from the DB
    generic_job = (
        "Software Engineer: Design, build and maintain scalable backend services. "
        "Required: Python, FastAPI, SQL, Docker, AWS, Git, CI/CD, REST APIs. "
        "Nice to have: React, TypeScript, Kubernetes, Redis, Machine Learning."
    )

    prompt = JOB_MATCHING_PROMPT.format(
        resume=resume_text[:4000],
        job_description=generic_job,
    )
    response = gemini_client.generate_text(prompt)
    data = extract_json_object(response) or {}

    matched_jobs = []
    if data.get("match_score") is not None:
        matched_jobs.append({
            "title": "Software Engineer",
            "company": "Matched via AI",
            "similarity_score": data.get("match_score", 0),
            "matching_skills": data.get("matching_skills", []),
            "missing_skills": data.get("missing_skills", []),
            "nice_to_have": data.get("nice_to_have_skills", []),
            "should_apply": data.get("should_apply", True),
            "reason": data.get("why_suitable", ""),
            "learning_plan": data.get("learning_plan", ""),
        })

    return {
        "matched_jobs": matched_jobs,
        "missing_skills": data.get("missing_skills", []),
    }
