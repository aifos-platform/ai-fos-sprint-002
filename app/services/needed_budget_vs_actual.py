from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)


def generate_needed_budget_vs_actual(
    needed_budget_lines: list[dict[str, Any]],
    available_budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[
        str,
        dict[str, Any],
    ]
    | None = None,
) -> dict[str, Any]:

    """
    Build AI-FOS Needed Budget vs Actual analysis.

    Needed Budget represents what an organisation
    requires financially for a fiscal period.

    It is intentionally independent from:
    - Fund
    - Donor
    - Donor Line
    - Grant

    Actual expenditure is determined by the central
    BudgetActualClassifier so Budget and Needed Budget
    analysis use the same spending treatment.
    """

    accounts_by_number = (
        accounts_by_number or {}
    )

    classifier = (
        BudgetActualClassifier()
    )

    available_budget_line_codes = {
        str(
            line.get("budget_line_code")
            or ""
        ).strip()
        for line in available_budget_lines
        if str(
            line.get("budget_line_code")
            or ""
        ).strip()
    }    

    needed_budget_years = {
        int(line.get("fiscal_year"))
        for line in needed_budget_lines
        if line.get("fiscal_year") is not None
    }    

    budget_transactions: list[
        dict[str, Any]
    ] = []

    for transaction in transactions:

        transaction_year = transaction.get(
            "fiscal_year"
        )

        if transaction_year is None:
            posting_date = (
                transaction.get("posting_date")
                or transaction.get("transaction_date")
            )

            transaction_year = _extract_year(
                posting_date
            )

        try:
            transaction_year = (
                int(transaction_year)
                if transaction_year is not None
                else None
            )
        except (TypeError, ValueError):
            transaction_year = None

        if (
            needed_budget_years
            and transaction_year not in needed_budget_years
        ):
            continue        

        classification = (
            classifier.classify(
                transaction=transaction,
                accounts_by_number=(
                    accounts_by_number
                ),
            )
        )

        if not classification.get(
            "is_budget_consuming",
            False,
        ):
            continue

        classified_transaction = dict(
            transaction
        )

        classified_transaction[
            "budget_actual_amount"
        ] = classification.get(
            "budget_actual_amount",
            0.0,
        )

        classified_transaction[
            "budget_treatment"
        ] = classification.get(
            "budget_treatment"
        )

        classified_transaction[
            "is_closing_entry"
        ] = classification.get(
            "is_closing_entry",
            False,
        )

        budget_transactions.append(
            classified_transaction
        )

        detailed = (
            _generate_detailed_view(
                needed_budget_lines=(
                    needed_budget_lines
                ),
                transactions=(
                    budget_transactions
                ),
            )
        )        

    by_budget_line = (
        _generate_dimension_view(
            needed_budget_lines=(
                needed_budget_lines
            ),
            transactions=(
                budget_transactions
            ),
            dimension_name="budget_line",
            budget_fields=[
                "budget_line_code",
            ],
            actual_fields=[
                "budget_line_code",
                "budget_line",
            ],
            name_field="budget_line_name",
            available_budget_line_codes=(
                available_budget_line_codes
            ),
        )
    )

    by_program = (
        _generate_dimension_view(
            needed_budget_lines=(
                needed_budget_lines
            ),
            transactions=(
                budget_transactions
            ),
            dimension_name="program",
            budget_fields=[
                "program_code",
                "program",
            ],
            actual_fields=[
                "program_code",
                "program",
            ],
            name_field="program_name",
        )
    )

    by_category = (
        _generate_dimension_view(
            needed_budget_lines=(
                needed_budget_lines
            ),
            transactions=(
                budget_transactions
            ),
            dimension_name="category",
            budget_fields=[
                "category_code",
                "category",
            ],
            actual_fields=[
                "category_code",
                "category",
            ],
            name_field="category_name",
        )
    )

    by_fiscal_year = (
        _generate_fiscal_year_view(
            needed_budget_lines=(
                needed_budget_lines
            ),
            transactions=(
                budget_transactions
            ),
        )
    )

    return {
        "summary": (
            by_budget_line[
                "summary"
            ]
        ),
        "lines": (
            by_budget_line[
                "lines"
            ]
        ),
        "detailed": (
            detailed
        ), 
        "by_budget_line": (
            by_budget_line
        ),
        "by_program": (
            by_program
        ),
        "by_category": (
            by_category
        ),
        "by_fiscal_year": (
            by_fiscal_year
        ),
    }

def _generate_detailed_view(
    needed_budget_lines: list[
        dict[str, Any]
    ],
    transactions: list[
        dict[str, Any]
    ],
) -> dict[str, Any]:
    """
    Build detailed Needed Budget vs Actual records
    while preserving the dimensional identity of each
    requirement.

    This view is intended for downstream engines such
    as Funding Gap, which need the relationship between
    fiscal year, program, category, budget line,
    project, and other available dimensions.

    Unlike the reporting views, this function does not
    aggregate requirements into a single dimension.

    The current Needed Budget dataset may contain a
    second, less-detailed representation of the same
    requirement without Budget Line. The detailed view
    keeps the richer Budget-Line record so the same
    financial need is not counted twice.
    """

    actual_by_key: dict[
        tuple[Any, ...],
        float,
    ] = defaultdict(
        float
    )

    dimension_fields = (
        "fiscal_year",
        "program_code",
        "category_code",
        "budget_line_code",
        "project_code",
    )

    #
    # Aggregate GL actuals using the same composite
    # dimensional identity as the Needed Budget.
    #
    for transaction in transactions:

        fiscal_year = transaction.get(
            "fiscal_year"
        )

        if fiscal_year is None:

            posting_date = (
                transaction.get(
                    "posting_date"
                )
                or transaction.get(
                    "transaction_date"
                )
            )

            fiscal_year = _extract_year(
                posting_date
            )

        try:
            fiscal_year = (
                int(fiscal_year)
                if fiscal_year is not None
                else None
            )

        except (
            TypeError,
            ValueError,
        ):
            fiscal_year = None

        key = (
            fiscal_year,

            _clean_text(
                transaction.get(
                    "program_code"
                )
                or transaction.get(
                    "program"
                )
            ),

            _clean_text(
                transaction.get(
                    "category_code"
                )
                or transaction.get(
                    "category"
                )
            ),

            _clean_text(
                transaction.get(
                    "budget_line_code"
                )
                or transaction.get(
                    "budget_line"
                )
            ),

            _clean_text(
                transaction.get(
                    "project_code"
                )
                or transaction.get(
                    "project"
                )
            ),
        )

        actual_by_key[
            key
        ] += _get_actual_amount(
            transaction
        )

    detailed_lines: list[
        dict[str, Any]
    ] = []

    total_needed_budget = 0.0
    total_actual = 0.0
    total_remaining_requirement = 0.0

    for needed_line in needed_budget_lines:

        budget_line_code = _clean_text(
            needed_line.get(
                "budget_line_code"
            )
            or needed_line.get(
                "budget_line"
            )
        )

        #
        # The current canonical Needed Budget dataset
        # contains a second, less-detailed
        # representation of the same requirement
        # without Budget Line.
        #
        # Keep only the richer dimensional record in
        # this detailed view so the same need is not
        # counted twice.
        #
        if not budget_line_code:
            continue

        fiscal_year = needed_line.get(
            "fiscal_year"
        )

        try:
            fiscal_year = (
                int(fiscal_year)
                if fiscal_year is not None
                else None
            )

        except (
            TypeError,
            ValueError,
        ):
            fiscal_year = None

        program_code = _clean_text(
            needed_line.get(
                "program_code"
            )
            or needed_line.get(
                "program"
            )
        )

        category_code = _clean_text(
            needed_line.get(
                "category_code"
            )
            or needed_line.get(
                "category"
            )
        )

        project_code = _clean_text(
            needed_line.get(
                "project_code"
            )
            or needed_line.get(
                "project"
            )
        )

        key = (
            fiscal_year,
            program_code,
            category_code,
            budget_line_code,
            project_code,
        )

        needed_budget = (
            _get_needed_budget_amount(
                needed_line
            )
        )

        actual = (
            actual_by_key.get(
                key,
                0.0,
            )
        )

        remaining_requirement = (
            needed_budget
            - actual
        )

        utilization_percentage = (
            actual
            / needed_budget
            * 100
            if needed_budget
            else None
        )

        status = (
            _get_needed_budget_status(
                needed_budget=(
                    needed_budget
                ),
                actual=actual,
            )
        )

        detailed_lines.append(
            {
                "fiscal_year": (
                    fiscal_year
                ),

                "program_code": (
                    program_code
                ),

                "program_name": (
                    _clean_text(
                        needed_line.get(
                            "program_name"
                        )
                    )
                ),

                "category_code": (
                    category_code
                ),

                "category_name": (
                    _clean_text(
                        needed_line.get(
                            "category_name"
                        )
                    )
                ),

                "budget_line_code": (
                    budget_line_code
                ),

                "budget_line_name": (
                    _clean_text(
                        needed_line.get(
                            "budget_line_name"
                        )
                    )
                ),

                "project_code": (
                    project_code
                ),

                "project_name": (
                    _clean_text(
                        needed_line.get(
                            "project_name"
                        )
                    )
                ),

                "needed_budget": round(
                    needed_budget,
                    2,
                ),

                "actual": round(
                    actual,
                    2,
                ),

                "remaining_requirement": (
                    round(
                        remaining_requirement,
                        2,
                    )
                ),

                "utilization_percentage": (
                    round(
                        utilization_percentage,
                        2,
                    )
                    if utilization_percentage
                    is not None
                    else None
                ),

                "status": (
                    status
                ),

                "budget_notes": (
                    needed_line.get(
                        "budget_notes"
                    )
                ),

                "employee_responsible": (
                    needed_line.get(
                        "employee_responsible"
                    )
                ),

                "requires_review": (
                    needed_line.get(
                        "requires_review",
                        False,
                    )
                ),

                "review_reasons": (
                    needed_line.get(
                        "review_reasons",
                        [],
                    )
                ),
            }
        )

        total_needed_budget += (
            needed_budget
        )

        total_actual += (
            actual
        )

        total_remaining_requirement += (
            remaining_requirement
        )

    return {
        "dimension": (
            "detailed_requirement"
        ),

        "matching_dimensions": list(
            dimension_fields
        ),

        "summary": {
            "total_needed_budget": round(
                total_needed_budget,
                2,
            ),

            "total_actual": round(
                total_actual,
                2,
            ),

            "remaining_requirement": round(
                total_remaining_requirement,
                2,
            ),

            "line_count": len(
                detailed_lines
            ),
        },

        "lines": (
            detailed_lines
        ),
    }

def _generate_dimension_view(
    needed_budget_lines: list[
        dict[str, Any]
    ],
    transactions: list[
        dict[str, Any]
    ],
    dimension_name: str,
    budget_fields: list[str],
    actual_fields: list[str],
    name_field: str | None,
    available_budget_line_codes: set[str] | None = None,
) -> dict[str, Any]:

    available_budget_line_codes = (
        available_budget_line_codes or set()
    )

    budget_by_key: dict[
        str,
        float,
    ] = defaultdict(
        float
    )

    actual_by_key: dict[
        str,
        float,
    ] = defaultdict(
        float
    )

    names: dict[
        str,
        str | None,
    ] = {}

    #
    # Needed Budget side
    #
    for budget_line in needed_budget_lines:

        key = _first_value(
            budget_line,
            budget_fields,
        )

        if not key:
            continue

        budget_amount = (
            _get_needed_budget_amount(
                budget_line
            )
        )

        budget_by_key[
            key
        ] += budget_amount

        if (
            name_field
            and key not in names
        ):
            names[
                key
            ] = _clean_text(
                budget_line.get(
                    name_field
                )
            )

    #
    # Actual side
    #
    for transaction in transactions:

        key = _first_value(
            transaction,
            actual_fields,
        )

        if not key:
            continue

        actual_by_key[
            key
        ] += _get_actual_amount(
            transaction
        )

    all_keys = sorted(
        set(
            budget_by_key
        )
        | set(
            actual_by_key
        )
    )

    comparison_lines: list[
        dict[str, Any]
    ] = []

    total_needed_budget = 0.0
    total_actual = 0.0

    for key in all_keys:

        needed_budget = (
            budget_by_key.get(
                key,
                0.0,
            )
        )

        actual = (
            actual_by_key.get(
                key,
                0.0,
            )
        )

        remaining_requirement = (
            needed_budget
            - actual
        )

        utilization_percentage = (
            actual
            / needed_budget
            * 100
            if needed_budget
            else None
        )

        status = (
            _get_needed_budget_status(
                needed_budget=(
                    needed_budget
                ),
                actual=actual,
            )
        )

        #
        # Planning interpretation
        #
        # Only Budget Line analysis can compare against
        # the Available Budget line-code population.
        #
        planning_status = None

        if (
            dimension_name == "budget_line"
            and abs(
                needed_budget
            )
            < 0.01
            and abs(
                actual
            )
            >= 0.01
        ):

            if (
                key
                in available_budget_line_codes
            ):
                planning_status = (
                    "Funded / No Additional Need Identified"
                )

            else:
                planning_status = (
                    "Unbudgeted or Unmapped Actual"
                )

        elif (
            dimension_name == "budget_line"
            and abs(
                needed_budget
            )
            >= 0.01
        ):
            planning_status = (
                "Needed Budget Identified"
            )

        record: dict[
            str,
            Any,
        ] = {
            "code": key,
            "needed_budget": round(
                needed_budget,
                2,
            ),
            "actual": round(
                actual,
                2,
            ),
            "remaining_requirement": (
                round(
                    remaining_requirement,
                    2,
                )
            ),
            "utilization_percentage": (
                round(
                    utilization_percentage,
                    2,
                )
                if (
                    utilization_percentage
                    is not None
                )
                else None
            ),
            "status": status,
            "planning_status": (
                planning_status
            ),
        }

        if (
            dimension_name
            == "budget_line"
        ):

            record[
                "budget_line_code"
            ] = key

            record[
                "budget_line_name"
            ] = names.get(
                key
            )

        else:

            record[
                f"{dimension_name}_code"
            ] = key

            if name_field:

                record[
                    f"{dimension_name}_name"
                ] = names.get(
                    key
                )

        comparison_lines.append(
            record
        )

        total_needed_budget += (
            needed_budget
        )

        total_actual += (
            actual
        )

    return {
        "dimension": (
            dimension_name
        ),
        "summary": (
            _build_summary(
                total_needed_budget=(
                    total_needed_budget
                ),
                total_actual=(
                    total_actual
                ),
                comparison_lines=(
                    comparison_lines
                ),
            )
        ),
        "lines": (
            comparison_lines
        ),
    }


def _generate_fiscal_year_view(
    needed_budget_lines: list[
        dict[str, Any]
    ],
    transactions: list[
        dict[str, Any]
    ],
) -> dict[str, Any]:

    needed_by_year: dict[
        str,
        float,
    ] = defaultdict(
        float
    )

    actual_by_year: dict[
        str,
        float,
    ] = defaultdict(
        float
    )

    for budget_line in (
        needed_budget_lines
    ):

        fiscal_year = (
            budget_line.get(
                "fiscal_year"
            )
        )

        if fiscal_year is None:
            continue

        key = str(
            fiscal_year
        ).strip()

        if not key:
            continue

        needed_by_year[
            key
        ] += (
            _get_needed_budget_amount(
                budget_line
            )
        )

    for transaction in transactions:

        fiscal_year = (
            transaction.get(
                "fiscal_year"
            )
        )

        if fiscal_year is None:

            posting_date = (
                transaction.get(
                    "posting_date"
                )
                or transaction.get(
                    "transaction_date"
                )
            )

            fiscal_year = (
                _extract_year(
                    posting_date
                )
            )

        if fiscal_year is None:
            continue

        key = str(
            fiscal_year
        ).strip()

        if not key:
            continue

        actual_by_year[
            key
        ] += _get_actual_amount(
            transaction
        )

    all_years = sorted(
        set(
            needed_by_year
        )
        | set(
            actual_by_year
        )
    )

    lines: list[
        dict[str, Any]
    ] = []

    total_needed_budget = 0.0
    total_actual = 0.0

    for year in all_years:

        needed_budget = (
            needed_by_year.get(
                year,
                0.0,
            )
        )

        actual = (
            actual_by_year.get(
                year,
                0.0,
            )
        )

        remaining_requirement = (
            needed_budget
            - actual
        )

        utilization_percentage = (
            actual
            / needed_budget
            * 100
            if needed_budget
            else None
        )

        status = (
            _get_needed_budget_status(
                needed_budget=(
                    needed_budget
                ),
                actual=actual,
            )
        )

        lines.append(
            {
                "fiscal_year": (
                    int(year)
                    if year.isdigit()
                    else year
                ),
                "needed_budget": (
                    round(
                        needed_budget,
                        2,
                    )
                ),
                "actual": round(
                    actual,
                    2,
                ),
                "remaining_requirement": (
                    round(
                        remaining_requirement,
                        2,
                    )
                ),
                "utilization_percentage": (
                    round(
                        utilization_percentage,
                        2,
                    )
                    if (
                        utilization_percentage
                        is not None
                    )
                    else None
                ),
                "status": (
                    status
                ),
            }
        )

        total_needed_budget += (
            needed_budget
        )

        total_actual += actual

    return {
        "dimension": (
            "fiscal_year"
        ),
        "summary": {
            "total_needed_budget": (
                round(
                    total_needed_budget,
                    2,
                )
            ),
            "total_actual": (
                round(
                    total_actual,
                    2,
                )
            ),
            "remaining_requirement": (
                round(
                    total_needed_budget
                    - total_actual,
                    2,
                )
            ),
            "year_count": len(
                lines
            ),
        },
        "lines": (
            lines
        ),
    }


def _build_summary(
    total_needed_budget: float,
    total_actual: float,
    comparison_lines: list[
        dict[str, Any]
    ],
) -> dict[str, Any]:

    remaining_requirement = (
        total_needed_budget
        - total_actual
    )

    utilization_percentage = (
        total_actual
        / total_needed_budget
        * 100
        if total_needed_budget
        else None
    )

    return {
        "total_needed_budget": (
            round(
                total_needed_budget,
                2,
            )
        ),
        "total_actual": (
            round(
                total_actual,
                2,
            )
        ),
        "remaining_requirement": (
            round(
                remaining_requirement,
                2,
            )
        ),
        "utilization_percentage": (
            round(
                utilization_percentage,
                2,
            )
            if (
                utilization_percentage
                is not None
            )
            else None
        ),
        "line_count": len(
            comparison_lines
        ),
        "over_needed_budget_count": sum(
            line.get(
                "status"
            )
            == "Over Needed Budget"
            for line in (
                comparison_lines
            )
        ),
        "within_needed_budget_count": sum(
            line.get(
                "status"
            )
            == "Within Needed Budget"
            for line in (
                comparison_lines
            )
        ),
        "no_needed_budget_count": sum(
            line.get(
                "status"
            )
            == "No Needed Budget"
            for line in (
                comparison_lines
            )
        ),
    }


def _get_needed_budget_amount(
    budget_line: dict[str, Any],
) -> float:

    return _to_float(
        budget_line.get(
            "needed_budget"
        )
    )


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
            (debit or 0.0)
            - (credit or 0.0)
        )

    amount = _first_numeric(
        transaction,
        [
            "amount",
        ],
    )

    return amount or 0.0


def _get_needed_budget_status(
    needed_budget: float,
    actual: float,
) -> str:

    if (
        abs(
            needed_budget
        )
        < 0.01
        and abs(
            actual
        )
        >= 0.01
    ):
        return (
            "No Needed Budget"
        )

    if actual > needed_budget:
        return (
            "Over Needed Budget"
        )

    return (
        "Within Needed Budget"
    )


def _first_value(
    record: dict[str, Any],
    fields: list[str],
) -> str | None:

    for field_name in fields:

        value = record.get(
            field_name
        )

        cleaned = _clean_text(
            value
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

        if _is_blank(
            value
        ):
            continue

        return _to_float(
            value
        )

    return None


def _extract_year(
    value: Any,
) -> int | None:

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value.year

    text = str(
        value
    ).strip()

    if not text:
        return None

    try:
        return datetime.fromisoformat(
            text
        ).year

    except ValueError:
        pass

    for format_string in [
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]:

        try:
            return datetime.strptime(
                text,
                format_string,
            ).year

        except ValueError:
            continue

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
        return float(
            value
        )

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
        return float(
            text
        )

    except ValueError:
        return 0.0