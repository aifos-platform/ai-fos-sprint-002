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


def test_historical_change_question_uses_persisted_history(
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
            "What changed since our "
            "last financial update?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "historical_change_summary"
    )

    assert (
        result["domain"]
        == "historical_change"
    )

    assert (
        "Test Organization"
        in result["answer"]
    )

    assert (
        "verified"
        in result["answer"].lower()
    )

    assert (
        result["financial_data_used"]
        is True
    )


def test_financial_position_change_uses_deterministic_metric_comparison(
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
            "Is our financial position "
            "improving or deteriorating?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "financial_position_change"
    )

    answer = result["answer"]

    assert (
        "Financial Health Score"
        in answer
    )

    assert (
        "Cash Runway"
        in answer
    )

    assert (
        "improved"
        in answer.lower()
    )


def test_new_risks_question_uses_risk_movement(
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
            "What new risks appeared "
            "since the previous update?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "new_risks_since_previous"
    )

    assert (
        "Operating deficit"
        in result["answer"]
    )

    assert (
        "High"
        in result["answer"]
    )


def test_resolved_risks_question_uses_risk_movement(
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
            "Which risks were resolved "
            "since the last update?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "resolved_risks_since_previous"
    )

    assert (
        "Low cash runway"
        in result["answer"]
    )

    assert (
        "no longer present"
        in result["answer"].lower()
    )


def test_risk_change_summary_uses_deterministic_history(
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
            "How have our financial "
            "risks changed?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "risk_change_summary"
    )

    answer = result["answer"].lower()

    assert "1 new risk" in answer

    assert "1 resolved risk" in answer


def test_historical_question_requires_two_snapshots(
    tmp_path: Path,
):
    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What changed since our "
            "last financial update?"
        ),
        organisation_id="ORG-001",
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["intent"]
        == "historical_change_summary"
    )

    assert (
        "at least two"
        in result["answer"].lower()
    )


def test_one_snapshot_is_insufficient_history(
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
            "What changed since our "
            "last financial update?"
        ),
        organisation_id="ORG-001",
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["intent"]
        == "historical_change_summary"
    )