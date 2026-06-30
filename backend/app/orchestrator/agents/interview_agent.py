from app.orchestrator.state import CareerState
from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import INTERVIEW_GENERATOR_PROMPT
from app.utils.text import extract_json_object


def generate_interview(state: CareerState) -> dict:
    """
    Interview Agent: Generates interview questions tailored to the
    user's target role and extracted skills.
    """
    extracted_skills = state.get("extracted_skills", [])
    skills_list = ", ".join([s.get("skill", "") for s in extracted_skills]) if extracted_skills else "General"

    analysis = state.get("resume_analysis", {})
    suitable_roles = analysis.get("suitable_job_roles", [])
    target_role = suitable_roles[0] if suitable_roles else "Software Engineer"

    prompt = INTERVIEW_GENERATOR_PROMPT.format(
        role=target_role,
        difficulty="Medium",
        skills=skills_list,
    )

    response = gemini_client.generate_text(prompt)
    data = extract_json_object(response) or {}

    return {
        "interview_questions": data.get("questions", [])
    }
