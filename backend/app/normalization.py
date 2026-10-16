import re
import unicodedata


def normalize_question(text: str) -> str:
    # Normalization for exact-match checks, not semantic equivalence.
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(
        " " if unicodedata.category(ch)[0] in {"P", "S"} else ch
        for ch in text
    )
    return re.sub(r"\s+", " ", text).strip()
