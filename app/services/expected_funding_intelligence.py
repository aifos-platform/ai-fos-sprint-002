from __future__ import annotations

from typing import Any


def generate_expected_funding_intelligence(
    expected_funding_lines: list[
        dict[str, Any]
    ] | None,
) -> dict[str, Any]:
    """
    Build deterministic Expected Funding Intelligence.

    Expected Funding represents prospective funding only.

    It must never be treated automatically as:
    - secured funding;
    - available budget;
    - recognized revenue;
    - available cash.

    Probability-weighted expected funding is calculated
    only when both:
    - a valid probability percentage exists; and
    - a most-likely amount exists.

    Missing probability is intentionally preserved as
    missing and is never silently interpreted as 0%.
    """

    expected_funding_lines = (
        expected_funding_lines or []
    )

    valid_records = [
        record
        for record in expected_funding_lines
        if isinstance(
            record,
            dict,
        )
    ]

    if not valid_records:
        return {
            "status": "not_available",
            "summary": {
                "record_count": 0,
                "record_count_requiring_review": 0,
                "minimum_pipeline_value": None,
                "most_likely_pipeline_value": None,
                "maximum_pipeline_value": None,
                "probability_weighted_expected_funding": None,
                "weighted_record_count": 0,
            },
            "by_stage": [],
            "by_donor": [],
            "records": [],
            "controls": {
                "prospective_funding_only": True,
                "treated_as_secured_funding": False,
                "financial_recalculation_performed": False,
            },
        }

    minimum_pipeline_value = 0.0
    most_likely_pipeline_value = 0.0
    maximum_pipeline_value = 0.0

    minimum_record_count = 0
    most_likely_record_count = 0
    maximum_record_count = 0

    probability_weighted_total = 0.0
    weighted_record_count = 0

    record_count_requiring_review = 0

    stage_totals: dict[
        str,
        dict[str, Any],
    ] = {}

    donor_totals: dict[
        str,
        dict[str, Any],
    ] = {}

    intelligence_records: list[
        dict[str, Any]
    ] = []

    for record in valid_records:

        requires_review = bool(
            record.get(
                "requires_review"
            )
        )

        if requires_review:
            record_count_requiring_review += 1

        minimum_amount = _optional_float(
            record.get(
                "minimum_amount"
            )
        )

        most_likely_amount = _optional_float(
            record.get(
                "most_likely_amount"
            )
        )

        maximum_amount = _optional_float(
            record.get(
                "maximum_amount"
            )
        )

        probability_percentage = _optional_float(
            record.get(
                "probability_percentage"
            )
        )

        if minimum_amount is not None:
            minimum_pipeline_value += (
                minimum_amount
            )
            minimum_record_count += 1

        if most_likely_amount is not None:
            most_likely_pipeline_value += (
                most_likely_amount
            )
            most_likely_record_count += 1

        if maximum_amount is not None:
            maximum_pipeline_value += (
                maximum_amount
            )
            maximum_record_count += 1

        weighted_expected_amount: float | None = None

        if (
            probability_percentage is not None
            and 0
            <= probability_percentage
            <= 100
            and most_likely_amount is not None
        ):
            weighted_expected_amount = round(
                most_likely_amount
                * probability_percentage
                / 100,
                2,
            )

            probability_weighted_total += (
                weighted_expected_amount
            )

            weighted_record_count += 1

        stage = (
            _clean_text(
                record.get(
                    "stage"
                )
            )
            or "Unspecified"
        )

        donor_code = _clean_text(
            record.get(
                "donor_code"
            )
        )

        donor_name = _clean_text(
            record.get(
                "donor_name"
            )
        )

        donor_key = (
            donor_code
            or donor_name
            or "Unspecified"
        )

        _accumulate_group(
            groups=stage_totals,
            key=stage,
            most_likely_amount=(
                most_likely_amount
            ),
            weighted_expected_amount=(
                weighted_expected_amount
            ),
        )

        _accumulate_group(
            groups=donor_totals,
            key=donor_key,
            most_likely_amount=(
                most_likely_amount
            ),
            weighted_expected_amount=(
                weighted_expected_amount
            ),
        )

        intelligence_record = dict(
            record
        )

        intelligence_record[
            "probability_weighted_amount"
        ] = (
            weighted_expected_amount
        )

        intelligence_records.append(
            intelligence_record
        )

    return {
        "status": "available",
        "summary": {
            "record_count": len(
                valid_records
            ),
            "record_count_requiring_review": (
                record_count_requiring_review
            ),
            "minimum_pipeline_value": (
                round(
                    minimum_pipeline_value,
                    2,
                )
                if minimum_record_count > 0
                else None
            ),
            "most_likely_pipeline_value": (
                round(
                    most_likely_pipeline_value,
                    2,
                )
                if most_likely_record_count > 0
                else None
            ),
            "maximum_pipeline_value": (
                round(
                    maximum_pipeline_value,
                    2,
                )
                if maximum_record_count > 0
                else None
            ),
            "probability_weighted_expected_funding": (
                round(
                    probability_weighted_total,
                    2,
                )
                if weighted_record_count > 0
                else None
            ),
            "weighted_record_count": (
                weighted_record_count
            ),
        },
        "by_stage": _group_list(
            stage_totals
        ),
        "by_donor": _group_list(
            donor_totals
        ),
        "records": intelligence_records,
        "methodology": (
            "probability_weighted_expected_funding"
        ),
        "methodology_description": (
            "Expected Funding Intelligence summarizes "
            "prospective funding records. Probability-"
            "weighted funding is calculated from the "
            "most-likely amount multiplied by the "
            "explicit probability percentage when both "
            "values are available and valid."
        ),
        "controls": {
            "prospective_funding_only": True,
            "treated_as_secured_funding": False,
            "financial_recalculation_performed": False,
            "missing_probability_preserved": True,
            "expected_funding_not_assumed_revenue": True,
            "expected_funding_not_assumed_cash": True,
        },
        "cautions": [
            (
                "Expected funding is prospective and "
                "must not be interpreted as secured "
                "funding."
            ),
            (
                "Probability-weighted expected funding "
                "is a scenario-weighted management "
                "estimate, not guaranteed funding."
            ),
            (
                "Expected funding is not automatically "
                "treated as revenue or cash."
            ),
        ],
    }


def _accumulate_group(
    groups: dict[
        str,
        dict[str, Any],
    ],
    key: str,
    most_likely_amount: float | None,
    weighted_expected_amount: float | None,
) -> None:

    if key not in groups:
        groups[key] = {
            "name": key,
            "record_count": 0,
            "most_likely_pipeline_value": 0.0,
            "most_likely_record_count": 0,
            "probability_weighted_expected_funding": 0.0,
            "weighted_record_count": 0,
        }

    group = groups[key]

    group[
        "record_count"
    ] += 1

    if most_likely_amount is not None:
        group[
            "most_likely_pipeline_value"
        ] += most_likely_amount

        group[
            "most_likely_record_count"
        ] += 1

    if weighted_expected_amount is not None:
        group[
            "probability_weighted_expected_funding"
        ] += weighted_expected_amount

        group[
            "weighted_record_count"
        ] += 1


def _group_list(
    groups: dict[
        str,
        dict[str, Any],
    ],
) -> list[dict[str, Any]]:

    result: list[
        dict[str, Any]
    ] = []

    for key in sorted(
        groups
    ):

        group = groups[key]

        result.append(
            {
                "name": group[
                    "name"
                ],
                "record_count": group[
                    "record_count"
                ],
                "most_likely_pipeline_value": (
                    round(
                        group[
                            "most_likely_pipeline_value"
                        ],
                        2,
                    )
                    if group[
                        "most_likely_record_count"
                    ] > 0
                    else None
                ),
                "probability_weighted_expected_funding": (
                    round(
                        group[
                            "probability_weighted_expected_funding"
                        ],
                        2,
                    )
                    if group[
                        "weighted_record_count"
                    ] > 0
                    else None
                ),
                "weighted_record_count": group[
                    "weighted_record_count"
                ],
            }
        )

    return result


def _optional_float(
    value: Any,
) -> float | None:

    if value in {
        None,
        "",
    }:
        return None

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def _clean_text(
    value: Any,
) -> str | None:

    if value is None:
        return None

    text = str(
        value
    ).strip()

    if not text:
        return None

    if text.lower() in {
        "none",
        "null",
        "nan",
    }:
        return None

    return text