from typing import Any


def generate_risk_assessment(
    income_statement: dict[str, Any] | None,
    balance_sheet: dict[str, Any] | None,
    financial_health: dict[str, Any] | None,
    budget_dashboard: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Build the first AI-FOS Risk Register.

    Each risk is represented as a structured object rather
    than free text so it can be reused by dashboards,
    reports, and the AI CFO.
    """

    income_statement = income_statement or {}
    balance_sheet = balance_sheet or {}
    financial_health = financial_health or {}
    budget_dashboard = budget_dashboard or {}
    grant_diagnostics = grant_diagnostics or {}

    risks: list[dict[str, Any]] = []

    revenue = float(income_statement.get("revenue", 0) or 0)

    net_result = float(
        income_statement.get(
            "net_profit",
            income_statement.get(
                "net_surplus_deficit",
                0,
            ),
        )
        or 0
    )

    assets = float(balance_sheet.get("assets", 0) or 0)

    liabilities = float(balance_sheet.get("liabilities", 0) or 0)

    health_score = int(
        financial_health.get(
            "score",
            0,
        )
        or 0
    )

    if revenue > 0 and net_result < 0:

        risks.append(
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Operating deficit",
                "evidence": (
                    f"Net result is {net_result:,.2f} USD."
                ),
                "recommendation": (
                    "Reduce costs or increase revenue."
                ),
            }
        )

    if liabilities > assets:

        risks.append(
            {
                "severity": "High",
                "category": "Financial Position",
                "title": "Liabilities exceed assets",
                "evidence": (
                    f"Liabilities are {liabilities:,.2f} USD "
                    f"while assets are {assets:,.2f} USD."
                ),
                "recommendation": (
                    "Review liquidity and long-term solvency."
                ),
            }
        )

    if health_score < 50:

        risks.append(
            {
                "severity": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "evidence": (
                    f"Financial Health Score is {health_score}/100."
                ),
                "recommendation": (
                    "Review the lowest-scoring categories first."
                ),
            }
        )

    if not risks:

        risks.append(
            {
                "severity": "Low",
                "category": "General",
                "title": "No major financial risks detected",
                "evidence": (
                    "Current rule set found no critical issues."
                ),
                "recommendation": (
                    "Continue monitoring financial performance."
                ),
            }
        )

    return risks