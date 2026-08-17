from typing import Any

from app.services.budget_alerts import generate_budget_alerts
from app.services.cfo_insights import generate_cfo_insights


def generate_budget_dashboard(
    budget_summary: dict[str, Any] | None,
    budget_vs_actual: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Build an executive dashboard from the budget modules.

    CFO recommendations are generated at the Organization
    level because they require financial statements,
    financial health, risk assessment, budget data,
    and grant diagnostics.
    """

    budget_summary = budget_summary or {}
    budget_vs_actual = budget_vs_actual or {}

    summary = budget_vs_actual.get(
        "summary",
        {},
    )

    dashboard = {
        "executive_summary": {
            "total_budget": summary.get(
                "total_budget",
                0,
            ),
            "total_actual": summary.get(
                "total_actual",
                0,
            ),
            "budgeted_actual": summary.get(
                "budgeted_actual",
                0,
            ),
            "unbudgeted_actual": summary.get(
                "unbudgeted_actual",
                0,
            ),
            "budget_variance": summary.get(
                "total_variance",
                0,
            ),
            "overall_variance_including_unbudgeted": summary.get(
                "overall_variance_including_unbudgeted",
                0,
            ),
            "utilization_percentage": summary.get(
                "utilization_percentage",
                0,
            ),
        },
        "budget_health": {
            "budget_line_count": summary.get(
                "budget_line_count",
                0,
            ),
            "over_budget_count": summary.get(
                "over_budget_count",
                0,
            ),
            "within_budget_count": summary.get(
                "within_budget_count",
                0,
            ),
            "no_budget_count": summary.get(
                "no_budget_count",
                0,
            ),
        },
        "organization": {
            "fund_count": budget_summary.get(
                "fund_count",
                0,
            ),
            "donor_count": budget_summary.get(
                "donor_count",
                0,
            ),
            "program_count": budget_summary.get(
                "program_count",
                0,
            ),
            "project_count": budget_summary.get(
                "project_count",
                0,
            ),
        },

        "by_fiscal_year": budget_vs_actual.get(
            "by_fiscal_year",
            {},
        ),

        "portfolio_control": budget_vs_actual.get(
            "portfolio_control",
            {},
        ),

        "largest_funds": budget_summary.get(
            "largest_funds",
            [],
        ),
        "largest_donors": budget_summary.get(
            "largest_donors",
            [],
        ),
        "largest_programs": budget_summary.get(
            "largest_programs",
            [],
        ),
        "largest_projects": budget_summary.get(
            "largest_projects",
            [],
        ),
    }

    dashboard["alerts"] = generate_budget_alerts(dashboard)

    dashboard["cfo_insights"] = generate_cfo_insights(dashboard)

    return dashboard
