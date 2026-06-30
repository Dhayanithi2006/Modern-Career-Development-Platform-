from app.models.job import Job
from app.services.matching_service import score_job_match


def test_score_job_match_returns_missing_skills():
    job = Job(
        title="Frontend Developer",
        company="Acme",
        location="Remote",
        description="React TypeScript SQL Docker",
        requirements="React, TypeScript, SQL, Docker",
        source="test",
    )

    score = score_job_match({"skills": ["react"]}, job)

    assert score["overall_score"] > 0
    assert "typescript" in score["missing_skills"]
    assert "sql" in score["missing_skills"]
