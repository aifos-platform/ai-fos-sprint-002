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


def _standard_balance_sheet() -> dict:
    return {
        "status": "available",
        "report_type": "standard_balance_sheet",
        "totals": {
            "assets": 1500.0,
            "liabilities": 500.0,
            "equity": 1000.0,
        },
        "sections": [],
        "reconciliation": {
            "reconciled": True,
        },
        "controls": {
            "reporting_layer_only": True,
            "financial_recalculation_performed": False,
        },
    }


def test_standard_balance_sheet_api_returns_persisted_report(
    monkeypatch,
    tmp_path: Path,
):
    report = _standard_balance_sheet()

    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    FinancialModelService.save_json(
        tmp_path,
        "standard_balance_sheet.json",
        report,
    )

    response = client.get(
        "/reports/test-org/balance-sheet"
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


def test_standard_balance_sheet_api_missing_workspace_returns_404(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: None,
    )

    response = client.get(
        "/reports/missing-org/balance-sheet"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "No workspace found for this organization."
    )


def test_standard_balance_sheet_api_missing_report_returns_404(
    monkeypatch,
    tmp_path: Path,
):
    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    response = client.get(
        "/reports/test-org/balance-sheet"
    )

    assert response.status_code == 404

    assert (
        "Standard Balance Sheet is not available yet"
        in response.json()["detail"]
    )


def test_standard_balance_sheet_api_does_not_recalculate_financials(
    monkeypatch,
    tmp_path: Path,
):
    report = _standard_balance_sheet()

    workspace = _workspace(tmp_path)

    monkeypatch.setattr(
        "app.main.workspace_service.get_workspace_by_organisation",
        lambda organisation_id: workspace,
    )

    FinancialModelService.save_json(
        tmp_path,
        "standard_balance_sheet.json",
        report,
    )

    def forbidden_recalculation(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "Balance Sheet API must not "
            "recalculate financials."
        )

    monkeypatch.setattr(
        Organization,
        "process_financials",
        forbidden_recalculation,
    )

    response = client.get(
        "/reports/test-org/balance-sheet"
    )

    assert response.status_code == 200
    assert response.json()["report"] == report