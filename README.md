# Induseuro Labs — Question 2: AI Question Generation & Duplicate Prevention

FastAPI starter for the Induseuro Labs AI/ML internship assignment.

## Included
- Exact matching after case, punctuation, and whitespace normalization.
- Semantic similarity using sentence-transformers embeddings.
- Seed corpus from the assignment's reflection-of-light examples.
- JSON persistence for a simple local demo.
- API endpoints for listing, checking, adding, and generating questions.
- Optional Gemini generation using `google-genai`.
- Flexible key-value tags; tags never determine duplicate status.

## Architecture
`FastAPI -> services -> independent duplicate detector -> repository`

Generation-time avoidance retrieves a bounded set of relevant existing questions and provides them to the LLM. Every candidate is then independently checked before being stored.

## Run locally (Windows PowerShell)
Python 3.12 recommended.

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI and `http://127.0.0.1:8000/health` for health.

The first semantic request may download the embedding model and can take a while.

## API examples
Check a candidate:

```powershell
$body = @{ question = "Define the reflection of light."; tags = @{ subject = "Physics" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/duplicates/check -ContentType "application/json" -Body $body
```

Generate (requires `GEMINI_API_KEY` in `.env`):

```powershell
$body = @{ topic = "reflection of light"; count = 3; tags = @{ subject = "Physics" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/questions/generate -ContentType "application/json" -Body $body
```

## Configuration
See `backend/.env.example`.
- `DATA_FILE`: JSON persistence path
- `EMBEDDING_MODEL`: sentence-transformers model
- `DUPLICATE_THRESHOLD`: similarity at/above which a candidate is classified as duplicate
- `REVIEW_THRESHOLD`: borderline similarity threshold
- `GEMINI_API_KEY`: optional generation key
- `GEMINI_MODEL`: model identifier available to your account

Thresholds are initial defaults, not universal truths. Calibrate against the provided corpus and report false positives/negatives.

## Evaluation
Install dev requirements and run from `backend/`:

```powershell
pip install -r requirements-dev.txt
python -m app.evaluate
pytest
```

Inspect borderline cases rather than optimizing only aggregate scores. The supplied corpus is too small to establish general accuracy.

## Deployment options
- API: Render or Railway free/trial offerings where available; plan limits change, and free instances may sleep.
- Database: MongoDB Atlas free cluster for shared durable persistence. This starter uses JSON for a fast local MVP; replace the repository adapter before multi-instance deployment.
- Frontend (later): Vercel or Netlify.
- Never commit `.env`; add keys through the host's environment settings.

## Before calling it production-ready
Add managed database persistence, auth/rate limits for public write endpoints, request IDs, structured logs, provider timeouts/retries, CI tests, and dependency/model version pinning.
