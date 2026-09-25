from __future__ import annotations

from pathlib import Path
from typing import Any


class OrganizationReadinessService:
    """
    Determine organization data readiness from
    persisted AI-FOS workspace evidence.

    This service does not calculate financial results.
    It only reports which validated/persisted artifacts
    currently exist for an organization.
    """

    def assess(
        self,
        workspace: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if workspace is None:
            return {
                "status": "not_registered",
                "registered": False,
                "has_uploaded_data": False,
                "has_chart_of_accounts": False,
                "has_general_ledger": False,
                "has_budget": False,
                "has_gl_validation": False,
                "has_financial_model": False,
                "has_financial_health": False,
                "has_executive_dashboard": False,
                "has_financial_intelligence": False,
                "has_cfo_report_data": False,
                "has_cfo_report_pdf": False,
            }

        paths = workspace.get(
            "paths",
            {},
        )

        financial_model_path = Path(
            paths.get(
                "financial_model",
                "",
            )
        )

        upload_count = int(
            workspace.get(
                "upload_count",
                0,
            )
            or 0
        )

        has_chart_of_accounts = (
            financial_model_path
            / "dim_account.json"
        ).exists()

        has_general_ledger = (
            financial_model_path
            / "fact_gl.json"
        ).exists()

        has_budget = (
            financial_model_path
            / "budget.json"
        ).exists()

        has_gl_validation = (
            financial_model_path
            / "gl_integrity.json"
        ).exists()

        has_financial_model = (
            financial_model_path
            / "financial_facts.json"
        ).exists()

        has_financial_health = (
            financial_model_path
            / "financial_health.json"
        ).exists()

        has_executive_dashboard = (
            financial_model_path
            / "executive_dashboard.json"
        ).exists()

        has_financial_intelligence = (
            financial_model_path
            / "intelligence_hub.json"
        ).exists()

        has_cfo_report_data = (
            financial_model_path
            / "cfo_report.json"
        ).exists()

        has_cfo_report_pdf = (
            financial_model_path
            / "cfo_report.pdf"
        ).exists()

        if has_cfo_report_pdf:
            status = "report_ready"

        elif has_financial_intelligence:
            status = "intelligence_ready"

        elif has_financial_model:
            status = "financial_model_ready"

        elif has_general_ledger:
            status = "financial_data_available"

        elif upload_count > 0:
            status = "data_uploaded"

        else:
            status = "registered"

        return {
            "status": status,
            "registered": True,
            "has_uploaded_data": (
                upload_count > 0
            ),
            "has_chart_of_accounts": (
                has_chart_of_accounts
            ),
            "has_general_ledger": (
                has_general_ledger
            ),
            "has_budget": has_budget,
            "has_gl_validation": (
                has_gl_validation
            ),
            "has_financial_model": (
                has_financial_model
            ),
            "has_financial_health": (
                has_financial_health
            ),
            "has_executive_dashboard": (
                has_executive_dashboard
            ),
            "has_financial_intelligence": (
                has_financial_intelligence
            ),
            "has_cfo_report_data": (
                has_cfo_report_data
            ),
            "has_cfo_report_pdf": (
                has_cfo_report_pdf
            ),
        }