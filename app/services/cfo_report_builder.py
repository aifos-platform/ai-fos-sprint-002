from typing import Any


def build_cfo_report(
    *,
    financial_health: dict[str, Any] | None = None,
    liquidity: dict[str, Any] | None = None,
    budget_dashboard: dict[str, Any] | None = None,
    funding_gap: dict[str, Any] | None = None,
    grant_diagnostics: dict[str, Any] | None = None,
    risk_assessment: list[dict[str, Any]] | None = None,
    forward_risks: list[dict[str, Any]] | None = None,
    financial_opportunities: list[dict[str, Any]] | None = None,
    cfo_recommendations: list[dict[str, Any]] | None = None,
    financial_trends: dict[str, Any] | None = None,
    financial_forecast: dict[str, Any] | None = None,
    core_cost_coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the structured AI-FOS CFO Report.

    The report consumes validated AI-FOS financial intelligence
    artifacts. It does not recalculate financial results.

    The resulting structure is intended to become the common
    source for future PDF, Word, Excel, and PowerPoint reports.
    """

    financial_health = financial_health or {}
    liquidity = liquidity or {}
    budget_dashboard = budget_dashboard or {}
    funding_gap = funding_gap or {}
    grant_diagnostics = grant_diagnostics or {}
    risk_assessment = risk_assessment or []
    forward_risks = forward_risks or []
    financial_opportunities = financial_opportunities or []
    cfo_recommendations = cfo_recommendations or []
    financial_trends = financial_trends or {}
    financial_forecast = financial_forecast or {}
    core_cost_coverage = core_cost_coverage or {}

    high_current_risks = [
        risk
        for risk in risk_assessment
        if isinstance(risk, dict)
        and str(risk.get("severity", "")).lower()
        in {"critical", "high"}
    ]

    high_forward_risks = [
        risk
        for risk in forward_risks
        if isinstance(risk, dict)
        and str(risk.get("severity", "")).lower()
        in {"critical", "high"}
    ]

    high_opportunities = [
        opportunity
        for opportunity in financial_opportunities
        if isinstance(opportunity, dict)
        and str(opportunity.get("priority", "")).lower()
        == "high"
    ]

    priority_recommendations = [
        recommendation
        for recommendation in cfo_recommendations
        if isinstance(recommendation, dict)
        and str(recommendation.get("priority", "")).lower()
        in {"critical", "high"}
    ]

    return {
        "report_type": "cfo_report",
        "version": "1.0",
        "methodology": {
            "calculation_policy": (
                "The CFO Report consumes validated AI-FOS "
                "financial intelligence outputs and does not "
                "recalculate financial results."
            ),
            "evidence_policy": (
                "Report sections remain traceable to validated "
                "AI-FOS financial model artifacts."
            ),
        },
        "executive_summary": {
            "financial_health": financial_health,
            "liquidity": liquidity,
            "high_current_risk_count": len(high_current_risks),
            "high_forward_risk_count": len(high_forward_risks),
            "high_opportunity_count": len(high_opportunities),
            "priority_action_count": len(priority_recommendations),
        },
        "financial_health": financial_health,
        "liquidity": liquidity,
        "budget": budget_dashboard,
        "funding": {
            "funding_gap": funding_gap,
            "grant_diagnostics": grant_diagnostics,
        },
        "core_cost_coverage": core_cost_coverage,
        "risks": {
            "current": risk_assessment,
            "high_current": high_current_risks,
            "forward": forward_risks,
            "high_forward": high_forward_risks,
        },
        "opportunities": {
            "all": financial_opportunities,
            "high_priority": high_opportunities,
        },
        "recommendations": {
            "all": cfo_recommendations,
            "priority_actions": priority_recommendations,
        },
        "trends": financial_trends,
        "forecast": financial_forecast,
    }