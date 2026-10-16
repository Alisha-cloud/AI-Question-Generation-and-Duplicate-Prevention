
from pathlib import Path

from app.detector import DuplicateDetector
from app.repository import JsonQuestionRepository


def make_detector(tmp_path: Path) -> DuplicateDetector:
    """Create an isolated question repository for each test."""
    data_file = tmp_path / "questions.json"
    data_file.write_text("[]", encoding="utf-8")
    repository = JsonQuestionRepository(str(data_file))

    # The repository seeds sample questions when empty; clear them so
    # every test starts with only the questions explicitly added below.
    data_file.write_text("[]", encoding="utf-8")

    return DuplicateDetector(repository)


def test_exact_duplicate_is_detected(tmp_path):
    detector = make_detector(tmp_path)
    detector.repository.add_question(
        "Define the reflection of light.",
        {"subject": "Physics"},
    )

    result = detector.check("  DEFINE the reflection of light!!! ")

    assert result.status == "duplicate"
    assert result.best_similarity == 1.0
    assert any(match.match_type == "exact_normalized" for match in result.matches)


def test_semantic_paraphrase_is_detected(tmp_path):
    detector = make_detector(tmp_path)
    detector.repository.add_question("What is reflection of light?", {})

    result = detector.check("Explain the meaning of light reflection.")

    assert result.status in {"duplicate", "review"}
    assert result.matches
    assert result.best_similarity >= detector.settings.review_threshold


def test_different_question_is_not_marked_duplicate(tmp_path):
    detector = make_detector(tmp_path)
    detector.repository.add_question("What is reflection of light?", {})

    result = detector.check(
        "What is the difference between regular and diffuse reflection?"
    )

    # A borderline result may legitimately require human review.
    assert result.status in {"unique", "review"}


def test_numeric_condition_difference_is_not_auto_accepted_as_duplicate(
    tmp_path,
):
    detector = make_detector(tmp_path)
    detector.repository.add_question(
        "The angle of incidence is 30 degrees. What is the angle of reflection?",
        {},
    )

    result = detector.check(
        "The angle of incidence is 45 degrees. What is the angle of reflection?"
    )

    assert result.status != "duplicate"


def test_tags_do_not_change_duplicate_identity(tmp_path):
    detector = make_detector(tmp_path)
    detector.repository.add_question(
        "Define the reflection of light.",
        {"subject": "Physics", "difficulty": "easy"},
    )

    # Tags are not passed into the detector's identity comparison.
    result = detector.check("Define the reflection of light.")

    assert result.status == "duplicate"


def test_empty_repository_returns_unique(tmp_path):
    detector = make_detector(tmp_path)

    result = detector.check("Explain refraction of light.")

    assert result.status == "unique"
    assert result.matches == []
    assert result.best_similarity == 0.0
