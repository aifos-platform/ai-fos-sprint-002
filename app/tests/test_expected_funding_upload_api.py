from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import app


client = TestClient(app)


def test_budget_upload_persists_expected_funding_outputs(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        Path(tmp_path)
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    upload_folder = (
        Path(tmp_path)
        / "uploads"
    )

    upload_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        "app.main.UPLOAD_FOLDER",
        upload_folder,
    )

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "create_workspace"
        ),
        lambda **kwargs: {
            "workspace_id": "test-workspace",
            "status": "ready",
            "paths": {
                "financial_model": str(
                    financial_model_folder
                ),
            },
        },
    )

    monkeypatch.setattr(
        (
            "app.main.workspace_service."
            "save_upload"
        ),
        lambda **kwargs: {
            "status": "saved",
        },
    )

    workbook = Workbook()

    budget_sheet = workbook.active
    budget_sheet.title = "Available Budget"

    budget_sheet.append(
        [
            "Budget Line Code",
            "Budget Line Code Name",
            "Budget Notes",
            "Total Original Budget (USD)",
        ]
    )

    budget_sheet.append(
        [
            "BL-001",
            "Personnel",
            "Secured budget",
            100000,
        ]
    )

    expected_sheet = workbook.create_sheet(
        "Expected Funding"
    )

    expected_sheet.append(
        [
            "Expected Funding Code",
            "Funding Name",
            "Donor Code",
            "Donor Name",
            "Stage",
            "Probability %",
            "Minimum Amount",
            "Most Likely Amount",
            "Maximum Amount",
            "Expected Decision Date",
            "Expected First Payment Date",
            "Original Currency",
            "Reporting Currency",
            "Program Code",
            "Project Code",
            "Budget Line Code",
            "Notes",
        ]
    )

    expected_sheet.append(
        [
            "EF-001",
            "Core Support Proposal",
            "OSF",
            "Open Society Foundations",
            "Proposal Submitted",
            75,
            400000,
            500000,
            600000,
            "2026-11-15",
            "2027-01-15",
            "USD",
            "USD",
            "CORE",
            "PRJ-001",
            "BL-001",
            "Management estimate",
        ]
    )

    workbook_bytes = BytesIO()

    workbook.save(
        workbook_bytes
    )

    workbook_bytes.seek(0)

    response = client.post(
        "/upload",
        files={
            "file": (
                "budget_with_expected_funding.xlsx",
                workbook_bytes.getvalue(),
                (
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
            ),
        },
        data={
            "organisation_id": "acss",
            "organisation_name": "ACSS",
            "base_currency": "USD",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_type"] == "budget"

    assert (
        data["expected_funding_line_count"]
        == 1
    )

    print(
        "EXPECTED FUNDING FILE:",
        data.get("expected_funding_file"),
    )

    assert (
        data["expected_funding_file"]
        is not None
    )

    assert (
        data[
            "expected_funding_intelligence_file"
        ]
        is not None
    )

    assert (
        financial_model_folder
        / "expected_funding.json"
    ).exists()

    assert (
        financial_model_folder
        / "expected_funding_intelligence.json"
    ).exists()