from pathlib import Path

from app.services.organization_readiness import (
    OrganizationReadinessService,
)


def build_workspace(
    financial_model_folder: Path,
    upload_count: int = 0,
) -> dict:
    return {
        "workspace_id": "test-workspace",
        "organisation_id": "test-org",
        "organisation_name": "Test Organization",
        "upload_count": upload_count,
        "paths": {
            "financial_model": str(
                financial_model_folder
            ),
        },
    }


def touch(
    folder: Path,
    filename: str,
) -> None:
    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        folder
        / filename
    ).write_text(
        "{}",
        encoding="utf-8",
    )


def test_not_registered():
    service = OrganizationReadinessService()

    result = service.assess(None)

    assert result["status"] == "not_registered"
    assert result["registered"] is False
    assert result["has_uploaded_data"] is False
    assert result["has_financial_intelligence"] is False
    assert result["has_cfo_report_pdf"] is False


def test_registered_without_data(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    workspace = build_workspace(
        tmp_path,
    )

    result = service.assess(workspace)

    assert result["status"] == "registered"
    assert result["registered"] is True
    assert result["has_uploaded_data"] is False
    assert result["has_general_ledger"] is False


def test_uploaded_data(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    workspace = build_workspace(
        tmp_path,
        upload_count=1,
    )

    result = service.assess(workspace)

    assert result["status"] == "data_uploaded"
    assert result["has_uploaded_data"] is True


def test_general_ledger_available(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    touch(
        tmp_path,
        "fact_gl.json",
    )

    workspace = build_workspace(
        tmp_path,
        upload_count=1,
    )

    result = service.assess(workspace)

    assert (
        result["status"]
        == "financial_data_available"
    )
    assert result["has_general_ledger"] is True


def test_financial_model_ready(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    touch(
        tmp_path,
        "financial_facts.json",
    )

    workspace = build_workspace(
        tmp_path,
        upload_count=1,
    )

    result = service.assess(workspace)

    assert (
        result["status"]
        == "financial_model_ready"
    )
    assert result["has_financial_model"] is True


def test_intelligence_ready(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    touch(
        tmp_path,
        "intelligence_hub.json",
    )

    workspace = build_workspace(
        tmp_path,
        upload_count=1,
    )

    result = service.assess(workspace)

    assert (
        result["status"]
        == "intelligence_ready"
    )
    assert (
        result["has_financial_intelligence"]
        is True
    )


def test_report_ready(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    touch(
        tmp_path,
        "cfo_report.pdf",
    )

    workspace = build_workspace(
        tmp_path,
        upload_count=1,
    )

    result = service.assess(workspace)

    assert result["status"] == "report_ready"
    assert result["has_cfo_report_pdf"] is True


def test_individual_artifact_flags(
    tmp_path: Path,
):
    service = OrganizationReadinessService()

    filenames = [
        "dim_account.json",
        "fact_gl.json",
        "budget.json",
        "gl_integrity.json",
        "financial_facts.json",
        "financial_health.json",
        "executive_dashboard.json",
        "intelligence_hub.json",
        "cfo_report.json",
        "cfo_report.pdf",
    ]

    for filename in filenames:
        touch(
            tmp_path,
            filename,
        )

    workspace = build_workspace(
        tmp_path,
        upload_count=3,
    )

    result = service.assess(workspace)

    assert result["status"] == "report_ready"
    assert result["has_uploaded_data"] is True
    assert result["has_chart_of_accounts"] is True
    assert result["has_general_ledger"] is True
    assert result["has_budget"] is True
    assert result["has_gl_validation"] is True
    assert result["has_financial_model"] is True
    assert result["has_financial_health"] is True
    assert result["has_executive_dashboard"] is True
    assert (
        result["has_financial_intelligence"]
        is True
    )
    assert result["has_cfo_report_data"] is True
    assert result["has_cfo_report_pdf"] is True