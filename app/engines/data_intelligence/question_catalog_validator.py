from typing import Any

from app.engines.data_intelligence.question_classifier import (
    QuestionClassifier,
)
from app.services.question_catalog import (
    get_question_catalog,
)


class QuestionCatalogValidator:
    """
    Validate every predefined AI-FOS catalogue question
    against the QuestionClassifier.

    This first-stage validator identifies classifier gaps
    before questions are exposed to users.
    """

    def __init__(self) -> None:
        self.classifier = QuestionClassifier()

    def validate(self) -> dict[str, Any]:
        catalog = get_question_catalog()

        results: list[dict[str, Any]] = []

        total_questions = 0
        supported_count = 0
        unknown_count = 0

        for category in catalog:
            category_name = category.get(
                "category",
                "Unknown",
            )

            for question_item in category.get(
                "questions",
                [],
            ):
                total_questions += 1

                question_id = question_item.get(
                    "id",
                    "",
                )

                question = question_item.get(
                    "question",
                    "",
                )

                classification = self.classifier.classify(
                    question
                )

                domain = classification.get(
                    "domain",
                    "unknown",
                )

                intent = classification.get(
                    "intent",
                    "unknown",
                )

                target = classification.get(
                    "target",
                )

                is_supported = (
                    domain != "unknown"
                    and intent != "unknown"
                )

                if is_supported:
                    supported_count += 1
                    status = "classified"
                else:
                    unknown_count += 1
                    status = "unknown"

                results.append(
                    {
                        "id": question_id,
                        "category": category_name,
                        "question": question,
                        "domain": domain,
                        "intent": intent,
                        "target": target,
                        "status": status,
                    }
                )

        coverage_percentage = (
            round(
                (
                    supported_count
                    / total_questions
                )
                * 100,
                2,
            )
            if total_questions
            else 0.0
        )

        unknown_questions = [
            result
            for result in results
            if result["status"] == "unknown"
        ]

        return {
            "total_questions": total_questions,
            "classified_questions": supported_count,
            "unknown_questions_count": unknown_count,
            "coverage_percentage": coverage_percentage,
            "unknown_questions": unknown_questions,
            "results": results,
        }