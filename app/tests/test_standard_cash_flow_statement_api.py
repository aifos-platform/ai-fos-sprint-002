from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.financial_model_service import (
    FinancialModelService,
)
from app.organization import Organization


client = TestClient(app)


def _workspace(
    financial_model_folder: Path,
) -> dict:
    return {
        "paths": {
            "financial_model": str(
                financial_model_folder
            ),
        },
    }


def _standard_cash_flow_statement() -> dict:
    return {
        "status": "available",
        "report_type": "standard_cash_flow_statement",
        "sections": {
            "operating_activities": {
                "amount": 100000.0,
            },
            "investing_activities": {
                "amount": -30000.0,
            },
            "financing_activities": {
                "amount": 15000.0,
            },
        },
        "net_change_in_cash": 85000.0,
        "reconciliation": {
            "reconciled": True,
        },
        "controls": {
            "reporting_layer_only": True,
            "financial_recalculation_performed": False,
        },
    }


def test_standard_cash_flow_statement_api_returns_persisted_report(
    monkeypatch,
    tmp_path: Path,
):
    report = _standard_cash_flow_statement()

    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    FinancialModelService.save_json(
        tmp_path,
        "standard_cash_flow_statement.json",
        report,
    )

    response = client.get(
        "/reports/test-org/cash-flow"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "available"
    assert payload["organisation_id"] == "test-org"
    assert payload["report"] == report

    controls = payload["controls"]

    assert controls["read_only"] is True

    assert (
        controls["financial_recalculation_performed"]
        is False
    )

    assert (
        controls["validated_financial_output_preserved"]
        is True
    )

    assert (
        controls["persisted_reporting_output_used"]
        is True
    )


def test_standard_cash_flow_statement_api_missing_workspace_returns_404(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: None,
    )

    response = client.get(
        "/reports/missing-org/cash-flow"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "No workspace found for this organization."
    )


def test_standard_cash_flow_statement_api_missing_report_returns_404(
    monkeypatch,
    tmp_path: Path,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    response = client.get(
        "/reports/test-org/cash-flow"
    )

    assert response.status_code == 404

    assert (
        "Standard Cash Flow Statement is not available yet"
        in response.json()["detail"]
    )


def test_standard_cash_flow_statement_api_does_not_recalculate_financials(
    monkeypatch,
    tmp_path: Path,
):
    report = _standard_cash_flow_statement()

    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    FinancialModelService.save_json(
        tmp_path,
        "standard_cash_flow_statement.json",
        report,
    )

    def forbidden_recalculation(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "Cash Flow API must not "
            "recalculate financials."
        )

    monkeypatch.setattr(
        Organization,
        "process_financials",
        forbidden_recalculation,
    )

    response = client.get(
        "/reports/test-org/cash-flow"
    )

    assert response.status_code == 200
    assert response.json()["report"] == report