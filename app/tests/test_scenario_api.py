from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.financial_model_service import (
    FinancialModelService,
)


client = TestClient(app)


def test_scenario_endpoint_returns_404_without_workspace(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: None,
    )

    response = client.post(
        "/scenario/acss",
        json={
            "scenario_name": "Revenue Down 10%",
            "revenue_change_percentage": -10.0,
        },
    )

    assert response.status_code == 404


def test_scenario_endpoint_runs_and_persists(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    FinancialModelService.save_json(
        financial_model_folder,
        "financial_forecast.json",
        {
            "status": "available",
            "forecast_horizon_months": 3,
            "forecast_series": [
                {
                    "period": "2026-09",
                    "revenue": 1000.0,
                    "expenses": 700.0,
                    "net_result": 300.0,
                },
                {
                    "period": "2026-10",
                    "revenue": 1000.0,
                    "expenses": 700.0,
                    "net_result": 300.0,
                },
                {
                    "period": "2026-11",
                    "revenue": 1000.0,
                    "expenses": 700.0,
                    "net_result": 300.0,
                },
            ],
            "forecast_totals": {
                "revenue": 3000.0,
                "expenses": 2100.0,
                "net_result": 900.0,
            },
        },
    )

    FinancialModelService.save_json(
        financial_model_folder,
        "liquidity.json",
        {
            "available_cash": 1200.0,
            "cash_runway_months": 6.0,
            "average_monthly_operating_expenses": 200.0,
        },
    )

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    response = client.post(
        "/scenario/acss",
        json={
            "scenario_name": "Revenue Down 10%",
            "revenue_change_percentage": -10.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"

    assert (
        data["financial_scenario"][
            "scenario_name"
        ]
        == "Revenue Down 10%"
    )

    assert (
        data["financial_scenario"][
            "scenario"
        ]["revenue"]
        == 2700.0
    )

    assert (
        data["scenario_decision_intelligence"][
            "decision_signal"
        ]
        == "negative"
    )

    assert (
        financial_model_folder
        / "financial_scenario.json"
    ).exists()

    assert (
        financial_model_folder
        / "scenario_decision_intelligence.json"
    ).exists()

    assert (
        financial_model_folder
        / "scenario_history.json"
    ).exists()

    history = FinancialModelService.load_json(
        financial_model_folder,
        "scenario_history.json",
    )

    assert isinstance(
        history,
        list,
    )

    assert len(history) == 1

    assert (
        history[0]["scenario_name"]
        == "Revenue Down 10%"
    )

    assert (
        history[0]["financial_scenario"][
            "scenario_name"
        ]
        == "Revenue Down 10%"
    )

    assert (
        history[0][
            "scenario_decision_intelligence"
        ]["decision_signal"]
        == "negative"
    )    


def test_scenario_endpoint_preserves_baseline_forecast(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    baseline_forecast = {
        "status": "available",
        "forecast_horizon_months": 1,
        "forecast_series": [
            {
                "period": "2026-09",
                "revenue": 1000.0,
                "expenses": 700.0,
                "net_result": 300.0,
            },
        ],
        "forecast_totals": {
            "revenue": 1000.0,
            "expenses": 700.0,
            "net_result": 300.0,
        },
    }

    FinancialModelService.save_json(
        financial_model_folder,
        "financial_forecast.json",
        baseline_forecast,
    )

    FinancialModelService.save_json(
        financial_model_folder,
        "liquidity.json",
        {
            "available_cash": 1200.0,
            "cash_runway_months": 6.0,
            "average_monthly_operating_expenses": 200.0,
        },
    )

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    response = client.post(
        "/scenario/acss",
        json={
            "scenario_name": "Expense Increase",
            "expense_change_percentage": 10.0,
        },
    )

    assert response.status_code == 200

    loaded_forecast = FinancialModelService.load_json(
        financial_model_folder,
        "financial_forecast.json",
    )

    assert loaded_forecast == baseline_forecast

def test_scenario_comparison_endpoint_returns_404_without_workspace(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: None,
    )

    response = client.post(
        "/scenario-comparison/acss",
        json={
            "scenario_a": {
                "status": "available",
                "scenario_name": "Scenario A",
                "severity": "high",
                "management_attention": "priority_review",
                "net_result_impact": {
                    "direction": "deteriorated",
                    "variance": -500.0,
                },
            },
            "scenario_b": {
                "status": "available",
                "scenario_name": "Scenario B",
                "severity": "medium",
                "management_attention": "review",
                "net_result_impact": {
                    "direction": "deteriorated",
                    "variance": -200.0,
                },
            },
        },
    )

    assert response.status_code == 404


def test_scenario_comparison_endpoint_runs_and_persists(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    response = client.post(
        "/scenario-comparison/acss",
        json={
            "scenario_a": {
                "status": "available",
                "scenario_name": "Scenario A",
                "severity": "high",
                "management_attention": "priority_review",
                "net_result_impact": {
                    "direction": "deteriorated",
                    "variance": -500.0,
                },
            },
            "scenario_b": {
                "status": "available",
                "scenario_name": "Scenario B",
                "severity": "medium",
                "management_attention": "review",
                "net_result_impact": {
                    "direction": "deteriorated",
                    "variance": -200.0,
                },
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"
    assert data["organization_id"] == "acss"

    assert (
        data["scenario_comparison_intelligence"][
            "comparison_signal"
        ]
        == "clear_preference"
    )

    assert (
        data["scenario_comparison_intelligence"][
            "preferred_scenario"
        ]
        == "Scenario B"
    )

    assert (
        financial_model_folder
        / "scenario_comparison_intelligence.json"
    ).exists()  

def test_scenario_history_endpoint_returns_404_without_workspace(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: None,
    )

    response = client.get(
        "/scenario-history/acss"
    )

    assert response.status_code == 404


def test_scenario_history_endpoint_lists_saved_scenarios(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    from app.services.scenario_history import (
        ScenarioHistoryService,
    )

    ScenarioHistoryService.save_scenario(
        financial_model_folder=financial_model_folder,
        financial_scenario={
            "status": "available",
            "scenario_name": "Scenario A",
            "scenario_type": "what_if",
        },
        scenario_decision_intelligence={
            "status": "available",
            "scenario_name": "Scenario A",
            "decision_signal": "negative",
        },
    )

    response = client.get(
        "/scenario-history/acss"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_id"] == "acss"
    assert len(data["scenarios"]) == 1

    assert (
        data["scenarios"][0]["scenario_name"]
        == "Scenario A"
    )


def test_scenario_history_endpoint_retrieves_saved_scenario(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    from app.services.scenario_history import (
        ScenarioHistoryService,
    )

    saved = ScenarioHistoryService.save_scenario(
        financial_model_folder=financial_model_folder,
        financial_scenario={
            "status": "available",
            "scenario_name": "Scenario B",
            "scenario_type": "what_if",
        },
        scenario_decision_intelligence={
            "status": "available",
            "scenario_name": "Scenario B",
            "decision_signal": "negative",
        },
    )

    response = client.get(
        (
            "/scenario-history/acss/"
            f"{saved['scenario_id']}"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["scenario"]["scenario_id"]
        == saved["scenario_id"]
    )

    assert (
        data["scenario"]["scenario_name"]
        == "Scenario B"
    )

def test_saved_scenario_comparison_returns_404_without_workspace(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: None,
    )

    response = client.post(
        "/scenario-comparison/acss/saved",
        json={
            "scenario_a_id": "scenario-a",
            "scenario_b_id": "scenario-b",
        },
    )

    assert response.status_code == 404


def test_saved_scenario_comparison_returns_404_for_missing_scenario(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    response = client.post(
        "/scenario-comparison/acss/saved",
        json={
            "scenario_a_id": "missing-a",
            "scenario_b_id": "missing-b",
        },
    )

    assert response.status_code == 404


def test_saved_scenario_comparison_runs_and_persists(
    tmp_path,
    monkeypatch,
):
    from app.services.scenario_history import (
        ScenarioHistoryService,
    )

    financial_model_folder = Path(tmp_path)

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "get_workspace_by_organisation"
        ),
        lambda organisation_id: {
            "paths": {
                "financial_model": str(
                    financial_model_folder
                )
            }
        },
    )

    scenario_a = ScenarioHistoryService.save_scenario(
        financial_model_folder=financial_model_folder,
        financial_scenario={
            "status": "available",
            "scenario_name": "Scenario A",
            "scenario_type": "what_if",
        },
        scenario_decision_intelligence={
            "status": "available",
            "scenario_name": "Scenario A",
            "severity": "high",
            "management_attention": "priority_review",
            "net_result_impact": {
                "direction": "deteriorated",
                "variance": -500.0,
            },
        },
    )

    scenario_b = ScenarioHistoryService.save_scenario(
        financial_model_folder=financial_model_folder,
        financial_scenario={
            "status": "available",
            "scenario_name": "Scenario B",
            "scenario_type": "what_if",
        },
        scenario_decision_intelligence={
            "status": "available",
            "scenario_name": "Scenario B",
            "severity": "medium",
            "management_attention": "review",
            "net_result_impact": {
                "direction": "deteriorated",
                "variance": -200.0,
            },
        },
    )

    response = client.post(
        "/scenario-comparison/acss/saved",
        json={
            "scenario_a_id": scenario_a["scenario_id"],
            "scenario_b_id": scenario_b["scenario_id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"
    assert data["organization_id"] == "acss"

    assert (
        data["scenario_comparison_intelligence"][
            "preferred_scenario"
        ]
        == "Scenario B"
    )

    assert (
        financial_model_folder
        / "scenario_comparison_intelligence.json"
    ).exists()
          