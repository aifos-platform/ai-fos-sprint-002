from typing import Any


def build_kpi_dashboard(organization) -> dict[str, Any]:
    """
    Build the Executive KPI Dashboard.
    """

    income = organization.income_statement or {}
    health = organization.financial_health or {}
    budget = organization.budget_dashboard or {}
    liquidity = organization.liquidity or {}

    return {
        "financial_health_score": health.get("score"),
        "financial_health_rating": health.get("rating"),
        "revenue": income.get("revenue"),
        "expenses": income.get("expenses"),
        "net_result": income.get("net_surplus_deficit", income.get("net_profit")),
        "available_cash": liquidity.get("available_cash"),
        "cash_runway_months": liquidity.get("cash_runway_months"),
        "budget_utilization": budget.get("executive_summary", {}).get(
            "utilization_percentage"
        ),
        "over_budget_lines": budget.get("budget_health", {}).get("over_budget_count"),
        "actuals_without_budget_lines": budget.get(
            "budget_health",
            {},
        ).get(
            "no_budget_count"
        ),
        "grant_count": len(organization.grants),
        "project_count": budget.get("organization", {}).get("project_count"),
        "donor_count": budget.get("organization", {}).get("donor_count"),
    }
