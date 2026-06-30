from app.services.resume_service import parse_resume_text


def test_parse_resume_text_extracts_core_fields():
    text = """
    Jane Student
    jane@example.com
    Skills
    Python React PostgreSQL Docker
    Education
    B.Tech Computer Science
    Projects
    Built a job matching platform
    Certifications
    AWS Cloud Practitioner
    """

    parsed = parse_resume_text(text)

    assert parsed["name"] == "Jane Student"
    assert parsed["email"] == "jane@example.com"
    assert "python" in parsed["skills"]
    assert "react" in parsed["skills"]
    assert parsed["education"]
    assert parsed["projects"]
