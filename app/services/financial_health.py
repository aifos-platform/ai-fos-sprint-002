from typing import Any


def calculate_financial_health(
    income_statement: dict[str, Any] | None,
    balance_sheet: dict[str, Any] | None,
    budget_dashboard: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
    liquidity: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Calculate a transparent first-version Financial Health Score.

    The total score is 100 points across five categories:

    1. Operating Performance: 25
    2. Financial Position: 20
    3. Liquidity: 20
    4. Budget Control: 20
    5. Grant and Data Quality: 15
    """

    income_statement = income_statement or {}
    balance_sheet = balance_sheet or {}
    budget_dashboard = budget_dashboard or {}
    grant_diagnostics = grant_diagnostics or {}
    liquidity = liquidity or {}

    category_scores: dict[str, dict[str, Any]] = {}

    # --------------------------------------------------
    # 1. Operating performance: 25 points
    # --------------------------------------------------

    revenue = float(
        income_statement.get(
            "revenue",
            0,
        )
        or 0
    )

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

    if revenue <= 0:
        operating_score = 0
        operating_reason = (
            "No positive revenue was available."
        )

    elif net_result >= 0:
        operating_score = 25
        operating_reason = (
            "The organisation generated a surplus."
        )

    else:
        deficit_ratio = (
            abs(net_result)
            / revenue
        )

        if deficit_ratio <= 0.05:
            operating_score = 20

        elif deficit_ratio <= 0.15:
            operating_score = 15

        elif deficit_ratio <= 0.30:
            operating_score = 8

        else:
            operating_score = 0

        operating_reason = (
            f"The deficit was "
            f"{deficit_ratio * 100:.2f}% "
            f"of revenue."
        )

    category_scores["operating_performance"] = {
        "score": operating_score,
        "maximum": 25,
        "reason": operating_reason,
    }

    # --------------------------------------------------
    # 2. Financial position: 20 points
    # --------------------------------------------------

    assets = float(
        balance_sheet.get(
            "assets",
            0,
        )
        or 0
    )

    liabilities = float(
        balance_sheet.get(
            "liabilities",
            0,
        )
        or 0
    )

    difference = float(
        balance_sheet.get(
            "difference",
            0,
        )
        or 0
    )

    financial_position_score = 20

    financial_position_reasons: list[str] = []

    equity = float(
        balance_sheet.get(
            "equity",
            0,
        )
        or 0
    )

    if equity < 0:
        financial_position_score -= 12

        financial_position_reasons.append(
            (
                "Adjusted equity/net assets are negative "
                f"at {equity:,.2f}."
            )
        )

    category_scores["financial_position"] = {
        "score": max(
            financial_position_score,
            0,
        ),
        "maximum": 20,
        "reason": (
            " ".join(
                financial_position_reasons
            )
            or (
                "The reported financial position "
                "is balanced."
            )
        ),
    }

    # --------------------------------------------------
    # 3. Liquidity: 20 points
    # --------------------------------------------------

    cash_runway = liquidity.get(
        "cash_runway_months"
    )

    if cash_runway is None:
        liquidity_score = 0

        liquidity_reason = (
            "Cash Runway could not be calculated."
        )

    else:
        cash_runway = float(
            cash_runway
        )

        if cash_runway >= 12:
            liquidity_score = 20

        elif cash_runway >= 9:
            liquidity_score = 17

        elif cash_runway >= 6:
            liquidity_score = 14

        elif cash_runway >= 3:
            liquidity_score = 8

        elif cash_runway >= 1:
            liquidity_score = 4

        else:
            liquidity_score = 0

        liquidity_reason = (
            f"Available cash provides "
            f"{cash_runway:.2f} months "
            f"of operating expense coverage."
        )

    category_scores["liquidity"] = {
        "score": liquidity_score,
        "maximum": 20,
        "reason": liquidity_reason,
    }

    # --------------------------------------------------
    # 4. Budget control: 20 points
    # --------------------------------------------------

    health = budget_dashboard.get(
        "budget_health",
        {},
    )

    executive_summary = budget_dashboard.get(
        "executive_summary",
        {},
    )

    over_budget_count = int(
        health.get(
            "over_budget_count",
            0,
        )
        or 0
    )

    no_budget_count = int(
        health.get(
            "no_budget_count",
            0,
        )
        or 0
    )

    total_budget = float(
        executive_summary.get(
            "total_budget",
            0,
        )
        or 0
    )

    budgeted_actual = float(
        executive_summary.get(
            "budgeted_actual",
            0,
        )
        or 0
    )

    unbudgeted_actual = float(
        executive_summary.get(
            "unbudgeted_actual",
            0,
        )
        or 0
    )

    utilization_percentage = (
        budgeted_actual / total_budget * 100
        if total_budget > 0
        else None
    )

    unbudgeted_ratio = (
        abs(unbudgeted_actual) / total_budget
        if total_budget > 0
        else None
    )

    #
    # Budget utilization: maximum 10 points.
    #

    if utilization_percentage is None:
        utilization_score = 0

    elif utilization_percentage <= 100:
        utilization_score = 10

    elif utilization_percentage <= 105:
        utilization_score = 8

    elif utilization_percentage <= 110:
        utilization_score = 6

    elif utilization_percentage <= 120:
        utilization_score = 3

    else:
        utilization_score = 0

    #
    # Unbudgeted spending: maximum 10 points.
    #

    if unbudgeted_ratio is None:
        unbudgeted_score = 0

    elif unbudgeted_ratio < 0.0001:
        unbudgeted_score = 10

    elif unbudgeted_ratio <= 0.01:
        unbudgeted_score = 9

    elif unbudgeted_ratio <= 0.03:
        unbudgeted_score = 7

    elif unbudgeted_ratio <= 0.05:
        unbudgeted_score = 5

    elif unbudgeted_ratio <= 0.10:
        unbudgeted_score = 2

    else:
        unbudgeted_score = 0

    budget_score = (
        utilization_score
        + unbudgeted_score
    )

    category_scores["budget_control"] = {
        "score": budget_score,
        "maximum": 20,
        "reason": (
            f"Budget utilization is "
            f"{utilization_percentage:.2f}% and "
            f"unbudgeted actual spending is "
            f"{unbudgeted_actual:,.2f}, representing "
            f"{unbudgeted_ratio * 100:.2f}% of total budget. "
            f"{over_budget_count} budget line(s) are over budget "
            f"and {no_budget_count} line(s) have actual activity "
            f"without an approved budget."
            if (
                utilization_percentage is not None
                and unbudgeted_ratio is not None
            )
            else (
                "Insufficient budget information was available "
                "to assess budget control."
            )
        ),
    }

    # --------------------------------------------------
    # 5. Grant and data quality: 15 points
    # --------------------------------------------------

    actual_only = (
        grant_diagnostics.get(
            "actual_only_grants",
            [],
        )
        or []
    )

    budget_only = (
        grant_diagnostics.get(
            "budget_only_grants",
            [],
        )
        or []
    )

    grant_score = 15

    grant_score -= min(
        len(actual_only),
        9,
    )

    grant_score -= min(
        len(budget_only),
        6,
    )

    category_scores["grant_data_quality"] = {
        "score": max(
            grant_score,
            0,
        ),
        "maximum": 15,
        "reason": (
            f"{len(actual_only)} grants have "
            f"actuals without budgets and "
            f"{len(budget_only)} grants have "
            f"budgets without actuals."
        ),
    }

    # --------------------------------------------------
    # Overall Financial Health Score
    # --------------------------------------------------

    total_score = sum(
        category["score"]
        for category
        in category_scores.values()
    )

    if total_score >= 85:
        rating = "Strong"

    elif total_score >= 70:
        rating = "Good"

    elif total_score >= 55:
        rating = "Fair"

    elif total_score >= 40:
        rating = "Weak"

    else:
        rating = "Critical"

    return {
        "score": total_score,
        "maximum": 100,
        "rating": rating,
        "categories": category_scores,
    }