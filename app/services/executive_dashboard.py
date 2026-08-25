from datetime import datetime, timezone
from typing import Any


def build_executive_dashboard(organization) -> dict[str, Any]:
    """
    Build the AI-FOS Executive Dashboard.

    This layer consolidates the most decision-relevant
    financial intelligence for management and board use.

    The dashboard does not recalculate financial intelligence.
    It exposes validated outputs produced by the underlying
    AI-FOS financial engines.
    """

    financial_health = organization.financial_health or {}
    kpi_dashboard = organization.kpi_dashboard or {}
    financial_analysis = organization.financial_analysis or {}
    budget_dashboard = organization.budget_dashboard or {}
    funding_gap = getattr(
        organization,
        "funding_gap",
        None,
    ) or {}
    risk_assessment = organization.risk_assessment or []
    cfo_recommendations = organization.cfo_recommendations or []
    grant_diagnostics = organization.grant_diagnostics or {}
    ai_cfo_report = organization.ai_cfo_report or {}

    funding_gap_summary = funding_gap.get(
        "summary",
        {},
    )

    return {
        "header": {
            "organization": organization.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },

        # --------------------------------------------------
        # Core financial position
        # --------------------------------------------------

        "financial_health": financial_health,
        "kpis": kpi_dashboard,
        "financial_summary": financial_analysis,

        # --------------------------------------------------
        # Budget intelligence
        # --------------------------------------------------

        "budget": budget_dashboard,
        "alerts": budget_dashboard.get(
            "alerts",
            [],
        ),

        # --------------------------------------------------
        # Funding intelligence
        # --------------------------------------------------

        "funding_gap": funding_gap,
        "funding_summary": {
            "remaining_requirement": funding_gap_summary.get(
                "remaining_requirement",
                0,
            ),
            "applied_secured_funding": funding_gap_summary.get(
                "applied_secured_funding",
                0,
            ),
            "funding_gap": funding_gap_summary.get(
                "funding_gap",
                0,
            ),
            "applied_coverage_percentage": funding_gap_summary.get(
                "applied_coverage_percentage",
                0,
            ),
            "matched_requirement_count": funding_gap_summary.get(
                "matched_requirement_count",
                0,
            ),
            "unmatched_requirement_count": funding_gap_summary.get(
                "unmatched_requirement_count",
                0,
            ),
            "status": funding_gap_summary.get(
                "status",
                "Unknown",
            ),
        },

        # --------------------------------------------------
        # CFO intelligence
        # --------------------------------------------------

        "risks": risk_assessment,
        "recommendations": cfo_recommendations,

        # --------------------------------------------------
        # Grant intelligence
        # --------------------------------------------------

        "grant_diagnostics": grant_diagnostics,

        # --------------------------------------------------
        # AI CFO narrative
        # --------------------------------------------------

        "ai_summary": ai_cfo_report,
    }