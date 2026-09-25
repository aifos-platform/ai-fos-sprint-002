from types import SimpleNamespace

from app.services.executive_dashboard import (
    build_executive_dashboard,
)


def test_executive_dashboard_includes_core_cost_coverage():
    core_cost_coverage = {
        "status": "available",
        "summary": {
            "needed_core_cost": 100000.0,
            "direct_grant_coverage": 40000.0,
            "available_indirect_recovery": 20000.0,
            "allocated_indirect_recovery": 15000.0,
            "used_indirect_recovery": 12000.0,
            "unrestricted_core_funding": 10000.0,
            "remaining_core_cost_gap": 35000.0,
            "core_cost_coverage_percentage": 65.0,
        },
        "lines": [],
        "controls": {},
    }

    organization = SimpleNamespace(
        financial_health={},
        kpi_dashboard={},
        financial_analysis={},
        budget_dashboard={},
        funding_gap={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[],
        cfo_recommendations=[],
        grant_diagnostics={},
        ai_cfo_report={},
        core_cost_coverage=core_cost_coverage,
        name="Test Organization",
    )

    dashboard = build_executive_dashboard(
        organization
    )

    assert dashboard["core_cost_coverage"] == (
        core_cost_coverage
    )

    assert dashboard["core_cost_coverage"] is (
        organization.core_cost_coverage
    )

def test_executive_dashboard_core_cost_coverage_defaults_to_empty():
    organization = SimpleNamespace(
        financial_health={},
        kpi_dashboard={},
        financial_analysis={},
        budget_dashboard={},
        funding_gap={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[],
        cfo_recommendations=[],
        grant_diagnostics={},
        ai_cfo_report={},
        name="Test Organization",
    )

    dashboard = build_executive_dashboard(
        organization
    )

    assert dashboard["core_cost_coverage"] == {}    