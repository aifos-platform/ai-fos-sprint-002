from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any
from app.services.budget_actual_classifier import BudgetActualClassifier
from app.services.budget_period_resolver import BudgetPeriodResolver

DIMENSION_VIEWS = {
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
}


def generate_budget_vs_actual(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build AI-FOS Budget vs Actual analysis.
    """
    accounts_by_number = accounts_by_number or {}

    classifier = BudgetActualClassifier()

    budget_transactions: list[dict[str, Any]] = []

    for transaction in transactions:
        classification = classifier.classify(
            transaction=transaction,
            accounts_by_number=accounts_by_number,
        )

        if not classification["is_budget_consuming"]:
            continue

        budget_transaction = dict(transaction)

        budget_transaction["budget_actual_amount"] = classification[
            "budget_actual_amount"
        ]

        budget_transaction["budget_treatment"] = classification["budget_treatment"]

        budget_transaction["is_closing_entry"] = classification["is_closing_entry"]

        budget_transactions.append(budget_transaction)

    views: dict[str, Any] = {}

    for dimension_name, config in DIMENSION_VIEWS.items():

        views[dimension_name] = _generate_dimension_view(
            budget_lines=budget_lines,
            transactions=budget_transactions,
            dimension_name=dimension_name,
            budget_fields=config["budget_fields"],
            actual_fields=config["actual_fields"],
            name_field=config["name_field"],
        )

    primary_view = views["budget_line"]

    fiscal_year_view = _generate_fiscal_year_view(
        budget_lines=budget_lines,
        transactions=budget_transactions,
    )

    return {
        # Backward-compatible outputs
        "summary": primary_view["summary"],
        "lines": primary_view["lines"],
        "portfolio_control": primary_view["summary"],
        
        # Canonical AI-FOS analysis views
        "by_budget_line": primary_view,
        "by_fund": views["fund"],
        "by_donor": views["donor"],
        "by_program": views["program"],
        "by_category": views["category"],
        "by_donor_line": views["donor_line"],
        "by_project": views["project"],
        "by_fiscal_year": fiscal_year_view,
    }


def _generate_dimension_view(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    dimension_name: str,
    budget_fields: list[str],
    actual_fields: list[str],
    name_field: str | None,
) -> dict[str, Any]:

    budget_by_key: dict[str, float] = defaultdict(float)
    actual_by_key: dict[str, float] = defaultdict(float)

    names: dict[str, str | None] = {}

    for budget_line in budget_lines:

        key = _first_value(
            budget_line,
            budget_fields,
        )

        if not key:
            continue

        budget_amount = _get_budget_amount(budget_line)

        budget_by_key[key] += budget_amount

        if name_field and key not in names:
            names[key] = _clean_text(budget_line.get(name_field))

    for transaction in transactions:

        key = _first_value(
            transaction,
            actual_fields,
        )

        if not key:
            continue

        actual_amount = _get_actual_amount(transaction)

        actual_by_key[key] += actual_amount

    all_keys = sorted(set(budget_by_key) | set(actual_by_key))

    comparison_lines: list[dict[str, Any]] = []

    total_budget = 0.0
    total_actual = 0.0

    for key in all_keys:

        budget = budget_by_key.get(
            key,
            0.0,
        )

        actual = actual_by_key.get(
            key,
            0.0,
        )

        variance = budget - actual

        utilization_percentage = actual / budget * 100 if budget else None

        status = _get_status(
            budget=budget,
            actual=actual,
        )

        record: dict[str, Any] = {
            "code": key,
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
                    utilization_percentage,
                    2,
                )
                if utilization_percentage is not None
                else None
            ),
            "status": status,
        }

        if dimension_name == "budget_line":

            record["budget_line_code"] = key
            record["budget_line_name"] = names.get(key)

        else:

            record[f"{dimension_name}_code"] = key

            if name_field:
                record[f"{dimension_name}_name"] = names.get(key)

        comparison_lines.append(record)

        total_budget += budget
        total_actual += actual

    return {
        "dimension": dimension_name,
        "summary": _build_summary(
            total_budget=total_budget,
            total_actual=total_actual,
            comparison_lines=comparison_lines,
        ),
        "lines": comparison_lines,
    }


def _generate_fiscal_year_view(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build a fiscal-year view while preserving the
    semantic meaning of dynamic Budget period amounts.

    Requested amounts, spending plans, budgets, and
    forecasts remain separate and are not blindly
    combined into one Budget figure.
    """

    resolver = BudgetPeriodResolver()

    budget_by_year: dict[str, float] = defaultdict(float)
    requested_by_year: dict[str, float] = defaultdict(float)
    spending_plan_by_year: dict[str, float] = defaultdict(float)
    forecast_by_year: dict[str, float] = defaultdict(float)

    budget_present: set[str] = set()
    requested_present: set[str] = set()
    spending_plan_present: set[str] = set()
    forecast_present: set[str] = set()

    actual_by_year: dict[str, float] = defaultdict(float)

    #
    # Budget-side period amounts
    #
    for budget_line in budget_lines:

        resolved = resolver.resolve_line(
            budget_line
        )

        by_year = resolved.get(
            "by_year",
            {},
        )

        if by_year:

            for fiscal_year, year_data in by_year.items():

                key = str(
                    fiscal_year
                ).strip()

                if not key:
                    continue

                budget_amount = year_data.get(
                    "budget"
                )

                requested_amount = year_data.get(
                    "requested"
                )

                spending_plan_amount = year_data.get(
                    "spending_plan"
                )

                forecast_amount = year_data.get(
                    "forecast"
                )

                if budget_amount is not None:
                    budget_present.add(key)
                    budget_by_year[key] += _to_float(
                        budget_amount
                    )

                if requested_amount is not None:
                    requested_present.add(key)
                    requested_by_year[key] += _to_float(
                        requested_amount
                    )

                if spending_plan_amount is not None:
                    spending_plan_present.add(key)
                    spending_plan_by_year[key] += _to_float(
                        spending_plan_amount
                    )

                if forecast_amount is not None:
                    forecast_present.add(key)
                    forecast_by_year[key] += _to_float(
                        forecast_amount
                    )

            continue

        #
        # Backward compatibility for older Budget files
        # containing one explicit fiscal_year.
        #
        fiscal_year = budget_line.get(
            "fiscal_year"
        )

        if fiscal_year is None:
            continue

        key = str(
            fiscal_year
        ).strip()

        if not key:
            continue

        budget_present.add(key)

        budget_by_year[key] += _get_budget_amount(
            budget_line
        )

    #
    # Actual-side fiscal years
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

        if fiscal_year is None:
            continue

        key = str(
            fiscal_year
        ).strip()

        if not key:
            continue

        actual_by_year[key] += _get_actual_amount(
            transaction
        )

    all_years = sorted(
        set(budget_by_year)
        | set(requested_by_year)
        | set(spending_plan_by_year)
        | set(forecast_by_year)
        | set(actual_by_year)
    )

    lines: list[dict[str, Any]] = []

    total_budget = 0.0
    total_actual = 0.0

    for year in all_years:

        budget = (
            budget_by_year.get(
                year,
                0.0,
            )
            if year in budget_present
            else None
        )

        requested = (
            requested_by_year.get(
                year,
                0.0,
            )
            if year in requested_present
            else None
        )

        spending_plan = (
            spending_plan_by_year.get(
                year,
                0.0,
            )
            if year in spending_plan_present
            else None
        )

        forecast = (
            forecast_by_year.get(
                year,
                0.0,
            )
            if year in forecast_present
            else None
        )

        actual = actual_by_year.get(
            year,
            0.0,
        )

        #
        # Only a genuine Budget amount is used for
        # Budget-vs-Actual variance at this stage.
        #
        variance = (
            budget - actual
            if budget is not None
            else None
        )

        utilization = (
            actual / budget * 100
            if (
                budget is not None
                and budget != 0
            )
            else None
        )

        status = (
            _get_status(
                budget=budget,
                actual=actual,
            )
            if budget is not None
            else "Budget Not Identified"
        )

        lines.append(
            {
                "fiscal_year": (
                    int(year)
                    if year.isdigit()
                    else year
                ),
                "budget": (
                    round(
                        budget,
                        2,
                    )
                    if budget is not None
                    else None
                ),
                "requested": (
                    round(
                        requested,
                        2,
                    )
                    if requested is not None
                    else None
                ),
                "spending_plan": (
                    round(
                        spending_plan,
                        2,
                    )
                    if spending_plan is not None
                    else None
                ),
                "forecast": (
                    round(
                        forecast,
                        2,
                    )
                    if forecast is not None
                    else None
                ),
                "actual": round(
                    actual,
                    2,
                ),
                "variance": (
                    round(
                        variance,
                        2,
                    )
                    if variance is not None
                    else None
                ),
                "utilization_percentage": (
                    round(
                        utilization,
                        2,
                    )
                    if utilization is not None
                    else None
                ),
                "status": status,
            }
        )

        if budget is not None:
            total_budget += budget

        total_actual += actual

    return {
        "dimension": "fiscal_year",
        "summary": {
            "total_budget": round(
                total_budget,
                2,
            ),
            "total_actual": round(
                total_actual,
                2,
            ),
            "year_count": len(
                lines
            ),
            "budget_year_count": len(
                budget_present
            ),
            "requested_year_count": len(
                requested_present
            ),
            "spending_plan_year_count": len(
                spending_plan_present
            ),
            "forecast_year_count": len(
                forecast_present
            ),
        },
        "lines": lines,
    }


def _build_summary(
    total_budget: float,
    total_actual: float,
    comparison_lines: list[dict[str, Any]],
) -> dict[str, Any]:

    budgeted_actual = 0.0
    unbudgeted_actual = 0.0

    for line in comparison_lines:
        budget = float(
            line.get("budget") or 0.0
        )

        actual = float(
            line.get("actual") or 0.0
        )

        if budget > 0:
            budgeted_actual += actual

        elif actual != 0:
            unbudgeted_actual += actual

    variance = total_budget - budgeted_actual

    utilization = (
        budgeted_actual / total_budget * 100
        if total_budget
        else None
    )

    overall_variance_including_unbudgeted = (
        total_budget - total_actual
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
        "budgeted_actual": round(
            budgeted_actual,
            2,
        ),
        "unbudgeted_actual": round(
            unbudgeted_actual,
            2,
        ),
        "total_variance": round(
            variance,
            2,
        ),
        "overall_variance_including_unbudgeted": round(
            overall_variance_including_unbudgeted,
            2,
        ),
        "utilization_percentage": (
            round(
                utilization,
                2,
            )
            if utilization is not None
            else None
        ),
        "line_count": len(comparison_lines),
        "budget_line_count": len(comparison_lines),
        "over_budget_count": sum(
            line.get("status") == "Over Budget"
            for line in comparison_lines
        ),
        "within_budget_count": sum(
            line.get("status") == "Within Budget"
            for line in comparison_lines
        ),
        "no_budget_count": sum(
            line.get("status") == "No Budget"
            for line in comparison_lines
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

        value = budget_line.get(field_name)

        if not _is_blank(value):
            return _to_float(value)

    return 0.0


def _get_actual_amount(
    transaction: dict[str, Any],
) -> float:
    """
    Return the Budget Actual amount determined by
    the central Budget Actual classifier.

    Falls back to accounting movement for backward
    compatibility.
    """

    classified_amount = transaction.get("budget_actual_amount")

    if classified_amount is not None:
        return _to_float(classified_amount)

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

    if debit is not None or credit is not None:
        return (debit or 0.0) - (credit or 0.0)

    amount = _first_numeric(
        transaction,
        [
            "amount",
        ],
    )

    return amount or 0.0


def _get_status(
    budget: float,
    actual: float,
) -> str:

    if abs(budget) < 0.01 and abs(actual) >= 0.01:
        return "No Budget"

    if actual > budget:
        return "Over Budget"

    return "Within Budget"


def _first_value(
    record: dict[str, Any],
    fields: list[str],
) -> str | None:

    for field_name in fields:

        value = record.get(field_name)

        cleaned = _clean_text(value)

        if cleaned:
            return cleaned

    return None


def _first_numeric(
    record: dict[str, Any],
    fields: list[str],
) -> float | None:

    for field_name in fields:

        value = record.get(field_name)

        if _is_blank(value):
            continue

        return _to_float(value)

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

    text = str(value).strip()

    if not text:
        return None

    try:
        return datetime.fromisoformat(text).year

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

    cleaned = str(value).strip()

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

    text = str(value).replace(",", "").replace("$", "").strip()

    if not text:
        return 0.0

    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]

    try:
        return float(text)

    except ValueError:
        return 0.0
