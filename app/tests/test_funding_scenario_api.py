from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.financial_model_service import (
    FinancialModelService,
)


client = TestClient(app)


def _expected_funding_intelligence():
    return {
        "status": "available",
        "summary": {
            "record_count": 2,
            "record_count_requiring_review": 0,
            "minimum_pipeline_value": 300000.0,
            "most_likely_pipeline_value": 500000.0,
            "maximum_pipeline_value": 700000.0,
            "probability_weighted_expected_funding": 350000.0,
            "weighted_record_count": 2,
        },
        "records": [
            {
                "expected_funding_code": "EF-001",
                "funding_name": "Ford Proposal",
                "minimum_amount": 100000.0,
                "most_likely_amount": 200000.0,
                "maximum_amount": 300000.0,
                "probability_weighted_amount": 100000.0,
            },
            {
                "expected_funding_code": "EF-002",
                "funding_name": "OSF Proposal",
                "minimum_amount": 200000.0,
                "most_likely_amount": 300000.0,
                "maximum_amount": 400000.0,
                "probability_weighted_amount": 250000.0,
            },
        ],
        "controls": {
            "prospective_funding_only": True,
            "treated_as_secured_funding": False,
            "expected_funding_not_assumed_revenue": True,
            "expected_funding_not_assumed_cash": True,
        },
    }


def test_funding_scenario_endpoint_returns_404_without_workspace(
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
        "/funding-scenario/acss",
        json={
            "scenario_name": "Expected Funding Down 20%",
            "expected_funding_change_percentage": -20.0,
        },
    )

    assert response.status_code == 404


def test_funding_scenario_endpoint_runs_and_persists(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    FinancialModelService.save_json(
        financial_model_folder,
        "expected_funding_intelligence.json",
        _expected_funding_intelligence(),
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
        "/funding-scenario/acss",
        json={
            "scenario_name": "Expected Funding Down 20%",
            "expected_funding_change_percentage": -20.0,
            "scenario_basis": "most_likely",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "available"

    assert (
        data["funding_scenario"][
            "scenario_name"
        ]
        == "Expected Funding Down 20%"
    )

    assert (
        data["funding_scenario"][
            "scenario"
        ][
            "most_likely_pipeline_value"
        ]
        == 400000.0
    )

    assert (
        financial_model_folder
        / "funding_scenario.json"
    ).exists()


def test_funding_scenario_endpoint_failed_grant(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = Path(tmp_path)

    FinancialModelService.save_json(
        financial_model_folder,
        "expected_funding_intelligence.json",
        _expected_funding_intelligence(),
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
        "/funding-scenario/acss",
        json={
            "scenario_name": "Ford Proposal Fails",
            "failed_expected_funding_codes": [
                "EF-001",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["funding_scenario"][
            "scenario"
        ][
            "most_likely_pipeline_value"
        ]
        == 300000.0
    )

    assert (
        data["funding_scenario"][
            "controls"
        ][
            "treated_as_secured_funding"
        ]
        is False
    )