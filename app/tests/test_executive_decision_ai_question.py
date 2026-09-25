from pathlib import Path

from app.engines.data_intelligence.question_classifier import (
    QuestionClassifier,
)
from app.services.ai_question_engine import (
    AIQuestionEngine,
)
from app.services.financial_model_service import (
    FinancialModelService,
)


class FakeWorkspaceService:
    def __init__(
        self,
        root: Path,
    ) -> None:
        self.root = root

    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ):
        financial_model = (
            self.root
            / "financial_model"
        )

        ai_knowledge = (
            self.root
            / "ai_knowledge"
        )

        financial_model.mkdir(
            parents=True,
            exist_ok=True,
        )

        ai_knowledge.mkdir(
            parents=True,
            exist_ok=True,
        )

        return {
            "organisation_id": organisation_id,
            "paths": {
                "financial_model": str(
                    financial_model
                ),
                "ai_knowledge": str(
                    ai_knowledge
                ),
            },
        }


class FakeKnowledgeReader:
    def get_summary(
        self,
        folder: Path,
    ):
        return {
            "status": "available",
            "organisation_name": (
                "Test Organization"
            ),
            "currency": "USD",
        }


class FakeFinancialIntelligenceService:
    pass


def _build_engine(
    tmp_path: Path,
) -> AIQuestionEngine:

    return AIQuestionEngine(
        workspace_service=(
            FakeWorkspaceService(
                tmp_path
            )
        ),
        knowledge_reader=(
            FakeKnowledgeReader()
        ),
        financial_intelligence_service=(
            FakeFinancialIntelligenceService()
        ),
        financial_model_service=(
            FinancialModelService()
        ),
    )


def _save_executive_decision(
    tmp_path: Path,
) -> None:

    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    FinancialModelService.save_json(
        financial_model_folder=(
            financial_model_folder
        ),
        filename=(
            "executive_decision_intelligence.json"
        ),
        data={
            "status": "available",
            "executive_signal": (
                "priority_attention"
            ),
            "highest_priority": "High",
            "priority_count": 1,
            "opportunity_count": 1,
            "priorities": [
                {
                    "rank": 1,
                    "priority": "High",
                    "category": (
                        "Financial Health"
                    ),
                    "title": (
                        "Weak financial health"
                    ),
                    "evidence": (
                        "Financial Health Score "
                        "is 54/100."
                    ),
                    "management_action": (
                        "Prepare a financial "
                        "recovery plan."
                    ),
                    "expected_impact": (
                        "Improve financial resilience."
                    ),
                    "source": (
                        "risk_assessment"
                    ),
                    "source_type": (
                        "current_risk"
                    ),
                }
            ],
            "opportunities": [
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": (
                        "Secured funding coverage"
                    ),
                    "evidence": (
                        "Validated secured funding "
                        "coverage exists."
                    ),
                    "recommended_action": (
                        "Protect validated funding "
                        "coverage."
                    ),
                    "source": (
                        "financial_opportunity"
                    ),
                }
            ],
            "controls": {
                "deterministic": True,
                "financial_recalculation_performed": (
                    False
                ),
                "validated_outputs_preserved": True,
                "missing_evidence_not_invented": True,
                "opportunities_do_not_cancel_risks": (
                    True
                ),
            },
        },
    )


def test_classifier_routes_management_focus_right_now():
    classifier = QuestionClassifier()

    result = classifier.classify(
        question=(
            "What should management "
            "focus on right now?"
        )
    )

    assert (
        result["domain"]
        == "executive_decision"
    )

    assert (
        result["intent"]
        == "executive_priority_summary"
    )

    assert (
        result["target"]
        == "executive_decision_intelligence"
    )


def test_existing_priority_actions_intent_is_preserved():
    classifier = QuestionClassifier()

    result = classifier.classify(
        question=(
            "What should management prioritize?"
        )
    )

    assert (
        result["intent"]
        == "priority_actions"
    )

    assert (
        result["domain"]
        == "recommendation"
    )


def test_ai_question_engine_uses_executive_decision_intelligence(
    tmp_path: Path,
):
    _save_executive_decision(
        tmp_path
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What should management "
            "focus on right now?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "executive_priority_summary"
    )

    assert (
        result["domain"]
        == "executive_decision"
    )

    assert (
        "Weak financial health"
        in result["answer"]
    )

    assert (
        "Financial Health Score is 54/100."
        in result["answer"]
    )

    assert (
        "Prepare a financial recovery plan."
        in result["answer"]
    )

    assert (
        "Improve financial resilience."
        in result["answer"]
    )

    assert (
        "Secured funding coverage"
        in result["answer"]
    )

    assert (
        result["financial_data_used"]
        is True
    )


def test_executive_question_does_not_require_cfo_recommendations(
    tmp_path: Path,
):
    _save_executive_decision(
        tmp_path
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What are our top "
            "management priorities?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "executive_priority_summary"
    )

    assert (
        "Weak financial health"
        in result["answer"]
    )


def test_missing_executive_decision_is_safe(
    tmp_path: Path,
):
    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What should management "
            "focus on right now?"
        ),
        organisation_id="ORG-001",
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["intent"]
        == "executive_priority_summary"
    )

    assert (
        "Executive Decision Intelligence "
        "is not available yet"
        in result["answer"]
    )