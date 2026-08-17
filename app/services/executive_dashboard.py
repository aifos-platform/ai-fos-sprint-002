from datetime import datetime, timezone
from typing import Any


def build_executive_dashboard(organization) -> dict[str, Any]:
    """
    Build the AI-FOS Executive Dashboard.

    This layer consolidates the most decision-relevant
    financial intelligence for management and board use.
    """

    budget_dashboard = organization.budget_dashboard or {}

    return {
        "header": {
            "organization": organization.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "financial_health": organization.financial_health or {},
        "kpis": organization.kpi_dashboard or {},
        "financial_summary": organization.financial_analysis or {},
        "budget": budget_dashboard,
        "alerts": budget_dashboard.get(
            "alerts",
            [],
        ),
        "risks": organization.risk_assessment or [],
        "recommendations": organization.cfo_recommendations or [],
        "grant_diagnostics": organization.grant_diagnostics or {},
        "ai_summary": organization.ai_cfo_report or {},
    }