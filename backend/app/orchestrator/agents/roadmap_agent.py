from app.orchestrator.state import CareerState
from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import ROADMAP_GENERATOR_PROMPT
from app.utils.text import extract_json_object


def generate_roadmap(state: CareerState) -> dict:
    """
    Roadmap Agent: Generates a personalized week-by-week learning roadmap
    based on the user's current skills, missing skills, and target role.
    """
    missing_skills = state.get("missing_skills", [])
    extracted_skills = state.get("extracted_skills", [])
    
    skills_list = ", ".join([s.get("skill", "") for s in extracted_skills]) if extracted_skills else "Not extracted yet"
    missing_list = ", ".join(missing_skills) if missing_skills else "None identified"
    
    # Determine target role from the resume analysis if available
    analysis = state.get("resume_analysis", {})
    suitable_roles = analysis.get("suitable_job_roles", [])
    target_role = suitable_roles[0] if suitable_roles else "Software Engineer"
    
    prompt = ROADMAP_GENERATOR_PROMPT.format(
        target_role=target_role,
        skills=skills_list,
        missing_skills=missing_list,
    )
    
    response = gemini_client.generate_text(prompt)
    data = extract_json_object(response) or {}
    
    roadmap = []
    weeks = data.get("weeks", [])
    for week_data in weeks:
        roadmap.append({
            "week": week_data.get("week", 0),
            "topic": ", ".join(week_data.get("learning_goals", [])) if isinstance(week_data.get("learning_goals"), list) else str(week_data.get("learning_goals", "")),
            "project": ", ".join(week_data.get("projects", [])) if isinstance(week_data.get("projects"), list) else str(week_data.get("projects", "")),
            "courses": week_data.get("courses", []),
            "practice_websites": week_data.get("practice_websites", []),
        })
    
    return {
        "roadmap": roadmap
    }
