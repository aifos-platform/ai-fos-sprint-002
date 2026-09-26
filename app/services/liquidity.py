from datetime import datetime, timedelta
from typing import Any

from app.services.budget_actual_classifier import BudgetActualClassifier


CASH_SUBCATEGORIES = {
    "cash",
    "cash and bank",
    "cash & bank",
    "cash and cash equivalents",
}

RUNWAY_LOOKBACK_DAYS = 365


def calculate_liquidity(
    transactions: list[dict[str, Any]],
    trial_balance: dict[str, dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate the organization's first-version
    liquidity and cash-runway metrics.

    Cash balances are classified using the
    liquidity_status stored in DIM_ACCOUNT.

    GL trial-balance values are the primary source
    for cash balances.

    If a posting cash account is completely absent
    from the GL trial balance, an explicit balance
    imported from the Chart of Accounts may be used
    as a fallback.

    Cash Runway:
        Available Cash / Average Monthly Expenses
    """

    total_cash = 0.0
    available_cash = 0.0
    blocked_cash = 0.0

    available_account_count = 0
    blocked_account_count = 0
    unclassified_cash_account_count = 0

    #
    # 1. Calculate cash balances by liquidity status.
    #
    # GL trial-balance values are the primary source.
    #
    # Never combine the GL balance and COA balance
    # for the same account.
    #

    processed_cash_accounts: set[str] = set()

    for account_number, balance_record in trial_balance.items():
        normalized_number = str(account_number).strip()

        metadata = accounts_by_number.get(
            normalized_number
        )

        if metadata is None:
            continue

        if metadata.get("is_posting_account") is False:
            continue

        if not _is_cash_account(metadata):
            continue

        debit = _to_float(
            balance_record.get("total_debit")
        )

        credit = _to_float(
            balance_record.get("total_credit")
        )

        balance = debit - credit

        processed_cash_accounts.add(
            normalized_number
        )

        total_cash += balance

        liquidity_status = str(
            metadata.get("liquidity_status")
            or ""
        ).strip()

        if liquidity_status == "Available":
            available_cash += balance
            available_account_count += 1

        elif liquidity_status == "Blocked":
            blocked_cash += balance
            blocked_account_count += 1

        else:
            unclassified_cash_account_count += 1

    #
    # COA balance fallback.
    #
    # Only posting cash accounts completely absent
    # from the GL trial balance are eligible.
    #

    for account_number, metadata in accounts_by_number.items():
        normalized_number = str(
            account_number
        ).strip()

        if normalized_number in processed_cash_accounts:
            continue

        if metadata.get("is_posting_account") is False:
            continue

        if not _is_cash_account(metadata):
            continue

        coa_balance = metadata.get("balance")

        if coa_balance is None:
            continue

        balance = _to_float(
            coa_balance
        )

        total_cash += balance

        liquidity_status = str(
            metadata.get("liquidity_status")
            or ""
        ).strip()

        if liquidity_status == "Available":
            available_cash += balance
            available_account_count += 1

        elif liquidity_status == "Blocked":
            blocked_cash += balance
            blocked_account_count += 1

        else:
            unclassified_cash_account_count += 1

    #
    # 2. Determine the reporting period.
    #

    transaction_dates: list[datetime] = []

    for transaction in transactions:
        transaction_date = _parse_date(
            transaction.get("transaction_date")
        )

        if transaction_date is not None:
            transaction_dates.append(
                transaction_date
            )

    period_start = None
    period_end = None
    reporting_month_count = 0

    if transaction_dates:
        period_end = max(
            transaction_dates
        )

        lookback_start = (
            period_end
            - timedelta(
                days=RUNWAY_LOOKBACK_DAYS
            )
        )

        earliest_transaction_date = min(
            transaction_dates
        )

        period_start = max(
            earliest_transaction_date,
            lookback_start,
        )

        if (
            earliest_transaction_date
            <= lookback_start
        ):
            reporting_month_count = 12
        else:
            reporting_month_count = (
                _month_count(
                    period_start,
                    period_end,
                )
            )

    #
    # 3. Calculate operating expenses for
    #    the reporting period.
    #
    # Use transaction-level classification so
    # year-end closing entries, depreciation,
    # revenue, and other non-operating movements
    # do not distort Cash Runway.
    #

    total_expenses = 0.0

    budget_actual_classifier = (
        BudgetActualClassifier()
    )

    for transaction in transactions:
        transaction_date = _parse_date(
            transaction.get(
                "transaction_date"
            )
        )

        if transaction_date is None:
            continue

        if (
            period_start
            and transaction_date < period_start
        ):
            continue

        if (
            period_end
            and transaction_date > period_end
        ):
            continue

        classification = (
            budget_actual_classifier.classify(
                transaction=transaction,
                accounts_by_number=(
                    accounts_by_number
                ),
            )
        )

        if (
            classification.get(
                "budget_treatment"
            )
            != "operating_expense"
        ):
            continue

        total_expenses += _to_float(
            classification.get(
                "budget_actual_amount"
            )
        )

    average_monthly_expenses = 0.0

    if reporting_month_count > 0:
        average_monthly_expenses = (
            total_expenses
            / reporting_month_count
        )

    #
    # 4. Calculate cash runway.
    #

    cash_runway_months = None

    if average_monthly_expenses > 0:
        cash_runway_months = (
            available_cash
            / average_monthly_expenses
        )

    #
    # 5. Return transparent liquidity metrics.
    #

    return {
        "total_cash": round(
            total_cash,
            2,
        ),
        "available_cash": round(
            available_cash,
            2,
        ),
        "blocked_cash": round(
            blocked_cash,
            2,
        ),
        "available_account_count": (
            available_account_count
        ),
        "blocked_account_count": (
            blocked_account_count
        ),
        "unclassified_cash_account_count": (
            unclassified_cash_account_count
        ),
        "total_expenses": round(
            total_expenses,
            2,
        ),
        "reporting_period_start": (
            period_start.date().isoformat()
            if period_start
            else None
        ),
        "reporting_period_end": (
            period_end.date().isoformat()
            if period_end
            else None
        ),
        "reporting_month_count": (
            reporting_month_count
        ),
        "average_monthly_expenses": round(
            average_monthly_expenses,
            2,
        ),
        "cash_runway_months": (
            round(
                cash_runway_months,
                2,
            )
            if cash_runway_months is not None
            else None
        ),
        "runway_basis": (
            "Available cash divided by average "
            "monthly expenses for the reporting period."
        ),
    }


def _is_cash_account(
    metadata: dict[str, Any],
) -> bool:
    category = str(
        metadata.get(
            "financial_category"
        )
        or ""
    ).strip()

    subcategory = str(
        metadata.get(
            "financial_subcategory"
        )
        or ""
    ).strip().lower()

    if category != "Asset":
        return False

    return (
        subcategory
        in CASH_SUBCATEGORIES
    )


def _month_count(
    start_date: datetime,
    end_date: datetime,
) -> int:
    """
    Count calendar months represented by the period,
    including both the starting and ending month.
    """

    return (
        (end_date.year - start_date.year) * 12
        + end_date.month
        - start_date.month
        + 1
    )


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
        return datetime.fromisoformat(
            text
        )

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
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0