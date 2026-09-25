from types import SimpleNamespace

from app.services.executive_dashboard import (
    build_executive_dashboard,
)


def test_executive_dashboard_exposes_forward_risks_separately():
    organization = SimpleNamespace(
        financial_health={},
        kpi_dashboard={},
        financial_analysis={},
        budget_dashboard={},
        funding_gap={},
        risk_assessment=[
            {
                "severity": "High",
                "title": "Current operating deficit",
            }
        ],
        forward_risks=[
            {
                "severity": "High",
                "title": "Forecast operating deficit",
            }
        ],
        cfo_recommendations=[],
        grant_diagnostics={},
        ai_cfo_report={},
        name="Test Organization",
    )

    dashboard = build_executive_dashboard(
        organization
    )

    assert dashboard["risks"] == (
        organization.risk_assessment
    )

    assert dashboard["forward_risks"] == (
        organization.forward_risks
    )

    assert dashboard["risks"] is not (
        dashboard["forward_risks"]
    )


def test_executive_dashboard_forward_risks_defaults_to_empty():
    organization = SimpleNamespace(
        financial_health={},
        kpi_dashboard={},
        financial_analysis={},
        budget_dashboard={},
        funding_gap={},
        risk_assessment=[],
        cfo_recommendations=[],
        grant_diagnostics={},
        ai_cfo_report={},
        name="Test Organization",
    )

    dashboard = build_executive_dashboard(
        organization
    )

    assert dashboard["forward_risks"] == []