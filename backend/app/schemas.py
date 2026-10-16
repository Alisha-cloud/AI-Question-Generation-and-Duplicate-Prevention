from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class QuestionCreate(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    tags: dict[str, Any] = Field(default_factory=dict)


class QuestionRecord(QuestionCreate):
    id: str
    created_at: datetime = Field(default_factory=utc_now)


class DuplicateCheckRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    tags: dict[str, Any] = Field(default_factory=dict)


class DuplicateMatch(BaseModel):
    question_id: str
    question: str
    similarity: float
    match_type: str


class DuplicateCheckResponse(BaseModel):
    status: str
    normalized_question: str
    best_similarity: float
    matches: list[DuplicateMatch]
    explanation: str


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)
    count: int = Field(default=5, ge=1, le=20)
    tags: dict[str, Any] = Field(default_factory=dict)


class GeneratedQuestion(BaseModel):
    question: str
    status: str
    reason: str


class GenerateResponse(BaseModel):
    topic: str
    requested_count: int
    accepted_count: int
    results: list[GeneratedQuestion]
    note: str | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
