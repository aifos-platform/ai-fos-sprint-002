from app.services.financial_forecast import (
    generate_financial_forecast,
)


def _trend_data() -> dict:
    return {
        "status": "available",
        "monthly_series": [
            {
                "period": "2026-01",
                "revenue": 1000.0,
                "expenses": 700.0,
                "net_result": 300.0,
            },
            {
                "period": "2026-02",
                "revenue": 1100.0,
                "expenses": 720.0,
                "net_result": 380.0,
            },
            {
                "period": "2026-03",
                "revenue": 1200.0,
                "expenses": 740.0,
                "net_result": 460.0,
            },
            {
                "period": "2026-04",
                "revenue": 1300.0,
                "expenses": 760.0,
                "net_result": 540.0,
            },
            {
                "period": "2026-05",
                "revenue": 1400.0,
                "expenses": 780.0,
                "net_result": 620.0,
            },
            {
                "period": "2026-06",
                "revenue": 1500.0,
                "expenses": 800.0,
                "net_result": 700.0,
            },
            {
                "period": "2026-07",
                "revenue": 1600.0,
                "expenses": 820.0,
                "net_result": 780.0,
            },
        ],
    }


def test_forecast_uses_recent_historical_baseline():
    result = generate_financial_forecast(
        financial_trends=_trend_data(),
        forecast_months=3,
        baseline_months=6,
    )

    assert result["status"] == "available"

    baseline = result["baseline"]

    assert baseline["average_monthly_revenue"] == 1250.0
    assert baseline["average_monthly_expenses"] == 750.0
    assert baseline["average_monthly_net_result"] == 500.0


def test_latest_observed_month_is_excluded_from_baseline():
    result = generate_financial_forecast(
        financial_trends=_trend_data(),
        forecast_months=3,
        baseline_months=6,
    )

    history = result["history"]

    assert history["latest_observed_period"] == "2026-07"
    assert history["latest_period_excluded_from_baseline"] is True

    assert history["baseline_periods"] == [
        "2026-01",
        "2026-02",
        "2026-03",
        "2026-04",
        "2026-05",
        "2026-06",
    ]


def test_forecast_generates_future_months():
    result = generate_financial_forecast(
        financial_trends=_trend_data(),
        forecast_months=3,
    )

    periods = [
        row["period"]
        for row in result["forecast_series"]
    ]

    assert periods == [
        "2026-08",
        "2026-09",
        "2026-10",
    ]


def test_forecast_totals_match_monthly_baseline():
    result = generate_financial_forecast(
        financial_trends=_trend_data(),
        forecast_months=3,
        baseline_months=6,
    )

    totals = result["forecast_totals"]

    assert totals["revenue"] == 3750.0
    assert totals["expenses"] == 2250.0
    assert totals["net_result"] == 1500.0


def test_forecast_confidence_is_medium_with_six_baseline_months():
    result = generate_financial_forecast(
        financial_trends=_trend_data(),
        baseline_months=6,
    )

    confidence = result["confidence"]

    assert confidence["level"] == "Medium"
    assert confidence["history_month_count"] == 6


def test_forecast_confidence_is_low_with_three_baseline_months():
    trends = {
        "monthly_series": [
            {
                "period": "2026-01",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-02",
                "revenue": 1100.0,
                "expenses": 720.0,
            },
            {
                "period": "2026-03",
                "revenue": 1200.0,
                "expenses": 740.0,
            },
            {
                "period": "2026-04",
                "revenue": 1300.0,
                "expenses": 760.0,
            },
        ],
    }

    result = generate_financial_forecast(
        financial_trends=trends,
        baseline_months=6,
    )

    assert result["status"] == "available"
    assert result["confidence"]["level"] == "Low"
    assert result["confidence"]["history_month_count"] == 3


def test_forecast_requires_four_observed_months():
    trends = {
        "monthly_series": [
            {
                "period": "2026-01",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-02",
                "revenue": 1100.0,
                "expenses": 720.0,
            },
            {
                "period": "2026-03",
                "revenue": 1200.0,
                "expenses": 740.0,
            },
        ],
    }

    result = generate_financial_forecast(
        financial_trends=trends,
    )

    assert result["status"] == "not_available"
    assert result["forecast_series"] == []
    assert result["history"]["observed_month_count"] == 3


def test_invalid_month_records_are_ignored():
    trends = {
        "monthly_series": [
            {
                "period": "not-a-month",
                "revenue": 999999.0,
                "expenses": 999999.0,
            },
            {
                "period": "2026-01",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-02",
                "revenue": 1100.0,
                "expenses": 720.0,
            },
            {
                "period": "2026-03",
                "revenue": 1200.0,
                "expenses": 740.0,
            },
            {
                "period": "2026-04",
                "revenue": 1300.0,
                "expenses": 760.0,
            },
        ],
    }

    result = generate_financial_forecast(
        financial_trends=trends,
    )

    assert result["status"] == "available"
    assert result["history"]["observed_month_count"] == 4


def test_forecast_handles_year_rollover():
    trends = {
        "monthly_series": [
            {
                "period": "2026-08",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-09",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-10",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-11",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
            {
                "period": "2026-12",
                "revenue": 1000.0,
                "expenses": 700.0,
            },
        ],
    }

    result = generate_financial_forecast(
        financial_trends=trends,
        forecast_months=3,
    )

    periods = [
        row["period"]
        for row in result["forecast_series"]
    ]

    assert periods == [
        "2027-01",
        "2027-02",
        "2027-03",
    ]


def test_forecast_exposes_methodology_and_cautions():
    result = generate_financial_forecast(
        financial_trends=_trend_data(),
    )

    assert (
        result["methodology"]
        == "historical_average_run_rate"
    )

    assert result["forecast_type"] == "baseline"

    assert len(result["assumptions"]) > 0
    assert len(result["cautions"]) > 0

    caution_text = " ".join(
        result["cautions"]
    ).lower()

    assert "seasonality" in caution_text
    assert "latest observed month" in caution_text