# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, START, END
from app.orchestrator.state import CareerState
from app.orchestrator.agents.resume_agent import process_resume
from app.orchestrator.agents.job_agent import match_jobs
from app.orchestrator.agents.roadmap_agent import generate_roadmap
from app.orchestrator.agents.project_agent import recommend_projects
from app.orchestrator.agents.interview_agent import generate_interview


def build_career_graph() -> StateGraph:
    """
    Builds the full LangGraph state machine for the Career Orchestrator.

    Pipeline:
    Resume Agent -> Job Agent -> Roadmap Agent -> Project Agent -> Interview Agent
    """
    workflow = StateGraph(CareerState)

    # Add all agent nodes
    workflow.add_node("resume_agent", process_resume)
    workflow.add_node("job_agent", match_jobs)
    workflow.add_node("roadmap_agent", generate_roadmap)
    workflow.add_node("project_agent", recommend_projects)
    workflow.add_node("interview_agent", generate_interview)

    # Wire the full pipeline
    workflow.add_edge(START, "resume_agent")
    workflow.add_edge("resume_agent", "job_agent")
    workflow.add_edge("job_agent", "roadmap_agent")
    workflow.add_edge("roadmap_agent", "project_agent")
    workflow.add_edge("project_agent", "interview_agent")
    workflow.add_edge("interview_agent", END)

    return workflow.compile()


# Singleton instance of the compiled graph
career_orchestrator = build_career_graph()
