from datetime import datetime, timezone
from typing import Any

from app.services.cfo_insights import generate_funding_gap_insights


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

    core_cost_coverage = getattr(
        organization,
        "core_cost_coverage",
        None,
    ) or {}

    risk_assessment = organization.risk_assessment or []

    forward_risks = (
        getattr(
            organization,
            "forward_risks",
            None,
        )
        or []
    )

    financial_opportunities = (
        getattr(
            organization,
            "financial_opportunities",
            None,
        )
        or []
    )

    cfo_recommendations = organization.cfo_recommendations or []
    grant_diagnostics = organization.grant_diagnostics or {}
    ai_cfo_report = organization.ai_cfo_report or {}

    funding_gap_summary = funding_gap.get(
        "summary",
        {},
    )

    funding_gap_insights = generate_funding_gap_insights(
        funding_gap
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

        "funding_gap": {
            "summary": funding_gap_summary,

            "diagnostics": {
                "dimension_incompatible_funding_exposure": (
                    funding_gap_summary.get(
                        "dimension_incompatible_funding_exposure",
                        0.0,
                    )
                ),

                "period_ineligible_funding_exposure": (
                    funding_gap_summary.get(
                        "period_ineligible_funding_exposure",
                        0.0,
                    )
                ),

                "period_unknown_funding_exposure": (
                    funding_gap_summary.get(
                        "period_unknown_funding_exposure",
                        0.0,
                    )
                ),

                "requirements_with_dimension_incompatible_funding": (
                    funding_gap_summary.get(
                        "requirements_with_dimension_incompatible_funding",
                        0,
                    )
                ),

                "requirements_with_period_ineligible_funding": (
                    funding_gap_summary.get(
                        "requirements_with_period_ineligible_funding",
                        0,
                    )
                ),

                "requirements_with_period_unknown_funding": (
                    funding_gap_summary.get(
                        "requirements_with_period_unknown_funding",
                        0,
                    )
                ),
            },

            "diagnostic_exposure_note": funding_gap.get(
                "diagnostic_exposure_note"
            ),

            "grant_period_rule": funding_gap.get(
                "grant_period_rule"
            ),

            "allocation_control": funding_gap.get(
                "allocation_control"
            ),
        }, 

        "core_cost_coverage": core_cost_coverage,               

        # --------------------------------------------------
        # Funding intelligence
        # --------------------------------------------------

        "funding_gap_insights": funding_gap_insights,
       
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

            "period_ineligible_funding_exposure": funding_gap_summary.get(
                "period_ineligible_funding_exposure",
                0.0,
            ),

            "period_unknown_funding_exposure": funding_gap_summary.get(
                "period_unknown_funding_exposure",
                0.0,
            ),

            "dimension_incompatible_funding_exposure": funding_gap_summary.get(
                "dimension_incompatible_funding_exposure",
                0.0,
            ),

            "requirements_with_period_ineligible_funding": funding_gap_summary.get(
                "requirements_with_period_ineligible_funding",
                0,
            ),

            "requirements_with_period_unknown_funding": funding_gap_summary.get(
                "requirements_with_period_unknown_funding",
                0,
            ),

            "requirements_with_dimension_incompatible_funding": funding_gap_summary.get(
                "requirements_with_dimension_incompatible_funding",
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
            ),
        },

        # --------------------------------------------------
        # CFO intelligence
        # --------------------------------------------------

        "risks": risk_assessment,
        "forward_risks": forward_risks,
        "financial_opportunities": financial_opportunities,
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