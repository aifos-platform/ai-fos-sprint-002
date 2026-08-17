from typing import Any


def generate_cfo_insights(
    budget_dashboard: dict[str, Any],
) -> list[str]:
    """
    Generate executive narrative insights
    from the Budget Dashboard.
    """

    insights: list[str] = []

    portfolio_control = budget_dashboard.get(
        "portfolio_control",
        {},
    )

    utilization = portfolio_control.get(
        "utilization_percentage",
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

    unbudgeted_actual = portfolio_control.get(
        "unbudgeted_actual",
        0,
    )    

    if utilization < 30:
        insights.append(
            (
                f"Portfolio budget utilization is only "
                f"{utilization:.2f}%, indicating that "
                "most planned activities have not yet "
                "been executed."
            )
        )

    elif utilization > 100:
        insights.append(
            (
                f"Portfolio budget utilization has reached "
                f"{utilization:.2f}%, meaning cumulative actual "
                "spending against approved portfolio budget lines "
                "has exceeded the approved portfolio budget."
            )
        )

    elif utilization > 90:
        insights.append(
            (
                f"Portfolio budget utilization has reached "
                f"{utilization:.2f}%, leaving limited "
                "portfolio budget available."
            )
        )

    if over_budget > 0:
        insights.append(
            (
                f"{over_budget} portfolio budget lines are "
                "already above their approved limits."
            )
        )

    if unbudgeted_actual > 0:
        insights.append(
            (
                f"${unbudgeted_actual:,.2f} of portfolio actual "
                "spending has no matching approved "
                "budget and requires management review."
            )
        )

    elif no_budget > 0:
        insights.append(
            (
                f"{no_budget} portfolio budget line(s) have actual "
                "activity without an approved budget."
            )
        )

    if not insights:
        insights.append(
            "No significant financial concerns were detected."
        )

    return insights