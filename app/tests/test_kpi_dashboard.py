from types import SimpleNamespace

from app.services.kpi_dashboard import build_kpi_dashboard


def test_kpi_dashboard_uses_current_period_income_statement_values():
    organization = SimpleNamespace(
        income_statement={
            "revenue": 8218390.31,
            "expenses": 9532573.04,
            "net_profit": -1314182.73,
            "current_period_revenue": 10208.45,
            "current_period_expenses": 1379551.15,
            "current_period_result": -1369342.70,
        },
        financial_health={},
        budget_dashboard={
            "organization": {
                "program_count": 27,
                "project_count": 0,
                "donor_count": 11,
            }
        },
        liquidity={},
        grants={},
    )

    dashboard = build_kpi_dashboard(organization)

    assert dashboard["revenue"] == 10208.45
    assert dashboard["expenses"] == 1379551.15
    assert dashboard["net_result"] == -1369342.70
    assert dashboard["program_count"] == 27
    assert dashboard["project_count"] == 0
    assert dashboard["donor_count"] == 11
