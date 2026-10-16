from tempfile import TemporaryDirectory
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from app.detector import DuplicateDetector
from app.repository import JsonQuestionRepository

CORPUS = [
    "What is reflection of light?",
    "Define the reflection of light.",
    "What do you understand by the reflection of light?",
    "Explain the meaning of light reflection.",
    "State the laws of reflection of light.",
    "What is the angle of reflection?",
    "The angle of incidence is 30°. What is the angle of reflection?",
    "What is reflection?",
    "What is the difference between regular and diffuse reflection?",
    "Define the reflection of light.",
]
# Q8 ("What is reflection?") is ambiguous and excluded from binary metrics.
EXPECTED_DUPLICATE = {
    1: True, 2: True, 3: True, 4: False, 5: False,
    6: False, 7: None, 8: False, 9: True,
}


def main():
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "questions.json"
        path.write_text("[]", encoding="utf-8")
        repo = JsonQuestionRepository(str(path))
        # The repository seeds the sample corpus on an empty file; clear it for incremental evaluation.
        path.write_text("[]", encoding="utf-8")
        detector = DuplicateDetector(repo)
        y_true, y_pred = [], []

        # Insert Q1, then evaluate each subsequent question against previously seen questions.
        repo.add_question(CORPUS[0], {})
        for idx in range(1, len(CORPUS)):
            candidate = CORPUS[idx]
            result = detector.check(candidate)
            expected = EXPECTED_DUPLICATE[idx]
            if expected is not None:
                y_true.append(int(expected))
                y_pred.append(int(result.status == "duplicate"))
            print(f"Q{idx+1}: expected={expected!s:5} predicted={result.status:9} "
                  f"score={result.best_similarity:.4f} :: {candidate}")
            repo.add_question(candidate, {})

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        print("\nBinary metrics (ambiguous Q8 excluded):")
        print(f"Accuracy : {accuracy_score(y_true, y_pred):.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall   : {recall:.3f}")
        print(f"F1       : {f1:.3f}")
        print("Confusion matrix [ [TN, FP], [FN, TP] ]:")
        print(confusion_matrix(y_true, y_pred, labels=[0, 1]))


if __name__ == "__main__":
    main()
