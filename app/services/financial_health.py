from typing import Any


def calculate_financial_health(
    income_statement: dict[str, Any] | None,
    balance_sheet: dict[str, Any] | None,
    budget_dashboard: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
    liquidity: dict[str, Any] | None,
    funding_gap: dict[str, Any] | None = None,
    budget_mapping_intelligence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate the transparent AI-FOS Financial Health Score.

    The total score is 100 points across five categories:

    1. Operating Performance: 25
    2. Financial Position: 20
    3. Liquidity: 20
    4. Budget Control: 20
    5. Funding and Grant Health: 15

    Funding and Grant Health uses the validated Funding Gap
    engine rather than treating gross secured funding as
    automatically available.

    Grant coverage differences remain diagnostic unless
    comparable-period evidence supports a stronger conclusion.
    """

    income_statement = (
        income_statement or {}
    )

    balance_sheet = (
        balance_sheet or {}
    )

    budget_dashboard = (
        budget_dashboard or {}
    )

    grant_diagnostics = (
        grant_diagnostics or {}
    )

    liquidity = (
        liquidity or {}
    )

    funding_gap = (
        funding_gap or {}
    )

    budget_mapping_intelligence = (
        budget_mapping_intelligence or {}
    )

    budget_mapping_summary = (
        budget_mapping_intelligence.get(
            "summary",
            {},
        )
        or {}
    )

    broader_match_actual = _to_float(
        budget_mapping_summary.get(
            "broader_match_actual"
        )
    )

    no_budget_identified_actual = _to_float(
        budget_mapping_summary.get(
            "no_budget_identified_actual"
        )
    )

    category_scores: dict[
        str,
        dict[str, Any],
    ] = {}

    # --------------------------------------------------
    # 1. Operating performance: 25 points
    # --------------------------------------------------

    revenue = _to_float(
        income_statement.get(
            "revenue"
        )
    )

    net_result = _to_float(
        income_statement.get(
            "net_profit",
            income_statement.get(
                "net_surplus_deficit",
                0,
            ),
        )
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
            abs(
                net_result
            )
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

    category_scores[
        "operating_performance"
    ] = {
        "score": (
            operating_score
        ),
        "maximum": 25,
        "reason": (
            operating_reason
        ),
    }

    # --------------------------------------------------
    # 2. Financial position: 20 points
    # --------------------------------------------------

    equity = _to_float(
        balance_sheet.get(
            "equity"
        )
    )

    financial_position_score = 20

    financial_position_reasons: list[
        str
    ] = []

    if equity < 0:

        financial_position_score -= 12

        financial_position_reasons.append(
            (
                "Adjusted equity/net assets are negative "
                f"at {equity:,.2f}."
            )
        )

    category_scores[
        "financial_position"
    ] = {
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

    cash_runway = (
        liquidity.get(
            "cash_runway_months"
        )
    )

    if cash_runway is None:

        liquidity_score = 0

        liquidity_reason = (
            "Cash Runway could not be calculated."
        )

    else:

        cash_runway = _to_float(
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

    category_scores[
        "liquidity"
    ] = {
        "score": (
            liquidity_score
        ),
        "maximum": 20,
        "reason": (
            liquidity_reason
        ),
    }

    # --------------------------------------------------
    # 4. Budget control: 20 points
    # --------------------------------------------------

    health = (
        budget_dashboard.get(
            "budget_health",
            {},
        )
        or {}
    )

    executive_summary = (
        budget_dashboard.get(
            "executive_summary",
            {},
        )
        or {}
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

    total_budget = _to_float(
        executive_summary.get(
            "total_budget"
        )
    )

    budgeted_actual = _to_float(
        executive_summary.get(
            "budgeted_actual"
        )
    )

    unbudgeted_actual = _to_float(
        executive_summary.get(
            "unbudgeted_actual"
        )
    )

    utilization_percentage = (
        budgeted_actual
        / total_budget
        * 100
        if total_budget > 0
        else None
    )

    unbudgeted_ratio = (
        abs(
            unbudgeted_actual
        )
        / total_budget
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

    if (
        utilization_percentage is not None
        and unbudgeted_ratio is not None
    ):

        if budget_mapping_summary:

            budget_reason = (
                f"Budget utilization is "
                f"{utilization_percentage:.2f}%. Strict "
                f"budget-line matching identified "
                f"{unbudgeted_actual:,.2f} of actual spending "
                f"without an exact budget-line match, "
                f"representing "
                f"{unbudgeted_ratio * 100:.2f}% of total "
                f"budget. Mapping analysis found broader budget "
                f"relationships for "
                f"{broader_match_actual:,.2f} of these "
                f"exceptions, requiring finance review, while "
                f"{no_budget_identified_actual:,.2f} currently "
                f"has no identified budget relationship. "
                f"{over_budget_count} aggregated budget line "
                f"code(s) are above budget and "
                f"{no_budget_count} aggregated budget line "
                f"code(s) contain exact-match exceptions."
            )

        else:

            budget_reason = (
                f"Budget utilization is "
                f"{utilization_percentage:.2f}% and "
                f"unbudgeted actual spending is "
                f"{unbudgeted_actual:,.2f}, representing "
                f"{unbudgeted_ratio * 100:.2f}% of total "
                f"budget. {over_budget_count} aggregated "
                f"budget line code(s) are above budget and "
                f"{no_budget_count} aggregated budget line "
                f"code(s) have actual activity with no "
                f"budget amount identified in the current "
                f"portfolio view."
            )

    else:

        budget_reason = (
            "Insufficient budget information was "
            "available to assess budget control."
        )

    category_scores[
        "budget_control"
    ] = {
        "score": (
            budget_score
        ),
        "maximum": 20,
        "reason": (
            budget_reason
        ),
    }

    # --------------------------------------------------
    # 5. Funding and Grant Health: 15 points
    # --------------------------------------------------

    funding_summary = (
        funding_gap.get(
            "summary",
            {},
        )
        or {}
    )

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

    remaining_requirement = _to_float(
        funding_summary.get(
            "remaining_requirement"
        )
    )

    applied_secured_funding = _to_float(
        funding_summary.get(
            "applied_secured_funding"
        )
    )

    funding_gap_amount = _to_float(
        funding_summary.get(
            "funding_gap"
        )
    )

    applied_coverage_percentage_raw = (
        funding_summary.get(
            "applied_coverage_percentage"
        )
    )

    unmatched_requirement_count = int(
        funding_summary.get(
            "unmatched_requirement_count",
            0,
        )
        or 0
    )

    matched_requirement_count = int(
        funding_summary.get(
            "matched_requirement_count",
            0,
        )
        or 0
    )

    if (
        applied_coverage_percentage_raw
        is None
    ):

        if remaining_requirement <= 0:

            funding_score = 15

            funding_reason = (
                "No remaining funding requirement "
                "was identified."
            )

        else:

            funding_score = 0

            funding_reason = (
                "Funding coverage could not be "
                "reliably calculated."
            )

    else:

        applied_coverage_percentage = (
            _to_float(
                applied_coverage_percentage_raw
            )
        )

        #
        # Funding coverage: maximum 15 points.
        #
        # These thresholds deliberately assess the
        # proportion of remaining organizational needs
        # that can be supported by currently validated
        # eligible secured funding.
        #
        if (
            applied_coverage_percentage
            >= 90
        ):

            funding_score = 15

        elif (
            applied_coverage_percentage
            >= 75
        ):

            funding_score = 12

        elif (
            applied_coverage_percentage
            >= 60
        ):

            funding_score = 9

        elif (
            applied_coverage_percentage
            >= 40
        ):

            funding_score = 6

        elif (
            applied_coverage_percentage
            >= 20
        ):

            funding_score = 3

        else:

            funding_score = 0

        funding_reason = (
            f"Validated eligible secured funding covers "
            f"{applied_coverage_percentage:.2f}% of the "
            f"remaining requirement. "
            f"{applied_secured_funding:,.2f} of secured "
            f"funding was applied against "
            f"{remaining_requirement:,.2f} of remaining "
            f"requirements, leaving a Funding Gap of "
            f"{funding_gap_amount:,.2f}. "
            f"{matched_requirement_count} requirement(s) "
            f"have eligible secured funding and "
            f"{unmatched_requirement_count} requirement(s) "
            f"do not currently have validated eligible "
            f"secured funding."
        )

    #
    # Grant coverage differences remain diagnostic.
    #
    grant_diagnostic_note = (
        f"{len(actual_only)} grant(s) have actual "
        f"activity with no grant budget identified "
        f"in the currently loaded budget dataset, "
        f"and {len(budget_only)} grant(s) have a "
        f"budget with no actual activity. These "
        f"differences remain diagnostic and do not "
        f"independently reduce the score."
    )

    category_scores[
        "funding_and_grant_health"
    ] = {
        "score": (
            funding_score
        ),
        "maximum": 15,
        "reason": (
            f"{funding_reason} "
            f"{grant_diagnostic_note}"
        ),
        "metrics": {
            "remaining_requirement": round(
                remaining_requirement,
                2,
            ),
            "applied_secured_funding": round(
                applied_secured_funding,
                2,
            ),
            "funding_gap": round(
                funding_gap_amount,
                2,
            ),
            "applied_coverage_percentage": (
                round(
                    _to_float(
                        applied_coverage_percentage_raw
                    ),
                    2,
                )
                if (
                    applied_coverage_percentage_raw
                    is not None
                )
                else None
            ),
            "matched_requirement_count": (
                matched_requirement_count
            ),
            "unmatched_requirement_count": (
                unmatched_requirement_count
            ),
            "actual_only_grant_count": (
                len(
                    actual_only
                )
            ),
            "budget_only_grant_count": (
                len(
                    budget_only
                )
            ),
        },
    }

    # --------------------------------------------------
    # Overall Financial Health Score
    # --------------------------------------------------

    total_score = sum(
        category[
            "score"
        ]
        for category
        in category_scores.values()
    )

    if total_score >= 85:

        rating = (
            "Strong"
        )

    elif total_score >= 70:

        rating = (
            "Good"
        )

    elif total_score >= 55:

        rating = (
            "Fair"
        )

    elif total_score >= 40:

        rating = (
            "Weak"
        )

    else:

        rating = (
            "Critical"
        )

    return {
        "score": (
            total_score
        ),
        "maximum": 100,
        "rating": (
            rating
        ),
        "categories": (
            category_scores
        ),
    }


def _to_float(
    value: Any,
) -> float:
    """
    Safely convert a financial value to float.
    """

    if value is None:
        return 0.0

    if isinstance(
        value,
        (int, float),
    ):

        return float(
            value
        )

    text = (
        str(
            value
        )
        .replace(
            ",",
            "",
        )
        .replace(
            "$",
            "",
        )
        .strip()
    )

    if not text:
        return 0.0

    if (
        text.startswith(
            "("
        )
        and text.endswith(
            ")"
        )
    ):

        text = (
            "-"
            + text[
                1:-1
            ]
        )

    try:

        return float(
            text
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0
