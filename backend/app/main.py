from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.detector import DuplicateDetector
from app.generation import QuestionGenerator
from app.repository import JsonQuestionRepository
from app.schemas import (
    DuplicateCheckRequest, DuplicateCheckResponse, GenerateRequest,
    GenerateResponse, HealthResponse, QuestionCreate, QuestionRecord
)

settings = get_settings()
repository = JsonQuestionRepository(settings.data_file)
detector = DuplicateDetector(repository)
generator = QuestionGenerator(repository, detector)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI question generation with independent duplicate detection.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    return {"status": "ok", "app": settings.app_name}


@app.get(f"{settings.api_prefix}/questions", response_model=list[QuestionRecord], tags=["questions"])
def list_questions(limit: int = Query(default=100, ge=1, le=500)):
    return repository.list_questions()[:limit]


@app.post(f"{settings.api_prefix}/questions", response_model=QuestionRecord, tags=["questions"])
def create_question(payload: QuestionCreate):
    try:
        check = detector.check(payload.question)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Duplicate detection unavailable: {type(exc).__name__}")
    if check.status != "unique":
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Question was not saved because a duplicate or review case was detected.",
                "duplicate_check": check.model_dump(mode="json"),
            },
        )
    return repository.add_question(payload.question, payload.tags)


@app.post(
    f"{settings.api_prefix}/duplicates/check",
    response_model=DuplicateCheckResponse,
    tags=["duplicate detection"],
)
def check_duplicate(payload: DuplicateCheckRequest):
    try:
        return detector.check(payload.question)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Duplicate detection unavailable: {type(exc).__name__}")


@app.post(f"{settings.api_prefix}/questions/generate", response_model=GenerateResponse, tags=["generation"])
def generate_questions(payload: GenerateRequest):
    try:
        results = generator.generate(payload.topic, payload.count, payload.tags)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Generation provider failed: {type(exc).__name__}")
    accepted = sum(item.status == "accepted" for item in results)
    return GenerateResponse(
        topic=payload.topic, requested_count=payload.count,
        accepted_count=accepted, results=results,
        note="Generation-time avoidance and independent duplicate detection are separate safeguards."
    )
