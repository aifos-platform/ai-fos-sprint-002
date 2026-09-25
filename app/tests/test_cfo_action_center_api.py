from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


client = TestClient(app)


def test_cfo_action_center_returns_consolidated_payload(
    monkeypatch,
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = CFOActionPlanService.create_action(
        financial_model_folder=(
            financial_model_folder
        ),
        title="Review funding gap",
        description=(
            "Review funding gap and funding coverage."
        ),
        priority="High",
        category="Funding",
    )

    CFOActionPlanService.update_action(
        financial_model_folder=(
            financial_model_folder
        ),
        action_id=action["action_id"],
        owner="Elie",
        status="in_progress",
    )

    CFOActionHistoryService.record_event(
        financial_model_folder=(
            financial_model_folder
        ),
        action_id=action["action_id"],
        event_type="status_changed",
        previous_value="in_progress",
        new_value="blocked",
    )

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

    response = client.get(
        "/organisations/org-1/cfo-action-center"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"
    assert data["organisation_id"] == "org-1"

    assert "summary" in data
    assert "actions" in data
    assert "monitoring" in data
    assert "escalation" in data
    assert "performance" in data

    assert len(data["actions"]) == 1

    assert (
        data["controls"]["read_only"]
        is True
    )

    assert (
        data["controls"][
            "action_records_modified"
        ]
        is False
    )

    assert (
        data["controls"][
            "history_records_modified"
        ]
        is False
    )


def test_cfo_action_center_handles_empty_action_plan(
    monkeypatch,
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

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

    response = client.get(
        "/organisations/org-1/cfo-action-center"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"
    assert data["actions"] == []

    assert (
        data["summary"]["total_actions"]
        == 0
    )


def test_cfo_action_center_returns_404_for_missing_workspace(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.main.workspace_service."
        "get_workspace_by_organisation",
        lambda organisation_id: None,
    )

    response = client.get(
        "/organisations/missing/cfo-action-center"
    )

    assert response.status_code == 404