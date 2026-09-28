from typing import Any


def generate_budget_alerts(
    budget_dashboard: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate executive alerts from the Budget Dashboard.
    """

    alerts: list[dict[str, str]] = []

    portfolio_control = budget_dashboard.get(
        "portfolio_control",
        {},
    )

    utilization = portfolio_control.get(
        "utilization_percentage",
        0,
    )
    unbudgeted_actual = portfolio_control.get(
        "unbudgeted_actual",
        0,
    )

    over_budget = portfolio_control.get(
        "over_budget_count",
        0,
    )
    no_budget = portfolio_control.get(
        "no_budget_count",
        0,
    )

    if over_budget > 0:
        alerts.append(
            {
                "severity": "High",
                "message": (
                    f"{over_budget} portfolio budget lines have exceeded "
                    "their approved budgets."
                ),
            }
        )

    if unbudgeted_actual > 0:
        alerts.append(
            {
                "severity": "High",
                "message": (
                    f"${unbudgeted_actual:,.2f} of portfolio actual spending "
                    "does not have an exact approved budget-line match and "
                    "requires budget mapping review."
                ),
                            }
        )

    elif no_budget > 0:
        alerts.append(
            {
                "severity": "Medium",
                "message": (
                    f"{no_budget} portfolio budget line(s) have actual "
                    "activity without an approved budget."
                ),
            }
        )

    if utilization > 100:
        alerts.append(
            {
                "severity": "High",
                "message": (
                    f"Portfolio budget utilization has reached "
                    f"{utilization:.2f}%, indicating cumulative spending "
                    "above the approved portfolio budget."
                ),
            }
        )

    elif utilization < 30:
        alerts.append(
            {
                "severity": "Low",
                "message": (
                    f"Portfolio budget utilization is only "
                    f"{utilization:.2f}%."
                ),
            }
        )

    if not alerts:
        alerts.append(
            {
                "severity": "Info",
                "message": (
                    "No significant budget issues detected."
                ),
            }
        )

    return alerts