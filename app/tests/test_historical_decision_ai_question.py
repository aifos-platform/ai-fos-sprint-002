from pathlib import Path

from app.services.ai_question_engine import (
    AIQuestionEngine,
)
from app.services.financial_intelligence_history import (
    FinancialIntelligenceHistoryService,
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


def _save_history(
    tmp_path: Path,
) -> None:

    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    snapshots = [
        {
            "snapshot_id": "SNAPSHOT-A",
            "captured_at": (
                "2026-08-31T12:00:00"
            ),
            "financial_intelligence": {
                "financial_health": {
                    "score": 50.0,
                },
                "liquidity": {
                    "cash_runway_months": 6.0,
                },
                "risk_assessment": [
                    {
                        "title": (
                            "Low cash runway"
                        ),
                        "severity": "High",
                        "category": "Liquidity",
                        "evidence": (
                            "Runway requires attention."
                        ),
                    },
                ],
            },
        },
        {
            "snapshot_id": "SNAPSHOT-B",
            "captured_at": (
                "2026-09-30T12:00:00"
            ),
            "financial_intelligence": {
                "financial_health": {
                    "score": 60.0,
                },
                "liquidity": {
                    "cash_runway_months": 8.0,
                },
                "risk_assessment": [
                    {
                        "title": (
                            "Operating deficit"
                        ),
                        "severity": "High",
                        "category": (
                            "Operating Performance"
                        ),
                        "evidence": (
                            "Expenses exceed revenue."
                        ),
                    },
                ],
            },
        },
    ]

    FinancialModelService.save_json(
        financial_model_folder=(
            financial_model_folder
        ),
        filename=(
            FinancialIntelligenceHistoryService.FILENAME
        ),
        data=snapshots,
    )


def test_historical_management_priority_question_uses_decision_intelligence(
    tmp_path: Path,
):
    _save_history(
        tmp_path
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What historical changes "
            "require management attention?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )

    assert (
        result["domain"]
        == "historical_decision"
    )

    assert (
        "Test Organization"
        in result["answer"]
    )

    assert (
        "Operating deficit"
        in result["answer"]
    )

    assert (
        "High"
        in result["answer"]
    )

    assert (
        result["financial_data_used"]
        is True
    )


def test_historical_decision_uses_change_driven_priority(
    tmp_path: Path,
):
    _save_history(
        tmp_path
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What deteriorations should "
            "management prioritize?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert (
        "operating deficit"
        in answer
    )

    assert (
        "new risk"
        in answer
    )

    assert (
        "priority attention"
        in answer
    )


def test_historical_decision_keeps_improvements_separate(
    tmp_path: Path,
):
    _save_history(
        tmp_path
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What historical changes "
            "require management attention?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    answer = result["answer"]

    assert (
        "Operating deficit"
        in answer
    )

    assert (
        "Positive historical developments "
        "remain separate"
        in answer
    )

    assert (
        "Financial Health Score improved"
        in answer
    )

    assert (
        "Cash Runway improved"
        in answer
    )


def test_historical_decision_does_not_hide_resolved_risk(
    tmp_path: Path,
):
    _save_history(
        tmp_path
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "Based on our latest financial changes, "
            "what should management focus on?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )

    assert (
        "Low cash runway"
        in result["answer"]
    )

    assert (
        "risk resolved"
        in result["answer"].lower()
    )


def test_historical_decision_requires_two_snapshots(
    tmp_path: Path,
):
    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What historical changes "
            "require management attention?"
        ),
        organisation_id="ORG-001",
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )

    assert (
        result["domain"]
        == "historical_decision"
    )

    assert (
        "at least two"
        in result["answer"].lower()
    )


def test_one_snapshot_is_insufficient_for_historical_decision(
    tmp_path: Path,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    FinancialModelService.save_json(
        financial_model_folder=(
            financial_model_folder
        ),
        filename=(
            FinancialIntelligenceHistoryService.FILENAME
        ),
        data=[
            {
                "snapshot_id": (
                    "ONLY-SNAPSHOT"
                ),
                "captured_at": (
                    "2026-09-30T12:00:00"
                ),
                "financial_intelligence": {
                    "financial_health": {
                        "score": 60.0,
                    },
                },
            }
        ],
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What historical financial changes "
            "need management attention?"
        ),
        organisation_id="ORG-001",
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )


def test_historical_decision_question_does_not_mutate_history(
    tmp_path: Path,
):
    _save_history(
        tmp_path
    )

    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    before = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What historical changes "
            "require management attention?"
        ),
        organisation_id="ORG-001",
    )

    after = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    assert result["status"] == "success"

    assert before == after