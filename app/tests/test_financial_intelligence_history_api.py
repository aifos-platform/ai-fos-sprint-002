from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.financial_intelligence_history import (
    FinancialIntelligenceHistoryService,
)
from app.services.financial_model_service import (
    FinancialModelService,
)


client = TestClient(app)


def _patch_workspace(
    monkeypatch,
    financial_model_folder: Path,
    ai_knowledge_folder: Path,
) -> None:
    monkeypatch.setattr(
        "app.main.workspace_service."
        "get_workspace_by_organisation",
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                ),
                "ai_knowledge": str(
                    ai_knowledge_folder
                ),
            }
        },
    )


def _save_two_snapshots(
    financial_model_folder: Path,
) -> None:
    snapshots = [
        {
            "snapshot_id": "SNAPSHOT-A",
            "captured_at": (
                "2026-08-31T12:00:00"
            ),
            "analysis_start_date": None,
            "analysis_end_date": None,
            "source": "test",
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
                            "Low cash runway"
                        ),
                        "severity": "High",
                        "category": "Liquidity",
                        "evidence": (
                            "Runway requires attention."
                        ),
                    }
                ],
            },
        },
        {
            "snapshot_id": "SNAPSHOT-B",
            "captured_at": (
                "2026-09-30T12:00:00"
            ),
            "analysis_start_date": None,
            "analysis_end_date": None,
            "source": "test",
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
                            "Operating deficit"
                        ),
                        "severity": "High",
                        "category": (
                            "Operating Performance"
                        ),
                        "evidence": (
                            "Expenses exceed revenue."
                        ),
                    }
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


def test_financial_intelligence_history_api_returns_management_payload(
    monkeypatch,
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _save_two_snapshots(
        financial_model_folder
    )

    _patch_workspace(
        monkeypatch,
        financial_model_folder,
        ai_knowledge_folder,
    )

    response = client.get(
        "/organisations/org-1/"
        "financial-intelligence-history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"

    assert (
        data["organisation_id"]
        == "org-1"
    )

    assert (
        data["snapshot_count"]
        == 2
    )

    assert len(
        data["snapshots"]
    ) == 2

    assert (
        data["latest_change"]["status"]
        == "available"
    )

    assert (
        data["historical_decision"]["status"]
        == "available"
    )

    assert (
        data["historical_decision"][
            "priority_count"
        ]
        > 0
    )


def test_financial_intelligence_history_api_returns_metadata_only_snapshots(
    monkeypatch,
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _save_two_snapshots(
        financial_model_folder
    )

    _patch_workspace(
        monkeypatch,
        financial_model_folder,
        ai_knowledge_folder,
    )

    response = client.get(
        "/organisations/org-1/"
        "financial-intelligence-history"
    )

    assert response.status_code == 200

    data = response.json()

    snapshot = data["snapshots"][0]

    assert (
        snapshot["snapshot_id"]
        == "SNAPSHOT-A"
    )

    assert (
        snapshot["captured_at"]
        == "2026-08-31T12:00:00"
    )

    assert (
        snapshot["source"]
        == "test"
    )

    assert (
        "financial_intelligence"
        not in snapshot
    )


def test_financial_intelligence_history_api_handles_insufficient_history(
    monkeypatch,
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
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
                "snapshot_id": "SNAPSHOT-ONLY",
                "captured_at": (
                    "2026-09-30T12:00:00"
                ),
                "analysis_start_date": None,
                "analysis_end_date": None,
                "source": "test",
                "financial_intelligence": {
                    "financial_health": {
                        "score": 50.0,
                    },
                },
            }
        ],
    )

    _patch_workspace(
        monkeypatch,
        financial_model_folder,
        ai_knowledge_folder,
    )

    response = client.get(
        "/organisations/org-1/"
        "financial-intelligence-history"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "insufficient_history"
    )

    assert (
        data["snapshot_count"]
        == 1
    )

    assert (
        data["latest_change"]["status"]
        == "insufficient_history"
    )

    assert (
        data["historical_decision"]["status"]
        == "not_available"
    )


def test_financial_intelligence_history_api_is_read_only(
    monkeypatch,
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _save_two_snapshots(
        financial_model_folder
    )

    _patch_workspace(
        monkeypatch,
        financial_model_folder,
        ai_knowledge_folder,
    )

    before = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    response = client.get(
        "/organisations/org-1/"
        "financial-intelligence-history"
    )

    after = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert before == after

    assert (
        data["controls"]["read_only"]
        is True
    )

    assert (
        data["controls"][
            "financial_recalculation_performed"
        ]
        is False
    )

    assert (
        data["controls"][
            "historical_snapshots_modified"
        ]
        is False
    )

    assert (
        data["controls"][
            "hypothetical_scenarios_excluded"
        ]
        is True
    )

    assert (
        data["controls"][
            "action_plan_modified"
        ]
        is False
    )


def test_financial_intelligence_history_api_returns_404_for_missing_workspace(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.main.workspace_service."
        "get_workspace_by_organisation",
        lambda organisation_id: None,
    )

    response = client.get(
        "/organisations/missing/"
        "financial-intelligence-history"
    )

    assert response.status_code == 404