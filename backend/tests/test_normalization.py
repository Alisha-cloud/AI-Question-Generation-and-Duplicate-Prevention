from app.normalization import normalize_question


def test_punctuation_and_case_normalize():
    assert normalize_question("Define the reflection of light.") == normalize_question(
        "  DEFINE the reflection of light!!! "
    )


def test_whitespace_normalizes():
    assert normalize_question("What   is reflection?") == normalize_question("What is reflection?")
