# AI Question Generation and Duplicate Prevention

An AI-powered question generation system that generates new questions using a Large Language Model (LLM) while identifying exact duplicates, semantic duplicates, and potentially similar questions before they are stored.

The project combines **LLM-based question generation, sentence embeddings, similarity scoring, and rule-based validation** to reduce repetitive questions and maintain a more useful question bank.

## 1. Problem Statement

Automatically generated questions may repeat existing questions even when their wording differs. For example:

- What is reflection of light?
- Define the reflection of light.
- Explain the meaning of light reflection.

Although these questions use different words, they ask essentially the same thing.

The objective of this project is to generate relevant questions while independently checking them against an existing question bank to prevent duplicates and flag uncertain matches for human review.

## 2. Objectives

- Generate questions using an LLM.
- Reduce duplicate generation by providing relevant existing questions as context.
- Detect exact duplicates using text normalization.
- Detect semantic duplicates using sentence embeddings and cosine similarity.
- Flag ambiguous or potentially similar questions for manual review.
- Support arbitrary key-value tags without allowing tags to determine question identity.
- Evaluate duplicate detection using a predefined question corpus.
- Provide API endpoints through FastAPI for testing and integration.

## 3. Key Features

### AI-Based Question Generation

The system uses the Google Gemini API to generate questions based on a supplied topic and existing question-bank context.

It selects up to 30 relevant existing questions using lexical token overlap and includes them in the generation prompt. The prompt instructs the LLM to avoid generating questions that repeat existing content.

### Independent Duplicate Detection

Duplicate detection is implemented separately from question generation. This means generated questions are checked by the detector rather than being accepted solely because the LLM claims they are new.

The detector uses the following process:

1. Normalize the candidate and existing questions.
2. Check for exact matches after normalization.
3. Generate sentence embeddings for semantic comparison.
4. Calculate cosine similarity scores.
5. Apply configurable thresholds to classify the candidate.
6. Store questions classified as unique and return duplicates or uncertain matches without storing them.

### Exact Duplicate Detection

Text normalization uses Unicode normalization, case folding, punctuation and symbol handling, and whitespace normalization.

This helps identify questions that are textually equivalent despite differences in capitalization, punctuation, or spacing.

### Semantic Duplicate Detection

The project uses the `sentence-transformers/all-MiniLM-L6-v2` embedding model to represent questions as numerical vectors.

Cosine similarity is used to compare the meaning of a candidate question with existing questions.

The default thresholds are:

- **0.82 and above:** Potential duplicate, subject to additional validation.
- **0.68 to below 0.82:** Requires review.
- **Below 0.68:** Generally classified as unique.

These are configurable thresholds, not universal guarantees of semantic equivalence.

### Human Review for Uncertain Questions

Questions with potentially overlapping meanings, broad wording, or different numerical conditions may require manual review.

For example, a broad question such as "What is reflection?" may be related to "What is reflection of light?" but is not necessarily identical. The system can flag such cases rather than automatically rejecting them.

### Tag Independence

Questions may contain arbitrary metadata, such as:

- Subject
- Topic
- Difficulty
- Department
- Category

These tags can help organize questions, but they do not determine whether two questions are duplicates. Duplicate identity is based on question text and its semantic similarity.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API framework | FastAPI |
| LLM integration | Google Gemini API |
| Embedding model | Sentence Transformers |
| Similarity calculation | Cosine similarity |
| Data validation | Pydantic |
| Data persistence | JSON file |
| Testing | Pytest |
| API documentation | Swagger UI / OpenAPI |

## 5. Project Structure

```text
induseuro-question2-starter/
├── .gitignore
├── README.md
└── backend/
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── pytest.ini
    ├── app/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── detector.py
    │   ├── evaluate.py
    │   ├── generation.py
    │   ├── main.py
    │   ├── normalization.py
    │   ├── repository.py
    │   └── schemas.py
    ├── data/
    │   └── questions.json
    └── tests/
        ├── test_api.py
        ├── test_detector.py
        └── test_normalization.py
```

## 6. Prerequisites

Install the following before running the project:

- Python 3.12 recommended.
- Git.
- A Google Gemini API key for question generation.
- Internet access for API calls and initial embedding-model download.

Other Python versions may work, depending on the compatibility of the installed dependencies.

## 7. Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/Alisha-cloud/AI-Question-Generation-and-Duplicate-Prevention.git
cd AI-Question-Generation-and-Duplicate-Prevention
```

### Step 2: Create and activate a virtual environment

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you are using another supported Python version, replace `3.12` with that version.

### Step 3: Install dependencies

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

### Step 4: Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and configure your Gemini API key:

```env
APP_NAME=Induseuro Question Intelligence API
API_PREFIX=/api/v1
DATA_FILE=./data/questions.json
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DUPLICATE_THRESHOLD=0.82
REVIEW_THRESHOLD=0.68
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173
```

Replace `your_gemini_api_key` with your own key. Do not commit the `.env` file or expose your API key publicly.

The duplicate detector can be tested without a Gemini API key. The key is required for LLM-based question generation.

### Step 5: Start the API server

From the `backend` directory, run:

```powershell
python -m uvicorn app.main:app --reload
```

The API should be available at:

- API base: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Use the interactive documentation to inspect the available endpoints and their request and response formats.

## 8. Configuration

The duplicate detection behavior can be adjusted through environment variables.

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Authenticates requests to the Gemini API |
| `GEMINI_MODEL` | Specifies the generation model |
| `EMBEDDING_MODEL` | Specifies the sentence embedding model |
| `DUPLICATE_THRESHOLD` | Similarity threshold for duplicate classification |
| `REVIEW_THRESHOLD` | Similarity threshold for review classification |
| `DATA_FILE` | Location of the JSON question repository |
| `API_PREFIX` | API route prefix |
| `CORS_ORIGINS` | Configured allowed frontend origins |

Changing thresholds affects the trade-off between duplicate detection and incorrectly flagging distinct questions. Thresholds should be calibrated against a larger, representative evaluation dataset.

## 9. Evaluation

The project includes a predefined corpus containing ten questions about reflection of light. The corpus covers exact duplicates, semantic paraphrases, distinct questions, numerical conditions, and an ambiguous question.

The evaluation command is:

```powershell
python -m app.evaluate
```

Run it from the `backend` directory.

### Evaluation Results

The latest local evaluation produced the following results:

| Metric | Result |
|---|---:|
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1-score | 1.000 |
| True positives | 4 |
| True negatives | 4 |
| False positives | 0 |
| False negatives | 0 |

The binary metrics exclude the ambiguous question, which is handled separately through review. Review classifications for distinct questions are treated as non-duplicates for this particular binary calculation.

**Important:** These results are from a small, predefined corpus with eight binary-labelled cases. They demonstrate the behavior of the current test set, not guaranteed performance on a large real-world question bank. More diverse questions and manually verified labels are required for a meaningful general evaluation.

## 10. Automated Testing

The project includes unit and API tests covering:

- API health checking.
- Exact duplicate detection.
- Semantic paraphrase detection.
- Distinct question handling.
- Numerical-condition differences.
- Independence of tags from duplicate identity.
- Empty repository behavior.
- Text normalization.

Run the test suite from the `backend` directory:

```powershell
python -m pytest -v
```

The current implementation passed all nine tests in the local test run.

## 11. Design Decisions

### Why use an LLM and an independent detector?

An LLM can generate natural questions but may repeat existing content. An independent detector provides a separate validation step, reducing reliance on the generation model's own assessment.

### Why use sentence embeddings?

Sentence embeddings capture semantic relationships that simple string comparison cannot identify. Cosine similarity provides a numerical measure of how similar two question representations are.

### How is context selected?

The current implementation ranks existing questions by lexical token overlap with the requested topic and includes up to 30 selected questions in the generation prompt.

This is a practical initial approach, but the number of questions is not a strict token-budget guarantee. A production system should estimate token usage, reserve room for the prompt and output, and select context within a configurable token budget.

### How does the system handle scale?

The current implementation uses JSON persistence and recomputes embeddings during duplicate checks. This is suitable for a small prototype but can become inefficient as the question bank grows.

For larger deployments, possible improvements include:

- Database-backed question storage.
- Cached embeddings.
- Vector indexes for efficient similarity search.
- Batch embedding and comparison.
- Explicit token-budget management.
- Persistent storage and distributed processing where required.
- Evaluation on larger, labelled datasets.

## 12. Current Limitations

- JSON storage is intended for a small local prototype, not concurrent multi-instance production deployments.
- Embeddings are recomputed during duplicate checks, which increases processing time as the repository grows.
- Context selection uses lexical overlap and a fixed maximum number of questions rather than a strict token budget.
- Similarity thresholds may require adjustment for different subjects and question styles.
- Some borderline cases require human review.
- The evaluation corpus is small and cannot establish general-purpose accuracy.
- LLM generation requires API access, and generation quality depends on the model response and prompt.

## 13. Future Enhancements

- Replace JSON persistence with a production database.
- Cache sentence embeddings and introduce vector similarity search.
- Add strict token-budget-aware context selection.
- Improve subject-aware and topic-aware retrieval.
- Expand the evaluation corpus with manually labelled duplicate and non-duplicate pairs.
- Tune thresholds using precision-recall analysis.
- Add monitoring for false positives, false negatives, and review rates.
- Introduce authentication, rate limiting, and deployment-specific security controls.

## 14. Security Notes

- Store API keys in environment variables.
- Never commit `.env` files, API credentials, or virtual environments.
- Keep `.env.example` free of real credentials.
- Review API authentication, request limits, and persistence requirements before public deployment.

## 15. Author

**Alisha-cloud**

GitHub repository:  
https://github.com/Alisha-cloud/AI-Question-Generation-and-Duplicate-Prevention

---

*Developed as an implementation of AI-based question generation and duplicate prevention using an LLM, sentence embeddings, and independent validation.*
