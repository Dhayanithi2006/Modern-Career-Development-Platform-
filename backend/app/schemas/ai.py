from typing import Any

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class AssistantSessionCreate(BaseModel):
    title: str = "Career Planning"


class RoadmapCreate(BaseModel):
    target_role: str
    duration_weeks: int = Field(default=4, ge=1, le=52)


class InterviewStart(BaseModel):
    target_role: str
    difficulty: str = "medium"
    interview_type: str = "mixed"


class InterviewAnswer(BaseModel):
    question_id: int
    answer: str = Field(min_length=1)


class GenericAIResponse(BaseModel):
    data: dict[str, Any]
