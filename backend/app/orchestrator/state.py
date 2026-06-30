from typing import Any, List, TypedDict, Annotated
import operator
# pyrefly: ignore [missing-import]
from langchain_core.messages import BaseMessage


def merge_list(a: List[Any], b: List[Any]) -> List[Any]:
    if not a:
        return b
    if not b:
        return a
    return a + b


class CareerState(TypedDict):
    """
    Main state for the AI Career Copilot orchestrator.
    Flows through: Resume Agent -> Job Agent -> Roadmap Agent -> Project Agent -> Interview Agent
    """
    user_id: int
    
    # Resume Pipeline
    resume_text: str
    ats_score: float
    ats_feedback: str
    extracted_skills: List[dict]
    resume_analysis: dict  # Full analysis from Resume Agent
    
    # Jobs Pipeline
    matched_jobs: List[dict]
    missing_skills: List[str]
    
    # Roadmap Pipeline
    roadmap: List[dict]
    
    # Project Recommendation Pipeline
    recommended_projects: List[dict]
    
    # Interview Pipeline
    interview_questions: List[dict]
    
    # Assistant / Memory
    messages: Annotated[List[BaseMessage], merge_list]
