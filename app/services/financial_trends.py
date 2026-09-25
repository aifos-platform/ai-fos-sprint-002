from datetime import date, datetime
from typing import Any

from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)


def generate_financial_trends(
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate validated financial trend intelligence from
    General Ledger transactions.

    The trend engine follows the same Income Statement
    accounting treatment used by AI-FOS:

    - only Income Statement posting accounts are included;
    - year-end closing entries are excluded;
    - revenue is calculated as credit minus debit;
    - expenses are calculated as debit minus credit;
    - legitimate accounting expenses remain included.

    The engine does not forecast or invent missing periods.
    It reports only periods supported by source transactions.
    """

    classifier = BudgetActualClassifier()

    monthly_totals: dict[str, dict[str, float]] = {}
    annual_totals: dict[str, dict[str, float]] = {}

    included_transaction_count = 0
    skipped_missing_date_count = 0
    skipped_invalid_date_count = 0
    excluded_closing_entry_count = 0

    earliest_posting_date: date | None = None
    latest_posting_date: date | None = None

    for transaction in transactions:

        raw_date = (
            transaction.get("transaction_date")
            or transaction.get("posting_date")
        )

        if raw_date is None or str(raw_date).strip() == "":
            skipped_missing_date_count += 1
            continue

        posting_date = _parse_date(raw_date)

        if posting_date is None:
            skipped_invalid_date_count += 1
            continue

        account_number = str(
            transaction.get("account")
            or transaction.get("account_number")
            or ""
        ).strip()

        if not account_number:
            continue

        metadata = accounts_by_number.get(account_number)

        if metadata is None:
            continue

        if metadata.get("income_balance") != "Income Statement":
            continue

        if metadata.get("is_posting_account") is False:
            continue

        classification = classifier.classify(
            transaction=transaction,
            accounts_by_number=accounts_by_number,
        )

        if classification.get("is_closing_entry"):
            excluded_closing_entry_count += 1
            continue

        debit = _to_float(
            transaction.get("debit")
            if transaction.get("debit") is not None
            else transaction.get("debit_amount")
        )

        credit = _to_float(
            transaction.get("credit")
            if transaction.get("credit") is not None
            else transaction.get("credit_amount")
        )

        category = metadata.get("financial_category")

        revenue_amount = 0.0
        expense_amount = 0.0

        if category == "Revenue":
            revenue_amount = credit - debit

        elif category == "Expense":
            expense_amount = debit - credit

        else:
            continue

        included_transaction_count += 1

        if (
            earliest_posting_date is None
            or posting_date < earliest_posting_date
        ):
            earliest_posting_date = posting_date

        if (
            latest_posting_date is None
            or posting_date > latest_posting_date
        ):
            latest_posting_date = posting_date

        month_key = posting_date.strftime("%Y-%m")
        year_key = str(posting_date.year)

        month_values = monthly_totals.setdefault(
            month_key,
            {
                "revenue": 0.0,
                "expenses": 0.0,
            },
        )

        month_values["revenue"] += revenue_amount
        month_values["expenses"] += expense_amount

        year_values = annual_totals.setdefault(
            year_key,
            {
                "revenue": 0.0,
                "expenses": 0.0,
            },
        )

        year_values["revenue"] += revenue_amount
        year_values["expenses"] += expense_amount

    monthly_series = [
        _build_period_record(
            period=period,
            values=monthly_totals[period],
        )
        for period in sorted(monthly_totals)
    ]

    annual_series = [
        _build_period_record(
            period=period,
            values=annual_totals[period],
        )
        for period in sorted(annual_totals)
    ]

    latest_month_comparison = _build_latest_comparison(
        records=monthly_series,
        period_type="month",
    )

    latest_year_comparison = _build_latest_comparison(
        records=annual_series,
        period_type="year",
    )

    return {
        "status": (
            "available"
            if monthly_series
            else "not_available"
        ),
        "basis": (
            "Income Statement posting accounts with "
            "year-end closing entries excluded."
        ),
        "coverage": {
            "earliest_posting_date": (
                earliest_posting_date.isoformat()
                if earliest_posting_date
                else None
            ),
            "latest_posting_date": (
                latest_posting_date.isoformat()
                if latest_posting_date
                else None
            ),
            "month_count": len(monthly_series),
            "year_count": len(annual_series),
        },
        "quality": {
            "included_transaction_count": (
                included_transaction_count
            ),
            "skipped_missing_date_count": (
                skipped_missing_date_count
            ),
            "skipped_invalid_date_count": (
                skipped_invalid_date_count
            ),
            "excluded_closing_entry_count": (
                excluded_closing_entry_count
            ),
        },
        "monthly_series": monthly_series,
        "annual_series": annual_series,
        "latest_month_comparison": (
            latest_month_comparison
        ),
        "latest_year_comparison": (
            latest_year_comparison
        ),
    }


def _build_period_record(
    period: str,
    values: dict[str, float],
) -> dict[str, Any]:
    revenue = round(
        _to_float(values.get("revenue")),
        2,
    )

    expenses = round(
        _to_float(values.get("expenses")),
        2,
    )

    net_result = round(
        revenue - expenses,
        2,
    )

    return {
        "period": period,
        "revenue": revenue,
        "expenses": expenses,
        "net_result": net_result,
    }


def _build_latest_comparison(
    records: list[dict[str, Any]],
    period_type: str,
) -> dict[str, Any] | None:
    """
    Compare the latest observed period with the immediately
    preceding observed period.

    No missing month or year is synthesized.

    The latest month may be incomplete if the source data
    does not cover the full calendar month, so the comparison
    basis is explicitly disclosed.
    """

    if len(records) < 2:
        return None

    current = records[-1]
    previous = records[-2]

    return {
        "period_type": period_type,
        "comparison_basis": (
            "latest_observed_period_vs_previous_observed_period"
        ),
        "current_period": current.get("period"),
        "previous_period": previous.get("period"),
        "revenue": _compare_values(
            current_value=_to_float(
                current.get("revenue")
            ),
            previous_value=_to_float(
                previous.get("revenue")
            ),
        ),
        "expenses": _compare_values(
            current_value=_to_float(
                current.get("expenses")
            ),
            previous_value=_to_float(
                previous.get("expenses")
            ),
        ),
        "net_result": _compare_values(
            current_value=_to_float(
                current.get("net_result")
            ),
            previous_value=_to_float(
                previous.get("net_result")
            ),
        ),
        "caution": (
            "Observed periods are compared as present in "
            "the source data. The latest period may be "
            "incomplete and should not automatically be "
            "interpreted as a like-for-like full-period "
            "comparison."
        ),
    }


def _compare_values(
    current_value: float,
    previous_value: float,
) -> dict[str, Any]:
    change_amount = round(
        current_value - previous_value,
        2,
    )

    if change_amount > 0:
        direction = "increased"

    elif change_amount < 0:
        direction = "decreased"

    else:
        direction = "unchanged"

    if abs(previous_value) < 0.0000001:
        change_percentage = None
    else:
        change_percentage = round(
            (
                change_amount
                / abs(previous_value)
            )
            * 100,
            2,
        )

    return {
        "current_value": round(
            current_value,
            2,
        ),
        "previous_value": round(
            previous_value,
            2,
        ),
        "change_amount": change_amount,
        "change_percentage": (
            change_percentage
        ),
        "direction": direction,
    }


def _parse_date(
    value: Any,
) -> date | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text = str(value).strip()

    if not text:
        return None

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]

    for format_string in formats:
        try:
            return datetime.strptime(
                text,
                format_string,
            ).date()

        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            text
        ).date()

    except ValueError:
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