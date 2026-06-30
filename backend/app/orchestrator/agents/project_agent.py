from app.orchestrator.state import CareerState
from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import PROJECT_RECOMMENDATION_PROMPT
from app.utils.text import extract_json_object


def recommend_projects(state: CareerState) -> dict:
    """
    Project Agent: Recommends portfolio projects based on the user's
    current skills, missing skills, and target role.
    """
    missing_skills = state.get("missing_skills", [])
    extracted_skills = state.get("extracted_skills", [])

    skills_list = ", ".join([s.get("skill", "") for s in extracted_skills]) if extracted_skills else "Not extracted yet"
    missing_list = ", ".join(missing_skills) if missing_skills else "None identified"

    analysis = state.get("resume_analysis", {})
    suitable_roles = analysis.get("suitable_job_roles", [])
    target_role = suitable_roles[0] if suitable_roles else "Software Engineer"

    prompt = PROJECT_RECOMMENDATION_PROMPT.format(
        role=target_role,
        skills=skills_list,
        missing_skills=missing_list,
    )

    response = gemini_client.generate_text(prompt)
    data = extract_json_object(response) or {}

    return {
        "recommended_projects": data.get("projects", [])
    }
