import re
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.normalization import normalize_question
from app.repository import JsonQuestionRepository
from app.schemas import DuplicateCheckResponse, DuplicateMatch


@dataclass
class CandidateScore:
    record_id: str
    question: str
    score: float
    match_type: str


def extract_numbers(text: str) -> set[str]:
    """Extract numeric values so different problem conditions are not conflated."""
    return set(re.findall(r"(?<!\w)\d+(?:\.\d+)?", text))


def has_different_numeric_conditions(
    candidate: str,
    matched_question: str,
) -> bool:
    """Detect whether similar questions specify different numeric conditions."""
    candidate_numbers = extract_numbers(candidate)
    matched_numbers = extract_numbers(matched_question)

    return (
        bool(candidate_numbers or matched_numbers)
        and candidate_numbers != matched_numbers
    )


class DuplicateDetector:
    """Detect exact and semantic duplicates in the question repository."""

    def __init__(self, repository: JsonQuestionRepository):
        self.repository = repository
        self.settings = get_settings()
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(
                self.settings.embedding_model
            )
        return self._model

    def _embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._get_model().encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)

    def check(self, candidate: str) -> DuplicateCheckResponse:
        candidate_normalized = normalize_question(candidate)
        records = self.repository.list_questions()

        if not records:
            return DuplicateCheckResponse(
                status="unique",
                normalized_question=candidate_normalized,
                best_similarity=0.0,
                matches=[],
                explanation=(
                    "The collection is empty; no duplicate candidates "
                    "were found."
                ),
            )

        # First, check exact matches after normalization.
        exact = [
            row
            for row in records
            if normalize_question(row.question) == candidate_normalized
        ]

        if exact:
            return DuplicateCheckResponse(
                status="duplicate",
                normalized_question=candidate_normalized,
                best_similarity=1.0,
                matches=[
                    DuplicateMatch(
                        question_id=row.id,
                        question=row.question,
                        similarity=1.0,
                        match_type="exact_normalized",
                    )
                    for row in exact
                ],
                explanation=(
                    "Exact duplicate after case, punctuation, and "
                    "whitespace normalization."
                ),
            )

        # Compare the candidate with existing questions using embeddings.
        vectors = self._embed(
            [candidate] + [row.question for row in records]
        )
        similarities = vectors[1:] @ vectors[0]
        order = np.argsort(similarities)[::-1]

        best_index = int(order[0]) if len(order) else None
        best = (
            float(similarities[best_index])
            if best_index is not None
            else 0.0
        )
        best_question = (
            records[best_index].question
            if best_index is not None
            else ""
        )

        matches = []
        for idx in order[:5]:
            score = float(similarities[int(idx)])

            if score >= self.settings.review_threshold:
                row = records[int(idx)]
                matches.append(
                    DuplicateMatch(
                        question_id=row.id,
                        question=row.question,
                        similarity=round(score, 4),
                        match_type="semantic",
                    )
                )

        # Decide whether the candidate is a duplicate, needs review, or is unique.
        
        # Decide whether the candidate is a duplicate, needs review, or is unique.
        candidate_words = candidate_normalized.split()
        matched_normalized = normalize_question(best_question)
        matched_words = matched_normalized.split()

        # Very broad questions can be similar to a specific question
        # without asking the same thing. Flag them for human review.
        broad_question = (
            len(candidate_words) <= 4
            and len(matched_words) >= len(candidate_words) + 2
            and best >= self.settings.review_threshold
        )

        if broad_question:
            status = "review"
            explanation = (
                "The candidate is broad and resembles a more specific "
                "question. Human review is recommended."
            )

        elif best >= self.settings.duplicate_threshold:
            if has_different_numeric_conditions(candidate, best_question):
                status = "review"
                explanation = (
                    "The questions are semantically similar but specify "
                    "different numerical conditions. Human review is required."
                )
            else:
                status = "duplicate"
                explanation = (
                    "High semantic similarity found. Inspect the matched "
                    "question for domain or assessment-intent differences."
                )

        elif best >= self.settings.review_threshold:
            status = "review"
            explanation = (
                "Borderline semantic match; human review is recommended."
            )

        else:
            status = "unique"
            explanation = (
                "No exact or high-similarity semantic duplicate was found."
            )


        return DuplicateCheckResponse(
            status=status,
            normalized_question=candidate_normalized,
            best_similarity=round(best, 4),
            matches=matches,
            explanation=explanation,
        )