import json
import re
from google import genai
from google.genai import types

from app.config import get_settings
from app.detector import DuplicateDetector
from app.repository import JsonQuestionRepository
from app.schemas import GeneratedQuestion


class QuestionGenerator:
    # Generation-time avoidance; the independent detector is a separate safeguard.
    def __init__(self, repository: JsonQuestionRepository, detector: DuplicateDetector):
        self.repository = repository
        self.detector = detector
        self.settings = get_settings()

    def generate(self, topic: str, count: int, tags: dict) -> list[GeneratedQuestion]:
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured. Add it to backend/.env.")
        client = genai.Client(api_key=self.settings.gemini_api_key)

        existing = self.repository.list_questions()
        topic_tokens = set(re.findall(r"[a-z0-9]+", topic.casefold()))
        ranked = sorted(
            existing,
            key=lambda row: sum(
                token in set(re.findall(r"[a-z0-9]+", row.question.casefold()))
                for token in topic_tokens
            ),
            reverse=True,
        )
        # Bounded context keeps the prompt predictable as the collection grows.
        context = [row.question for row in ranked[:30]]
        prompt = f'''
You create high-quality educational questions.
Topic: {topic}
Requested count: {count}
Tags (metadata only): {json.dumps(tags, ensure_ascii=False)}
Existing questions to avoid:
{json.dumps(context, ensure_ascii=False)}

Return ONLY valid JSON: {{"questions": ["question one", "question two"]}}
Generate genuinely new questions, not paraphrases. Cover different learning objectives.
Do not merely change names, numbers, or punctuation. Return no more than {count}.
'''
        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5, response_mime_type="application/json"
            ),
        )
        try:
            candidates = json.loads(response.text or "{}").get("questions", [])
        except (json.JSONDecodeError, TypeError):
            raise RuntimeError("The LLM returned invalid JSON. Please retry.")

        results = []
        for candidate in candidates[:count]:
            if not isinstance(candidate, str) or len(candidate.strip()) < 5:
                continue
            candidate = candidate.strip()
            check = self.detector.check(candidate)
            if check.status == "unique":
                self.repository.add_question(candidate, tags)
                results.append(GeneratedQuestion(
                    question=candidate, status="accepted",
                    reason="Passed the independent duplicate detector."
                ))
            else:
                results.append(GeneratedQuestion(
                    question=candidate, status=check.status, reason=check.explanation
                ))
        return results
