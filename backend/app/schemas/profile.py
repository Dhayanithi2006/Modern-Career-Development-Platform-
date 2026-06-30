from pydantic import BaseModel, Field


class ProfileUpsert(BaseModel):
    phone: str | None = None
    location: str | None = None
    education_level: str | None = None
    college: str | None = None
    graduation_year: int | None = None
    target_role: str | None = None
    target_industry: str | None = None
    experience_level: str | None = None


class ProfileRead(ProfileUpsert):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str | None = None
    proficiency_level: int = Field(default=1, ge=1, le=5)


class SkillRead(BaseModel):
    id: int
    name: str
    category: str | None = None
    proficiency_level: int
