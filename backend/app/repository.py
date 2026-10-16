import json
from pathlib import Path
from threading import RLock
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

from app.schemas import QuestionRecord


class JsonQuestionRepository:
    # Single-process local repository. Replace with managed DB for multi-instance use.
    def __init__(self, file_path: str):
        self.path = Path(file_path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        if not self.path.exists():
            self._write([])
        if not self._read():
            self.seed_if_empty()

    def _read(self) -> list[dict[str, Any]]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _write(self, rows: list[dict[str, Any]]) -> None:
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temp_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self.path)

    def list_questions(self) -> list[QuestionRecord]:
        with self._lock:
            result = []
            for row in self._read():
                try:
                    result.append(QuestionRecord.model_validate(row))
                except Exception:
                    continue
            return result

    def add_question(self, question: str, tags: dict[str, Any] | None = None) -> QuestionRecord:
        record = QuestionRecord(
            id=str(uuid4()), question=question.strip(), tags=tags or {},
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            rows = self._read()
            rows.append(record.model_dump(mode="json"))
            self._write(rows)
        return record

    def seed_if_empty(self) -> None:
        corpus = [
            ("What is reflection of light?", {"subject": "Physics", "concept": "reflection of light"}),
            ("Define the reflection of light.", {"subject": "Physics", "concept": "reflection of light"}),
            ("What do you understand by the reflection of light?", {"subject": "Physics", "concept": "reflection of light"}),
            ("Explain the meaning of light reflection.", {"subject": "Physics", "concept": "reflection of light"}),
            ("State the laws of reflection of light.", {"subject": "Physics", "concept": "reflection of light"}),
            ("What is the angle of reflection?", {"subject": "Physics", "concept": "reflection of light"}),
            ("The angle of incidence is 30°. What is the angle of reflection?", {"subject": "Physics", "concept": "reflection of light"}),
            ("What is reflection?", {"subject": "Physics", "concept": "reflection"}),
            ("What is the difference between regular and diffuse reflection?", {"subject": "Physics", "concept": "reflection of light"}),
            ("Define the reflection of light.", {"subject": "Physics", "concept": "reflection of light"}),
        ]
        with self._lock:
            if self._read():
                return
            rows = []
            for question, tags in corpus:
                rows.append(QuestionRecord(
                    id=str(uuid4()), question=question, tags=tags,
                    created_at=datetime.now(timezone.utc)
                ).model_dump(mode="json"))
            self._write(rows)
