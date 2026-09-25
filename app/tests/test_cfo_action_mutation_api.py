from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.cfo_action_history import CFOActionHistoryService
from app.services.cfo_action_plan import CFOActionPlanService
from app.services.financial_model_service import FinancialModelService


client = TestClient(app)


def _workspace(tmp_path: Path) -> dict:
    financial_model_folder = tmp_path / "financial_model"
    financial_model_folder.mkdir(parents=True, exist_ok=True)

    return {
        "workspace_id": "test-workspace",
        "organisation_id": "test-org",
        "paths": {
            "financial_model": str(financial_model_folder),
        },
    }


def _create_action(
    financial_model_folder: Path,
) -> dict:
    return CFOActionPlanService.create_action(
        financial_model_folder=financial_model_folder,
        title="Review funding gap",
        description="Review the organization's funding gap.",
        priority="High",
        source_type="executive_decision_intelligence",
        source_title="Review funding gap",
        source_priority="High",
    )


def test_command_endpoint_assigns_owner_and_writes_history(
    tmp_path,
    monkeypatch,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    action = _create_action(financial_model_folder)

    history_before = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    response = client.post(
        (
            f"/organisations/test-org/cfo-actions/"
            f"{action['action_id']}/command"
        ),
        json={
            "command": "assign",
            "value": "Wassim",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert body["action"]["owner"] == "Wassim"

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=financial_model_folder,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["owner"] == "Wassim"

    history_after = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    assert len(history_after) == len(history_before) + 1

    new_event = history_after[-1]

    assert new_event["action_id"] == action["action_id"]
    assert new_event["field"] == "owner"
    assert new_event["new_value"] == "Wassim"
    assert new_event["actor"] is None
    assert new_event["source"] == "user_interface"


def test_invalid_command_produces_no_mutation_or_history(
    tmp_path,
    monkeypatch,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    action = _create_action(financial_model_folder)

    before = CFOActionPlanService.get_action(
        financial_model_folder=financial_model_folder,
        action_id=action["action_id"],
    )

    history_before = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    response = client.post(
        (
            f"/organisations/test-org/cfo-actions/"
            f"{action['action_id']}/command"
        ),
        json={
            "command": "not_a_real_command",
            "value": "anything",
        },
    )

    assert response.status_code == 400

    after = CFOActionPlanService.get_action(
        financial_model_folder=financial_model_folder,
        action_id=action["action_id"],
    )

    history_after = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    assert after == before
    assert history_after == history_before


def test_unknown_action_produces_no_mutation_or_history(
    tmp_path,
    monkeypatch,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    history_before = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    response = client.post(
        "/organisations/test-org/cfo-actions/missing-action/command",
        json={
            "command": "start",
        },
    )

    assert response.status_code == 400

    assert CFOActionPlanService.list_actions(
        financial_model_folder
    ) == []

    history_after = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    assert history_after == history_before


def test_invalid_assignment_produces_no_mutation_or_history(
    tmp_path,
    monkeypatch,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    action = _create_action(financial_model_folder)

    before = CFOActionPlanService.get_action(
        financial_model_folder=financial_model_folder,
        action_id=action["action_id"],
    )

    history_before = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    response = client.post(
        (
            f"/organisations/test-org/cfo-actions/"
            f"{action['action_id']}/command"
        ),
        json={
            "command": "assign",
            "value": "",
        },
    )

    assert response.status_code == 400

    after = CFOActionPlanService.get_action(
        financial_model_folder=financial_model_folder,
        action_id=action["action_id"],
    )

    history_after = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    assert after == before
    assert history_after == history_before


def test_create_action_from_persisted_executive_priority(
    tmp_path,
    monkeypatch,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    executive_decision_intelligence = {
        "status": "available",
        "priorities": [
            {
                "title": "Protect liquidity runway",
                "management_action": (
                    "Management should protect available liquidity."
                ),
                "priority": "Critical",
                "source_type": "current_risk",
            }
        ],
    }

    FinancialModelService.save_json(
        financial_model_folder=financial_model_folder,
        filename="executive_decision_intelligence.json",
        data=executive_decision_intelligence,
    )

    response = client.post(
        (
            "/organisations/test-org/cfo-actions/"
            "from-executive-priority"
        ),
        json={
            "priority_index": 0,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "created"

    action = body["action"]

    assert action["title"] == "Protect liquidity runway"
    assert action["owner"] is None
    assert action["due_date"] is None
    assert action["status"] == "open"
    assert action["progress_percentage"] == 0

    persisted_actions = CFOActionPlanService.list_actions(
        financial_model_folder
    )

    assert len(persisted_actions) == 1
    assert persisted_actions[0]["action_id"] == action["action_id"]
    assert persisted_actions[0]["owner"] is None
    assert persisted_actions[0]["due_date"] is None


def test_create_from_invalid_priority_index_creates_nothing(
    tmp_path,
    monkeypatch,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    FinancialModelService.save_json(
        financial_model_folder=financial_model_folder,
        filename="executive_decision_intelligence.json",
        data={
            "status": "available",
            "priorities": [],
        },
    )

    history_before = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    response = client.post(
        (
            "/organisations/test-org/cfo-actions/"
            "from-executive-priority"
        ),
        json={
            "priority_index": 0,
        },
    )

    assert response.status_code == 400

    assert CFOActionPlanService.list_actions(
        financial_model_folder
    ) == []

    history_after = CFOActionHistoryService.list_events(
        financial_model_folder
    )

    assert history_after == history_before
    