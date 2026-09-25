from typing import Any


def generate_financial_scenario(
    financial_forecast: dict[str, Any] | None,
    liquidity: dict[str, Any] | None = None,
    *,
    scenario_name: str = "Custom Scenario",
    revenue_change_percentage: float = 0.0,
    expense_change_percentage: float = 0.0,
    one_time_revenue_adjustment: float = 0.0,
    one_time_expense_adjustment: float = 0.0,
    cash_inflow_adjustment: float = 0.0,
    cash_outflow_adjustment: float = 0.0,
) -> dict[str, Any]:
    """
    Generate a deterministic financial what-if scenario.

    Scenario Intelligence does not modify the validated
    baseline forecast. It creates a separate alternative
    view based only on explicit scenario assumptions.

    Supported v1 assumptions:
    - percentage change in forecast revenue;
    - percentage change in forecast expenses;
    - one-time revenue adjustment;
    - one-time expense adjustment;
    - explicit cash inflow adjustment;
    - explicit cash outflow adjustment.

    Revenue and expense assumptions affect the projected
    Income Statement scenario.

    Cash adjustments affect cash separately. Revenue and
    expense assumptions are not automatically treated as
    cash movements because accounting revenue/expense and
    cash receipts/payments are not necessarily identical.
    """

    financial_forecast = financial_forecast or {}
    liquidity = liquidity or {}

    if financial_forecast.get("status") != "available":
        return {
            "status": "not_available",
            "scenario_name": scenario_name,
            "reason": (
                "A validated baseline financial forecast is "
                "required before AI-FOS can calculate a "
                "financial scenario."
            ),
        }

    baseline_totals = (
        financial_forecast.get(
            "forecast_totals",
            {},
        )
        or {}
    )

    baseline_series = (
        financial_forecast.get(
            "forecast_series",
            [],
        )
        or []
    )

    forecast_horizon_months = _to_int(
        financial_forecast.get(
            "forecast_horizon_months"
        )
    )

    baseline_revenue = _to_float(
        baseline_totals.get("revenue")
    )

    baseline_expenses = _to_float(
        baseline_totals.get("expenses")
    )

    baseline_net_result = _to_float(
        baseline_totals.get("net_result")
    )

    revenue_change_percentage = _to_float(
        revenue_change_percentage
    )

    expense_change_percentage = _to_float(
        expense_change_percentage
    )

    one_time_revenue_adjustment = _to_float(
        one_time_revenue_adjustment
    )

    one_time_expense_adjustment = _to_float(
        one_time_expense_adjustment
    )

    cash_inflow_adjustment = _to_float(
        cash_inflow_adjustment
    )

    cash_outflow_adjustment = _to_float(
        cash_outflow_adjustment
    )

    # --------------------------------------------------
    # Scenario Income Statement
    # --------------------------------------------------

    percentage_revenue_impact = round(
        baseline_revenue
        * revenue_change_percentage
        / 100,
        2,
    )

    percentage_expense_impact = round(
        baseline_expenses
        * expense_change_percentage
        / 100,
        2,
    )

    scenario_revenue = round(
        baseline_revenue
        + percentage_revenue_impact
        + one_time_revenue_adjustment,
        2,
    )

    scenario_expenses = round(
        baseline_expenses
        + percentage_expense_impact
        + one_time_expense_adjustment,
        2,
    )

    scenario_net_result = round(
        scenario_revenue
        - scenario_expenses,
        2,
    )

    revenue_variance = round(
        scenario_revenue
        - baseline_revenue,
        2,
    )

    expense_variance = round(
        scenario_expenses
        - baseline_expenses,
        2,
    )

    net_result_variance = round(
        scenario_net_result
        - baseline_net_result,
        2,
    )

    # --------------------------------------------------
    # Scenario monthly series
    # --------------------------------------------------

    scenario_series = _build_scenario_series(
        baseline_series=baseline_series,
        revenue_change_percentage=(
            revenue_change_percentage
        ),
        expense_change_percentage=(
            expense_change_percentage
        ),
        one_time_revenue_adjustment=(
            one_time_revenue_adjustment
        ),
        one_time_expense_adjustment=(
            one_time_expense_adjustment
        ),
    )

    # --------------------------------------------------
    # Explicit cash scenario
    # --------------------------------------------------

    baseline_available_cash = _optional_float(
        liquidity.get("available_cash")
    )

    net_cash_adjustment = round(
        cash_inflow_adjustment
        - cash_outflow_adjustment,
        2,
    )

    scenario_available_cash: float | None = None
    available_cash_variance: float | None = None

    if baseline_available_cash is not None:
        scenario_available_cash = round(
            baseline_available_cash
            + net_cash_adjustment,
            2,
        )

        available_cash_variance = round(
            scenario_available_cash
            - baseline_available_cash,
            2,
        )

    # --------------------------------------------------
    # Cash runway
    # --------------------------------------------------

    baseline_runway = _optional_float(
        liquidity.get("cash_runway_months")
    )

    average_monthly_operating_expenses = (
        _get_average_monthly_operating_expenses(
            liquidity=liquidity,
        )
    )

    scenario_runway: float | None = None
    runway_change: float | None = None

    if (
        scenario_available_cash is not None
        and average_monthly_operating_expenses is not None
        and average_monthly_operating_expenses > 0
    ):
        scenario_runway = round(
            scenario_available_cash
            / average_monthly_operating_expenses,
            2,
        )

        if baseline_runway is not None:
            runway_change = round(
                scenario_runway
                - baseline_runway,
                2,
            )

    # --------------------------------------------------
    # Scenario interpretation
    # --------------------------------------------------

    if net_result_variance > 0:
        net_result_direction = "improved"

    elif net_result_variance < 0:
        net_result_direction = "deteriorated"

    else:
        net_result_direction = "unchanged"

    assumptions = {
        "revenue_change_percentage": round(
            revenue_change_percentage,
            2,
        ),
        "expense_change_percentage": round(
            expense_change_percentage,
            2,
        ),
        "one_time_revenue_adjustment": round(
            one_time_revenue_adjustment,
            2,
        ),
        "one_time_expense_adjustment": round(
            one_time_expense_adjustment,
            2,
        ),
        "cash_inflow_adjustment": round(
            cash_inflow_adjustment,
            2,
        ),
        "cash_outflow_adjustment": round(
            cash_outflow_adjustment,
            2,
        ),
    }

    return {
        "status": "available",
        "scenario_name": scenario_name,
        "scenario_type": "what_if",
        "forecast_horizon_months": (
            forecast_horizon_months
        ),
        "baseline": {
            "revenue": round(
                baseline_revenue,
                2,
            ),
            "expenses": round(
                baseline_expenses,
                2,
            ),
            "net_result": round(
                baseline_net_result,
                2,
            ),
        },
        "assumptions": assumptions,
        "scenario": {
            "revenue": scenario_revenue,
            "expenses": scenario_expenses,
            "net_result": scenario_net_result,
        },
        "impact": {
            "revenue_variance": revenue_variance,
            "expense_variance": expense_variance,
            "net_result_variance": (
                net_result_variance
            ),
            "net_result_direction": (
                net_result_direction
            ),
        },
        "scenario_series": scenario_series,
        "cash": {
            "baseline_available_cash": (
                baseline_available_cash
            ),
            "cash_inflow_adjustment": (
                round(
                    cash_inflow_adjustment,
                    2,
                )
            ),
            "cash_outflow_adjustment": (
                round(
                    cash_outflow_adjustment,
                    2,
                )
            ),
            "net_cash_adjustment": (
                net_cash_adjustment
            ),
            "scenario_available_cash": (
                scenario_available_cash
            ),
            "available_cash_variance": (
                available_cash_variance
            ),
        },
        "runway": {
            "baseline_cash_runway_months": (
                baseline_runway
            ),
            "average_monthly_operating_expenses": (
                average_monthly_operating_expenses
            ),
            "scenario_cash_runway_months": (
                scenario_runway
            ),
            "cash_runway_change_months": (
                runway_change
            ),
            "available": (
                scenario_runway is not None
            ),
        },
        "methodology": (
            "explicit_assumption_scenario"
        ),
        "methodology_description": (
            "The scenario starts from the validated AI-FOS "
            "baseline financial forecast and applies only the "
            "explicit assumptions supplied for the scenario. "
            "The validated baseline forecast itself is not "
            "modified."
        ),
        "controls": {
            "baseline_forecast_preserved": True,
            "revenue_expense_not_assumed_cash": True,
            "cash_requires_explicit_adjustment": True,
            "runway_requires_authoritative_liquidity_inputs": (
                True
            ),
        },
        "cautions": [
            (
                "Scenario results are hypothetical and are "
                "not predictions or guaranteed outcomes."
            ),
            (
                "Revenue and expense changes are not "
                "automatically treated as cash movements."
            ),
            (
                "Cash impacts are calculated only from "
                "explicit cash inflow and cash outflow "
                "assumptions."
            ),
            (
                "Cash runway is recalculated only when "
                "authoritative available-cash and average "
                "monthly operating-expense inputs are "
                "available."
            ),
            (
                "The scenario should be interpreted together "
                "with funding, grant, budget, liquidity, risk, "
                "and management information."
            ),
        ],
    }


def _build_scenario_series(
    baseline_series: list[dict[str, Any]],
    revenue_change_percentage: float,
    expense_change_percentage: float,
    one_time_revenue_adjustment: float,
    one_time_expense_adjustment: float,
) -> list[dict[str, Any]]:
    """
    Apply recurring percentage assumptions to each baseline
    forecast period.

    One-time adjustments are applied to the first forecast
    period only so they are not accidentally repeated across
    the entire forecast horizon.
    """

    result: list[dict[str, Any]] = []

    for index, record in enumerate(
        baseline_series
    ):
        if not isinstance(
            record,
            dict,
        ):
            continue

        baseline_revenue = _to_float(
            record.get("revenue")
        )

        baseline_expenses = _to_float(
            record.get("expenses")
        )

        revenue = round(
            baseline_revenue
            * (
                1
                + revenue_change_percentage
                / 100
            ),
            2,
        )

        expenses = round(
            baseline_expenses
            * (
                1
                + expense_change_percentage
                / 100
            ),
            2,
        )

        if index == 0:
            revenue = round(
                revenue
                + one_time_revenue_adjustment,
                2,
            )

            expenses = round(
                expenses
                + one_time_expense_adjustment,
                2,
            )

        net_result = round(
            revenue - expenses,
            2,
        )

        result.append(
            {
                "period": record.get(
                    "period"
                ),
                "baseline_revenue": round(
                    baseline_revenue,
                    2,
                ),
                "baseline_expenses": round(
                    baseline_expenses,
                    2,
                ),
                "baseline_net_result": round(
                    baseline_revenue
                    - baseline_expenses,
                    2,
                ),
                "scenario_revenue": revenue,
                "scenario_expenses": expenses,
                "scenario_net_result": (
                    net_result
                ),
            }
        )

    return result


def _get_average_monthly_operating_expenses(
    liquidity: dict[str, Any],
) -> float | None:
    """
    Read an authoritative operating-expense basis when one
    exists in the validated liquidity artifact.

    No operating-expense amount is inferred here.
    """

    candidate_fields = [
        "average_monthly_operating_expenses",
        "monthly_operating_expenses",
        "average_monthly_expenses",
    ]

    for field in candidate_fields:
        value = _optional_float(
            liquidity.get(field)
        )

        if (
            value is not None
            and value > 0
        ):
            return value

    return None


def _optional_float(
    value: Any,
) -> float | None:

    if value in {
        None,
        "",
    }:
        return None

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return None


def _to_float(
    value: Any,
) -> float:

    if value in {
        None,
        "",
    }:
        return 0.0

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _to_int(
    value: Any,
) -> int:

    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0