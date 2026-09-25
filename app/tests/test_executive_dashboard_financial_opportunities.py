from app.organization import Organization
from app.services.executive_dashboard import (
    build_executive_dashboard,
)


def _build_organization(
    financial_opportunities,
):
    organization = Organization()

    organization.financial_health = {}
    organization.kpi_dashboard = {}
    organization.financial_analysis = {}
    organization.budget_dashboard = {}
    organization.funding_gap = {}
    organization.risk_assessment = []
    organization.forward_risks = []
    organization.financial_opportunities = (
        financial_opportunities
    )
    organization.cfo_recommendations = []
    organization.grant_diagnostics = {}
    organization.ai_cfo_report = {}

    return organization


def test_executive_dashboard_exposes_financial_opportunities():
    financial_opportunities = [
        {
            "priority": "High",
            "category": "Funding",
            "title": (
                "Secured funding coverage opportunity"
            ),
            "evidence": (
                "Validated Funding Gap analysis shows "
                "secured funding coverage."
            ),
            "recommended_action": (
                "Protect secured funding coverage."
            ),
        },
        {
            "priority": "Medium",
            "category": "Liquidity",
            "title": "Strong liquidity capacity",
            "evidence": (
                "Validated liquidity analysis shows "
                "strong cash runway."
            ),
            "recommended_action": (
                "Use liquidity capacity strategically."
            ),
        },
    ]

    organization = _build_organization(
        financial_opportunities
    )

    dashboard = build_executive_dashboard(
        organization
    )

    assert "financial_opportunities" in dashboard
    assert (
        dashboard["financial_opportunities"]
        == financial_opportunities
    )


def test_executive_dashboard_keeps_opportunities_separate_from_risks():
    financial_opportunities = [
        {
            "priority": "High",
            "category": "Funding",
            "title": (
                "Secured funding coverage opportunity"
            ),
            "evidence": (
                "Validated opportunity evidence."
            ),
            "recommended_action": (
                "Protect the opportunity."
            ),
        }
    ]

    organization = _build_organization(
        financial_opportunities
    )

    dashboard = build_executive_dashboard(
        organization
    )

    assert dashboard["risks"] == []
    assert dashboard["forward_risks"] == []
    assert (
        dashboard["financial_opportunities"]
        == financial_opportunities
    )