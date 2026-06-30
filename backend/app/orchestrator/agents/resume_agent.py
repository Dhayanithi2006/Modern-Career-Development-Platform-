from app.orchestrator.state import CareerState
from app.ai.gemini_client import gemini_client
from app.ai.prompts.templates import RESUME_ANALYZER_PROMPT
from app.utils.text import extract_json_object


def process_resume(state: CareerState) -> dict:
    """
    Resume Agent: Full ATS analysis with skill extraction using the
    comprehensive Resume Analyzer prompt.
    """
    resume_text = state.get("resume_text", "")
    if not resume_text:
        return {}

    prompt = RESUME_ANALYZER_PROMPT.format(resume_text=resume_text[:8000])
    response = gemini_client.generate_text(prompt)
    data = extract_json_object(response) or {}

    # Merge all skill categories into a unified extracted_skills list
    all_skills = []
    for category in ("technical_skills", "programming_languages", "frameworks",
                     "databases", "cloud_technologies", "tools", "hidden_skills"):
        items = data.get(category, [])
        if isinstance(items, list):
            for item in items:
                skill_name = item if isinstance(item, str) else str(item)
                all_skills.append({
                    "skill": skill_name,
                    "category": category,
                    "level": "Intermediate",
                    "experience": "Resume"
                })

    return {
        "ats_score": float(data.get("ats_score", 0.0)),
        "ats_feedback": str(data.get("ats_score_explanation", "No feedback available.")),
        "extracted_skills": all_skills,
        "resume_analysis": data,  # store full analysis for downstream agents
    }
