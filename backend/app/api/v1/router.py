from fastapi import APIRouter

from app.api.v1.endpoints import assistant, auth, dashboard, interviews, jobs, matches, profile, resumes, roadmaps, skill_gap

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(resumes.router, prefix="/resume", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(skill_gap.router, prefix="/skill-gap", tags=["skill-gap"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
