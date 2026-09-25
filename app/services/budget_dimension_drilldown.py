from collections import defaultdict
from typing import Any

from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)


DRILLDOWN_DIMENSIONS = {
    "fund": {
        "budget_fields": [
            "fund_code",
            "fund",
        ],
        "actual_fields": [
            "fund_code",
            "fund",
        ],
        "name_field": "fund_name",
    },
    "donor": {
        "budget_fields": [
            "donor_code",
            "donor",
        ],
        "actual_fields": [
            "donor_code",
            "donor",
        ],
        "name_field": "donor_name",
    },
    "program": {
        "budget_fields": [
            "program_code",
            "program",
        ],
        "actual_fields": [
            "program_code",
            "program",
        ],
        "name_field": "program_name",
    },
    "project": {
        "budget_fields": [
            "project_code",
            "project",
        ],
        "actual_fields": [
            "project_code",
            "project",
        ],
        "name_field": "project_name",
    },
    "category": {
        "budget_fields": [
            "category_code",
            "category",
        ],
        "actual_fields": [
            "category_code",
            "category",
        ],
        "name_field": "category_name",
    },
    "budget_line": {
        "budget_fields": [
            "budget_line_code",
        ],
        "actual_fields": [
            "budget_line_code",
            "budget_line",
        ],
        "name_field": "budget_line_name",
    },
    "donor_line": {
        "budget_fields": [
            "donor_line_code",
            "donor_line",
        ],
        "actual_fields": [
            "donor_line_code",
            "donor_line",
        ],
        "name_field": None,
    },
}


DRILLDOWN_PATHS = {
    "fund": [
        "program",
        "category",
        "budget_line",
        "donor_line",
    ],
    "donor": [
        "fund",
        "program",
        "category",
        "budget_line",
        "donor_line",
    ],
    "program": [
        "fund",
        "category",
        "budget_line",
        "donor_line",
    ],
    "project": [
        "fund",
        "program",
        "category",
        "budget_line",
        "donor_line",
    ],
    "category": [
        "fund",
        "program",
        "budget_line",
        "donor_line",
    ],
    "budget_line": [
        "fund",
        "program",
        "category",
        "donor_line",
    ],
    "donor_line": [
        "fund",
        "program",
        "category",
        "budget_line",
    ],
}


def generate_budget_dimension_drilldown(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build cross-dimensional Budget drill-down intelligence.

    This service uses the same Budget inputs and the same
    central Budget Actual classifier as Budget vs Actual.

    It does not replace the canonical Budget vs Actual
    engine. It builds relationships between dimensions so
    users can investigate which underlying dimensions are
    driving a selected Budget exception.
    """

    accounts_by_number = accounts_by_number or {}

    budget_transactions = _prepare_budget_transactions(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=accounts_by_number,
    )

    drilldown: dict[str, Any] = {}

    for parent_dimension, child_dimensions in (
        DRILLDOWN_PATHS.items()
    ):
        parent_records = _build_parent_records(
            budget_lines=budget_lines,
            transactions=budget_transactions,
            parent_dimension=parent_dimension,
            child_dimensions=child_dimensions,
        )

        if not parent_records:
            continue

        drilldown[parent_dimension] = {
            "dimension": parent_dimension,
            "record_count": len(parent_records),
            "records": parent_records,
        }

    return drilldown


def _prepare_budget_transactions(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    classifier = BudgetActualClassifier()

    budget_fund_codes = {
        _first_value(
            budget_line,
            DRILLDOWN_DIMENSIONS["fund"][
                "budget_fields"
            ],
        )
        for budget_line in budget_lines
    }

    budget_fund_codes.discard(None)

    prepared: list[dict[str, Any]] = []

    for transaction in transactions:
        transaction_fund = _first_value(
            transaction,
            DRILLDOWN_DIMENSIONS["fund"][
                "actual_fields"
            ],
        )

        if (
            budget_fund_codes
            and transaction_fund
            not in budget_fund_codes
        ):
            continue

        classification = classifier.classify(
            transaction=transaction,
            accounts_by_number=accounts_by_number,
        )

        if not classification[
            "is_budget_consuming"
        ]:
            continue

        prepared_transaction = dict(
            transaction
        )

        prepared_transaction[
            "budget_actual_amount"
        ] = classification[
            "budget_actual_amount"
        ]

        prepared_transaction[
            "budget_treatment"
        ] = classification[
            "budget_treatment"
        ]

        prepared_transaction[
            "is_closing_entry"
        ] = classification[
            "is_closing_entry"
        ]

        prepared.append(
            prepared_transaction
        )

    return prepared


def _build_parent_records(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    parent_dimension: str,
    child_dimensions: list[str],
) -> list[dict[str, Any]]:
    parent_config = (
        DRILLDOWN_DIMENSIONS[
            parent_dimension
        ]
    )

    parent_keys: set[str] = set()

    parent_names: dict[
        str,
        str | None,
    ] = {}

    for budget_line in budget_lines:
        parent_key = _first_value(
            budget_line,
            parent_config[
                "budget_fields"
            ],
        )

        if not parent_key:
            continue

        parent_keys.add(parent_key)

        name_field = parent_config[
            "name_field"
        ]

        if (
            name_field
            and parent_key
            not in parent_names
        ):
            parent_names[
                parent_key
            ] = _clean_text(
                budget_line.get(
                    name_field
                )
            )

    for transaction in transactions:
        parent_key = _first_value(
            transaction,
            parent_config[
                "actual_fields"
            ],
        )

        if parent_key:
            parent_keys.add(
                parent_key
            )

    records: list[dict[str, Any]] = []

    for parent_key in sorted(
        parent_keys
    ):
        child_views: dict[str, Any] = {}

        for child_dimension in (
            child_dimensions
        ):
            child_view = (
                _build_child_view(
                    budget_lines=budget_lines,
                    transactions=transactions,
                    parent_dimension=parent_dimension,
                    parent_key=parent_key,
                    child_dimension=child_dimension,
                )
            )

            if child_view["lines"]:
                child_views[
                    child_dimension
                ] = child_view

        if not child_views:
            continue

        records.append(
            {
                "code": parent_key,
                "name": parent_names.get(
                    parent_key
                ),
                "drilldown": child_views,
            }
        )

    return records


def _build_child_view(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    parent_dimension: str,
    parent_key: str,
    child_dimension: str,
) -> dict[str, Any]:
    parent_config = (
        DRILLDOWN_DIMENSIONS[
            parent_dimension
        ]
    )

    child_config = (
        DRILLDOWN_DIMENSIONS[
            child_dimension
        ]
    )

    budget_by_child: dict[
        str,
        float,
    ] = defaultdict(float)

    actual_by_child: dict[
        str,
        float,
    ] = defaultdict(float)

    names: dict[
        str,
        str | None,
    ] = {}

    for budget_line in budget_lines:
        current_parent = _first_value(
            budget_line,
            parent_config[
                "budget_fields"
            ],
        )

        if current_parent != parent_key:
            continue

        child_key = _first_value(
            budget_line,
            child_config[
                "budget_fields"
            ],
        )

        if not child_key:
            child_key = "__UNASSIGNED__"
            names[child_key] = "Unassigned"

        budget_by_child[
            child_key
        ] += _get_budget_amount(
            budget_line
        )

        name_field = child_config[
            "name_field"
        ]

        if (
            name_field
            and child_key
            not in names
        ):
            names[
                child_key
            ] = _clean_text(
                budget_line.get(
                    name_field
                )
            )

    for transaction in transactions:
        current_parent = _first_value(
            transaction,
            parent_config[
                "actual_fields"
            ],
        )

        if current_parent != parent_key:
            continue

        child_key = _first_value(
            transaction,
            child_config[
                "actual_fields"
            ],
        )

        if not child_key:
            child_key = "__UNASSIGNED__"
            names[child_key] = "Unassigned"

        actual_by_child[
            child_key
        ] += _get_actual_amount(
            transaction
        )

    all_child_keys = sorted(
        set(budget_by_child)
        | set(actual_by_child)
    )

    lines: list[
        dict[str, Any]
    ] = []

    for child_key in all_child_keys:
        budget = budget_by_child.get(
            child_key,
            0.0,
        )

        actual = actual_by_child.get(
            child_key,
            0.0,
        )

        variance = budget - actual

        utilization = (
            actual / budget * 100
            if budget
            else None
        )

        status = _get_status(
            budget=budget,
            actual=actual,
        )

        lines.append(
            {
                "code": child_key,
                "name": names.get(
                    child_key
                ),
                "budget": round(
                    budget,
                    2,
                ),
                "actual": round(
                    actual,
                    2,
                ),
                "variance": round(
                    variance,
                    2,
                ),
                "utilization_percentage": (
                    round(
                        utilization,
                        2,
                    )
                    if utilization
                    is not None
                    else None
                ),
                "status": status,
            }
        )

    return {
        "dimension": child_dimension,
        "summary": _build_summary(
            lines
        ),
        "lines": lines,
    }


def _build_summary(
    lines: list[dict[str, Any]],
) -> dict[str, Any]:
    total_budget = sum(
        float(
            line.get(
                "budget"
            )
            or 0
        )
        for line in lines
    )

    total_actual = sum(
        float(
            line.get(
                "actual"
            )
            or 0
        )
        for line in lines
    )

    return {
        "total_budget": round(
            total_budget,
            2,
        ),
        "total_actual": round(
            total_actual,
            2,
        ),
        "total_variance": round(
            total_budget
            - total_actual,
            2,
        ),
        "line_count": len(lines),
        "over_budget_count": sum(
            line.get("status")
            == "Over Budget"
            for line in lines
        ),
        "within_budget_count": sum(
            line.get("status")
            == "Within Budget"
            for line in lines
        ),
        "no_budget_count": sum(
            line.get("status")
            == "No Budget"
            for line in lines
        ),
    }


def _get_budget_amount(
    budget_line: dict[str, Any],
) -> float:
    for field_name in [
        "current_budget",
        "revised_budget",
        "original_budget",
    ]:
        value = budget_line.get(
            field_name
        )

        if not _is_blank(value):
            return _to_float(value)

    return 0.0


def _get_actual_amount(
    transaction: dict[str, Any],
) -> float:
    classified_amount = (
        transaction.get(
            "budget_actual_amount"
        )
    )

    if classified_amount is not None:
        return _to_float(
            classified_amount
        )

    debit = _first_numeric(
        transaction,
        [
            "debit_amount",
            "debit",
        ],
    )

    credit = _first_numeric(
        transaction,
        [
            "credit_amount",
            "credit",
        ],
    )

    if (
        debit is not None
        or credit is not None
    ):
        return (
            debit or 0.0
        ) - (
            credit or 0.0
        )

    amount = _first_numeric(
        transaction,
        ["amount"],
    )

    return amount or 0.0


def _get_status(
    budget: float,
    actual: float,
) -> str:
    if (
        abs(budget) < 0.01
        and abs(actual) >= 0.01
    ):
        return "No Budget"

    if actual > budget:
        return "Over Budget"

    return "Within Budget"


def _first_value(
    record: dict[str, Any],
    fields: list[str],
) -> str | None:
    for field_name in fields:
        cleaned = _clean_text(
            record.get(
                field_name
            )
        )

        if cleaned:
            return cleaned

    return None


def _first_numeric(
    record: dict[str, Any],
    fields: list[str],
) -> float | None:
    for field_name in fields:
        value = record.get(
            field_name
        )

        if _is_blank(value):
            continue

        return _to_float(value)

    return None


def _clean_text(
    value: Any,
) -> str | None:
    if value is None:
        return None

    cleaned = str(
        value
    ).strip()

    if not cleaned:
        return None

    if cleaned.lower() in {
        "none",
        "null",
        "nan",
    }:
        return None

    return cleaned


def _is_blank(
    value: Any,
) -> bool:
    if value is None:
        return True

    if isinstance(
        value,
        str,
    ):
        return not value.strip()

    return False


def _to_float(
    value: Any,
) -> float:
    if value is None:
        return 0.0

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    text = (
        str(value)
        .replace(",", "")
        .replace("$", "")
        .strip()
    )

    if not text:
        return 0.0

    if (
        text.startswith("(")
        and text.endswith(")")
    ):
        text = (
            "-"
            + text[1:-1]
        )

    try:
        return float(text)

    except ValueError:
        return 0.0