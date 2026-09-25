from __future__ import annotations

from typing import Any


def generate_funding_scenario(
    expected_funding_intelligence: dict[str, Any] | None,
    scenario_name: str,
    expected_funding_change_percentage: float = 0.0,
    failed_expected_funding_codes: list[str] | None = None,
    scenario_basis: str = "most_likely",
) -> dict[str, Any]:
    """
    Generate a deterministic Expected Funding scenario.

    Expected Funding remains prospective only and is not
    automatically treated as secured funding, revenue,
    available budget, or cash.
    """

    if (
        not expected_funding_intelligence
        or expected_funding_intelligence.get("status")
        != "available"
    ):
        return {
            "status": "not_available",
            "scenario_name": scenario_name,
        }

    summary = (
        expected_funding_intelligence.get("summary")
        or {}
    )

    records = (
        expected_funding_intelligence.get("records")
        or []
    )

    baseline_minimum = _optional_float(
        summary.get("minimum_pipeline_value")
    )

    baseline_most_likely = _optional_float(
        summary.get("most_likely_pipeline_value")
    )

    baseline_maximum = _optional_float(
        summary.get("maximum_pipeline_value")
    )

    baseline_weighted = _optional_float(
        summary.get(
            "probability_weighted_expected_funding"
        )
    )

    failed_codes = {
        str(code).strip()
        for code in (
            failed_expected_funding_codes or []
        )
        if str(code).strip()
    }

    failed_minimum = 0.0
    failed_most_likely = 0.0
    failed_maximum = 0.0
    failed_weighted = 0.0

    for record in records:
        if not isinstance(record, dict):
            continue

        code = str(
            record.get("expected_funding_code")
            or ""
        ).strip()

        if code not in failed_codes:
            continue

        failed_minimum += (
            _optional_float(
                record.get("minimum_amount")
            )
            or 0.0
        )

        failed_most_likely += (
            _optional_float(
                record.get("most_likely_amount")
            )
            or 0.0
        )

        failed_maximum += (
            _optional_float(
                record.get("maximum_amount")
            )
            or 0.0
        )

        failed_weighted += (
            _optional_float(
                record.get(
                    "probability_weighted_amount"
                )
            )
            or 0.0
        )

    change_factor = (
        1.0
        + (
            float(expected_funding_change_percentage)
            / 100.0
        )
    )

    scenario_minimum = _scenario_value(
        baseline_minimum,
        failed_minimum,
        change_factor,
    )

    scenario_most_likely = _scenario_value(
        baseline_most_likely,
        failed_most_likely,
        change_factor,
    )

    scenario_maximum = _scenario_value(
        baseline_maximum,
        failed_maximum,
        change_factor,
    )

    scenario_weighted = _scenario_value(
        baseline_weighted,
        failed_weighted,
        change_factor,
    )

    basis_values = {
        "minimum": scenario_minimum,
        "most_likely": scenario_most_likely,
        "maximum": scenario_maximum,
        "probability_weighted": scenario_weighted,
    }

    selected_pipeline_value = basis_values.get(
        scenario_basis,
        scenario_most_likely,
    )

    return {
        "status": "available",
        "scenario_name": scenario_name,
        "scenario_basis": scenario_basis,
        "baseline": {
            "minimum_pipeline_value": baseline_minimum,
            "most_likely_pipeline_value": (
                baseline_most_likely
            ),
            "maximum_pipeline_value": baseline_maximum,
            "probability_weighted_expected_funding": (
                baseline_weighted
            ),
        },
        "scenario": {
            "minimum_pipeline_value": scenario_minimum,
            "most_likely_pipeline_value": (
                scenario_most_likely
            ),
            "maximum_pipeline_value": scenario_maximum,
            "probability_weighted_expected_funding": (
                scenario_weighted
            ),
            "selected_pipeline_value": (
                selected_pipeline_value
            ),
        },
        "impact": {
            "minimum_pipeline_variance": _variance(
                scenario_minimum,
                baseline_minimum,
            ),
            "most_likely_pipeline_variance": _variance(
                scenario_most_likely,
                baseline_most_likely,
            ),
            "maximum_pipeline_variance": _variance(
                scenario_maximum,
                baseline_maximum,
            ),
            "probability_weighted_variance": _variance(
                scenario_weighted,
                baseline_weighted,
            ),
        },
        "assumptions": {
            "expected_funding_change_percentage": (
                float(
                    expected_funding_change_percentage
                )
            ),
            "failed_expected_funding_codes": sorted(
                failed_codes
            ),
        },
        "controls": {
            "prospective_funding_only": True,
            "treated_as_secured_funding": False,
            "treated_as_revenue": False,
            "treated_as_cash": False,
            "financial_recalculation_performed": False,
        },
    }


def _scenario_value(
    baseline: float | None,
    failed_amount: float,
    change_factor: float,
) -> float | None:

    if baseline is None:
        return None

    remaining = baseline - failed_amount

    return round(
        remaining * change_factor,
        2,
    )


def _variance(
    scenario: float | None,
    baseline: float | None,
) -> float | None:

    if scenario is None or baseline is None:
        return None

    return round(
        scenario - baseline,
        2,
    )


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