from typing import Any


def generate_financial_forecast(
    financial_trends: dict[str, Any] | None,
    forecast_months: int = 3,
    baseline_months: int = 6,
) -> dict[str, Any]:
    """
    Generate deterministic baseline financial forecasts from
    validated Financial Trend Intelligence.

    Forecast Intelligence v1 intentionally uses a conservative
    historical run-rate methodology rather than an ML model.

    Methodology:
    - consume validated monthly trend observations;
    - exclude the latest observed month from the baseline to
      reduce partial-period distortion;
    - use up to the most recent baseline_months observations;
    - calculate average monthly revenue and expenses;
    - project those baseline amounts forward;
    - derive forecast net result as revenue minus expenses.

    The engine does not alter historical observations and does
    not interpret forecasts as guaranteed outcomes.
    """

    financial_trends = financial_trends or {}

    monthly_series = financial_trends.get(
        "monthly_series",
        [],
    )

    if not isinstance(
        monthly_series,
        list,
    ):
        monthly_series = []

    valid_months = [
        record
        for record in monthly_series
        if _is_valid_month_record(record)
    ]

    valid_months.sort(
        key=lambda record: str(
            record.get("period")
        )
    )

    forecast_months = _normalize_positive_int(
        forecast_months,
        default=3,
    )

    baseline_months = _normalize_positive_int(
        baseline_months,
        default=6,
    )

    # --------------------------------------------------
    # Data sufficiency
    # --------------------------------------------------

    # The latest observed period is deliberately excluded
    # from the baseline because the source period may still
    # be incomplete.
    if len(valid_months) < 4:
        return {
            "status": "not_available",
            "reason": (
                "At least four validated monthly financial "
                "periods are required to build the baseline "
                "forecast safely. The latest observed period "
                "is excluded from the forecast baseline."
            ),
            "methodology": (
                "historical_average_run_rate"
            ),
            "forecast_horizon_months": (
                forecast_months
            ),
            "history": {
                "observed_month_count": len(
                    valid_months
                ),
                "minimum_required_month_count": 4,
                "latest_period_excluded_from_baseline": (
                    True
                ),
            },
            "forecast_series": [],
        }

    latest_observed = valid_months[-1]

    baseline_candidates = valid_months[:-1]

    history_used = baseline_candidates[
        -baseline_months:
    ]

    if len(history_used) < 3:
        return {
            "status": "not_available",
            "reason": (
                "At least three historical baseline months "
                "are required after excluding the latest "
                "observed period."
            ),
            "methodology": (
                "historical_average_run_rate"
            ),
            "forecast_horizon_months": (
                forecast_months
            ),
            "forecast_series": [],
        }

    # --------------------------------------------------
    # Historical baseline
    # --------------------------------------------------

    average_revenue = round(
        sum(
            _to_float(
                record.get("revenue")
            )
            for record in history_used
        )
        / len(history_used),
        2,
    )

    average_expenses = round(
        sum(
            _to_float(
                record.get("expenses")
            )
            for record in history_used
        )
        / len(history_used),
        2,
    )

    average_net_result = round(
        average_revenue
        - average_expenses,
        2,
    )

    latest_period = str(
        latest_observed.get("period")
    )

    forecast_periods = _future_months(
        latest_period=latest_period,
        count=forecast_months,
    )

    # --------------------------------------------------
    # Baseline forecast
    # --------------------------------------------------

    forecast_series: list[
        dict[str, Any]
    ] = []

    for period in forecast_periods:

        forecast_series.append(
            {
                "period": period,
                "revenue": average_revenue,
                "expenses": average_expenses,
                "net_result": (
                    average_net_result
                ),
            }
        )

    total_forecast_revenue = round(
        average_revenue
        * forecast_months,
        2,
    )

    total_forecast_expenses = round(
        average_expenses
        * forecast_months,
        2,
    )

    total_forecast_net_result = round(
        total_forecast_revenue
        - total_forecast_expenses,
        2,
    )

    confidence = _determine_confidence(
        history_month_count=len(
            history_used
        )
    )

    # --------------------------------------------------
    # Historical periods used
    # --------------------------------------------------

    history_periods = [
        str(record.get("period"))
        for record in history_used
    ]

    return {
        "status": "available",
        "forecast_type": "baseline",
        "methodology": (
            "historical_average_run_rate"
        ),
        "methodology_description": (
            "The forecast uses the average monthly revenue "
            "and expenses from recent validated historical "
            "periods. The latest observed month is excluded "
            "from the baseline to reduce the risk that a "
            "partial month distorts the forecast."
        ),
        "forecast_horizon_months": (
            forecast_months
        ),
        "history": {
            "observed_month_count": len(
                valid_months
            ),
            "baseline_month_count": len(
                history_used
            ),
            "baseline_periods": history_periods,
            "latest_observed_period": (
                latest_period
            ),
            "latest_period_excluded_from_baseline": (
                True
            ),
        },
        "baseline": {
            "average_monthly_revenue": (
                average_revenue
            ),
            "average_monthly_expenses": (
                average_expenses
            ),
            "average_monthly_net_result": (
                average_net_result
            ),
        },
        "forecast_series": forecast_series,
        "forecast_totals": {
            "revenue": total_forecast_revenue,
            "expenses": total_forecast_expenses,
            "net_result": (
                total_forecast_net_result
            ),
        },
        "confidence": confidence,
        "assumptions": [
            (
                "Recent historical operating patterns "
                "provide a reasonable baseline for the "
                "forecast horizon."
            ),
            (
                "No major structural change, exceptional "
                "event, new grant, grant closure, financing "
                "event, or other material change is assumed."
            ),
            (
                "The forecast is a baseline planning view "
                "and not a guaranteed future outcome."
            ),
        ],
        "cautions": [
            (
                "The model does not yet incorporate "
                "seasonality."
            ),
            (
                "The model does not yet incorporate budget "
                "forecast columns, expected grants, donor "
                "payment schedules, or management scenarios."
            ),
            (
                "The latest observed month is excluded from "
                "the baseline because it may represent a "
                "partial reporting period."
            ),
            (
                "Forecast results should be interpreted "
                "together with liquidity, budget, grant, "
                "risk, and management information."
            ),
        ],
    }


def _determine_confidence(
    history_month_count: int,
) -> dict[str, Any]:
    """
    Describe forecast data sufficiency.

    V1 deliberately does not assign High confidence because
    the baseline model does not yet account for seasonality,
    structural changes, grant schedules, or scenarios.
    """

    if history_month_count >= 6:

        level = "Medium"

        reason = (
            "The baseline uses at least six validated "
            "historical monthly periods, but the model does "
            "not yet incorporate seasonality or forward-"
            "looking operational drivers."
        )

    else:

        level = "Low"

        reason = (
            "The baseline is supported by only three to five "
            "validated historical monthly periods."
        )

    return {
        "level": level,
        "history_month_count": (
            history_month_count
        ),
        "reason": reason,
    }


def _future_months(
    latest_period: str,
    count: int,
) -> list[str]:
    """
    Generate future YYYY-MM forecast periods after the latest
    observed monthly period.
    """

    parsed = _parse_month(
        latest_period
    )

    if parsed is None:
        return []

    year, month = parsed

    periods: list[str] = []

    for _ in range(count):

        month += 1

        if month > 12:
            month = 1
            year += 1

        periods.append(
            f"{year:04d}-{month:02d}"
        )

    return periods


def _parse_month(
    value: Any,
) -> tuple[int, int] | None:

    if value is None:
        return None

    text = str(value).strip()

    parts = text.split("-")

    if len(parts) != 2:
        return None

    try:
        year = int(parts[0])
        month = int(parts[1])

    except ValueError:
        return None

    if year < 1:
        return None

    if month < 1 or month > 12:
        return None

    return year, month


def _is_valid_month_record(
    record: Any,
) -> bool:

    if not isinstance(
        record,
        dict,
    ):
        return False

    if _parse_month(
        record.get("period")
    ) is None:
        return False

    return True


def _normalize_positive_int(
    value: Any,
    default: int,
) -> int:

    try:
        result = int(value)

    except (
        TypeError,
        ValueError,
    ):
        return default

    if result < 1:
        return default

    return result


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