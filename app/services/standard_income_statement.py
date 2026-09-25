from typing import Any


def generate_standard_income_statement(
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
    validated_income_statement: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the detailed Standard Income Statement used by
    AI-FOS reporting.

    This service is a reporting layer only.

    It does not replace or recalculate the authoritative
    AI-FOS Income Statement. Instead, it organizes posting
    account activity into a detailed hierarchy and then
    reconciles the resulting report totals against the
    already validated Income Statement.

    Year-end closing entries are excluded from report
    activity by restricting the report to the current
    reporting period identified by the validated Income
    Statement's latest closing date.
    """

    validated_income_statement = (
        validated_income_statement or {}
    )

    latest_closing_date = (
        validated_income_statement.get(
            "latest_closing_date"
        )
    )

    account_balances: dict[str, float] = {}

    for transaction in transactions:
        account_number = str(
            transaction.get("account")
            or transaction.get("account_number")
            or ""
        ).strip()

        if not account_number:
            continue

        account = accounts_by_number.get(
            account_number
        )

        if not account:
            continue

        if (
            account.get("income_balance")
            != "Income Statement"
        ):
            continue

        if account.get("is_posting_account") is not True:
            continue

        category = account.get(
            "financial_category"
        )

        if category not in {
            "Revenue",
            "Expense",
        }:
            continue

        if not _is_current_period_transaction(
            transaction=transaction,
            latest_closing_date=latest_closing_date,
        ):
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

        if category == "Revenue":
            amount = credit - debit
        else:
            amount = debit - credit

        account_balances[account_number] = (
            account_balances.get(
                account_number,
                0.0,
            )
            + amount
        )

    revenue_lines = _build_report_lines(
        category="Revenue",
        account_balances=account_balances,
        accounts_by_number=accounts_by_number,
    )

    expense_lines = _build_report_lines(
        category="Expense",
        account_balances=account_balances,
        accounts_by_number=accounts_by_number,
    )

    detailed_revenue = round(
        sum(
            line["amount"]
            for line in revenue_lines
        ),
        2,
    )

    detailed_expenses = round(
        sum(
            line["amount"]
            for line in expense_lines
        ),
        2,
    )

    detailed_net_result = round(
        detailed_revenue - detailed_expenses,
        2,
    )

    validated_revenue = _validated_current_value(
        validated_income_statement,
        current_key="current_period_revenue",
        fallback_key="revenue",
    )

    validated_expenses = _validated_current_value(
        validated_income_statement,
        current_key="current_period_expenses",
        fallback_key="expenses",
    )

    validated_net_result = _validated_current_value(
        validated_income_statement,
        current_key="current_period_result",
        fallback_key="net_profit",
    )

    revenue_difference = round(
        detailed_revenue - validated_revenue,
        2,
    )

    expense_difference = round(
        detailed_expenses - validated_expenses,
        2,
    )

    net_result_difference = round(
        detailed_net_result - validated_net_result,
        2,
    )

    reconciled = (
        revenue_difference == 0.0
        and expense_difference == 0.0
        and net_result_difference == 0.0
    )

    return {
        "status": (
            "available"
            if reconciled
            else "reconciliation_failed"
        ),
        "report_type": "income_statement",
        "title": "Income Statement",
        "reporting_basis": "current_period",
        "latest_closing_date": latest_closing_date,
        "sections": [
            {
                "section": "Revenue",
                "lines": revenue_lines,
                "total": detailed_revenue,
            },
            {
                "section": "Expenses",
                "lines": expense_lines,
                "total": detailed_expenses,
            },
        ],
        "totals": {
            "revenue": detailed_revenue,
            "expenses": detailed_expenses,
            "net_result": detailed_net_result,
        },
        "validated_totals": {
            "revenue": validated_revenue,
            "expenses": validated_expenses,
            "net_result": validated_net_result,
        },
        "reconciliation": {
            "reconciled": reconciled,
            "revenue_difference": revenue_difference,
            "expense_difference": expense_difference,
            "net_result_difference": net_result_difference,
        },
        "controls": {
            "reporting_layer_only": True,
            "validated_income_statement_preserved": True,
            "financial_recalculation_performed": False,
            "posting_accounts_only": True,
            "income_statement_accounts_only": True,
            "missing_accounts_not_invented": True,
            "hierarchy_metadata_preserved": True,
            "reconciliation_required": True,
        },
    }


def _build_report_lines(
    *,
    category: str,
    account_balances: dict[str, float],
    accounts_by_number: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build detailed posting-account lines while preserving
    the Chart of Accounts hierarchy metadata.
    """

    lines: list[dict[str, Any]] = []

    for account_number, account in accounts_by_number.items():
        if (
            account.get("financial_category")
            != category
        ):
            continue

        if (
            account.get("income_balance")
            != "Income Statement"
        ):
            continue

        if account.get("is_posting_account") is not True:
            continue

        amount = round(
            account_balances.get(
                str(account_number).strip(),
                0.0,
            ),
            2,
        )

        lines.append(
            {
                "account_number": str(
                    account_number
                ).strip(),
                "account_name": str(
                    account.get("account_name")
                    or ""
                ).strip(),
                "parent_account": account.get(
                    "parent_account"
                ),
                "level": account.get("level"),
                "financial_category": account.get(
                    "financial_category"
                ),
                "financial_subcategory": account.get(
                    "financial_subcategory"
                ),
                "normal_balance": account.get(
                    "normal_balance"
                ),
                "amount": amount,
            }
        )

    lines.sort(
        key=_report_line_sort_key
    )

    return lines


def _report_line_sort_key(
    line: dict[str, Any],
) -> tuple[Any, ...]:
    """
    Produce deterministic report ordering.

    Account number remains the primary ordering mechanism
    because ERP Chart of Accounts numbering normally
    carries the intended reporting order.
    """

    account_number = str(
        line.get("account_number")
        or ""
    ).strip()

    return (
        _natural_account_key(
            account_number
        ),
        str(
            line.get("account_name")
            or ""
        ).lower(),
    )


def _natural_account_key(
    account_number: str,
) -> tuple[Any, ...]:
    """
    Sort numeric account numbers numerically where possible,
    while still supporting alphanumeric ERP account codes.
    """

    text = str(
        account_number or ""
    ).strip()

    if text.isdigit():
        return (
            0,
            int(text),
        )

    return (
        1,
        text.lower(),
    )


def _validated_current_value(
    income_statement: dict[str, Any],
    *,
    current_key: str,
    fallback_key: str,
) -> float:
    """
    Prefer the validated current-period amount.

    Fall back to the existing validated aggregate only when
    the current-period field is not present.
    """

    if (
        current_key in income_statement
        and income_statement.get(
            current_key
        )
        is not None
    ):
        return round(
            _to_float(
                income_statement.get(
                    current_key
                )
            ),
            2,
        )

    return round(
        _to_float(
            income_statement.get(
                fallback_key
            )
        ),
        2,
    )


def _is_current_period_transaction(
    *,
    transaction: dict[str, Any],
    latest_closing_date: Any,
) -> bool:
    """
    Keep transactions after the latest validated closing
    date.

    When no closing date exists, all otherwise eligible
    transactions belong to the available reporting period.
    """

    if not latest_closing_date:
        return True

    transaction_date = (
        transaction.get("transaction_date")
        or transaction.get("posting_date")
    )

    if transaction_date is None:
        return False

    transaction_date_text = str(
        transaction_date
    ).strip()

    closing_date_text = str(
        latest_closing_date
    ).strip()

    if not transaction_date_text:
        return False

    return (
        transaction_date_text[:10]
        > closing_date_text[:10]
    )


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