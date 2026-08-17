from datetime import datetime
from typing import Any

from app.services.budget_actual_classifier import BudgetActualClassifier


def generate_income_statement(
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate an Income Statement from transaction-level
    General Ledger data.

    Year-end closing entries are excluded so they do not
    distort reported revenue, expenses, or net result.

    Legitimate accounting expenses such as depreciation
    and amortization remain included.
    """

    revenue = 0.0
    expenses = 0.0

    classifier = BudgetActualClassifier()

    latest_closing_date = None

    for transaction in transactions:
        classification = classifier.classify(
            transaction=transaction,
            accounts_by_number=accounts_by_number,
        )

        if not classification.get("is_closing_entry"):
            continue

        transaction_date = _parse_date(
            transaction.get("transaction_date")
            or transaction.get("posting_date")
        )

        if transaction_date is None:
            continue

        if (
            latest_closing_date is None
            or transaction_date > latest_closing_date
        ):
            latest_closing_date = transaction_date

    for transaction in transactions:
        account_number = str(
            transaction.get("account")
            or transaction.get("account_number")
            or ""
        ).strip()

        if not account_number:
            continue

        metadata = accounts_by_number.get(
            account_number
        )

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

        category = metadata.get(
            "financial_category"
        )

        if category == "Revenue":
            revenue += credit - debit

        elif category == "Expense":
            expenses += debit - credit

    current_period_revenue = 0.0
    current_period_expenses = 0.0

    for transaction in transactions:
        transaction_date = _parse_date(
            transaction.get("transaction_date")
            or transaction.get("posting_date")
        )

        if transaction_date is None:
            continue

        if (
            latest_closing_date is not None
            and transaction_date <= latest_closing_date
        ):
            continue

        account_number = str(
            transaction.get("account")
            or transaction.get("account_number")
            or ""
        ).strip()

        if not account_number:
            continue

        metadata = accounts_by_number.get(
            account_number
        )

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

        category = metadata.get(
            "financial_category"
        )

        if category == "Revenue":
            current_period_revenue += credit - debit

        elif category == "Expense":
            current_period_expenses += debit - credit

    return {
        "revenue": round(
            revenue,
            2,
        ),
        "expenses": round(
            expenses,
            2,
        ),
        "net_profit": round(
            revenue - expenses,
            2,
        ),
        "latest_closing_date": (
            latest_closing_date.date().isoformat()
            if latest_closing_date
            else None
        ),
        "current_period_revenue": round(
            current_period_revenue,
            2,
        ),
        "current_period_expenses": round(
            current_period_expenses,
            2,
        ),
        "current_period_result": round(
            current_period_revenue
            - current_period_expenses,
            2,
        ),
    }

def _parse_date(
    value: Any,
) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    text = str(value).strip()

    if not text:
        return None

    try:
        return datetime.fromisoformat(text)

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