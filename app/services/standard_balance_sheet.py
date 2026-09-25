from typing import Any


def generate_standard_balance_sheet(
    trial_balance: dict[str, dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
    validated_balance_sheet: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the detailed Standard Balance Sheet used by
    AI-FOS reporting.

    This service is a reporting layer only.

    It does not replace the authoritative AI-FOS Balance Sheet.
    Instead, it organizes the validated Trial Balance into
    detailed Asset, Liability, and Equity account lines and
    reconciles the resulting report totals against the already
    validated Balance Sheet.

    Current-period profit or loss remains a separate equity
    adjustment because the authoritative Balance Sheet already
    applies it before year-end closing entries are posted.
    """

    trial_balance = trial_balance or {}
    accounts_by_number = accounts_by_number or {}
    validated_balance_sheet = validated_balance_sheet or {}

    asset_lines = _build_report_lines(
        category="Asset",
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    liability_lines = _build_report_lines(
        category="Liability",
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    equity_lines = _build_report_lines(
        category="Equity",
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    detailed_assets = round(
        sum(
            line["amount"]
            for line in asset_lines
        ),
        2,
    )

    detailed_liabilities = round(
        sum(
            line["amount"]
            for line in liability_lines
        ),
        2,
    )

    detailed_reported_equity = round(
        sum(
            line["amount"]
            for line in equity_lines
        ),
        2,
    )

    validated_assets = _validated_value(
        validated_balance_sheet,
        "assets",
    )

    validated_liabilities = _validated_value(
        validated_balance_sheet,
        "liabilities",
    )

    validated_reported_equity = _validated_value(
        validated_balance_sheet,
        "reported_equity",
    )

    current_period_result = _validated_value(
        validated_balance_sheet,
        "current_period_result",
    )

    validated_adjusted_equity = _validated_value(
        validated_balance_sheet,
        "equity",
    )

    validated_liabilities_and_equity = _validated_value(
        validated_balance_sheet,
        "liabilities_and_equity",
    )

    validated_difference = _validated_value(
        validated_balance_sheet,
        "difference",
    )

    detailed_adjusted_equity = round(
        detailed_reported_equity
        + current_period_result,
        2,
    )

    detailed_liabilities_and_equity = round(
        detailed_liabilities
        + detailed_adjusted_equity,
        2,
    )

    detailed_difference = round(
        detailed_assets
        - detailed_liabilities_and_equity,
        2,
    )

    asset_difference = round(
        detailed_assets
        - validated_assets,
        2,
    )

    liability_difference = round(
        detailed_liabilities
        - validated_liabilities,
        2,
    )

    reported_equity_difference = round(
        detailed_reported_equity
        - validated_reported_equity,
        2,
    )

    adjusted_equity_difference = round(
        detailed_adjusted_equity
        - validated_adjusted_equity,
        2,
    )

    liabilities_and_equity_difference = round(
        detailed_liabilities_and_equity
        - validated_liabilities_and_equity,
        2,
    )

    accounting_equation_difference = round(
        detailed_difference
        - validated_difference,
        2,
    )

    reconciled = (
        asset_difference == 0.0
        and liability_difference == 0.0
        and reported_equity_difference == 0.0
        and adjusted_equity_difference == 0.0
        and liabilities_and_equity_difference == 0.0
        and accounting_equation_difference == 0.0
    )

    return {
        "status": (
            "available"
            if reconciled
            else "reconciliation_failed"
        ),
        "report_type": "balance_sheet",
        "title": "Balance Sheet",
        "reporting_basis": "as_of_date",
        "sections": [
            {
                "section": "Assets",
                "lines": asset_lines,
                "total": detailed_assets,
            },
            {
                "section": "Liabilities",
                "lines": liability_lines,
                "total": detailed_liabilities,
            },
            {
                "section": "Equity / Net Assets",
                "lines": equity_lines,
                "reported_equity": detailed_reported_equity,
                "current_period_result": current_period_result,
                "total": detailed_adjusted_equity,
            },
        ],
        "totals": {
            "assets": detailed_assets,
            "liabilities": detailed_liabilities,
            "reported_equity": detailed_reported_equity,
            "current_period_result": current_period_result,
            "equity": detailed_adjusted_equity,
            "liabilities_and_equity": (
                detailed_liabilities_and_equity
            ),
            "difference": detailed_difference,
        },
        "validated_totals": {
            "assets": validated_assets,
            "liabilities": validated_liabilities,
            "reported_equity": validated_reported_equity,
            "current_period_result": current_period_result,
            "equity": validated_adjusted_equity,
            "liabilities_and_equity": (
                validated_liabilities_and_equity
            ),
            "difference": validated_difference,
        },
        "reconciliation": {
            "reconciled": reconciled,
            "asset_difference": asset_difference,
            "liability_difference": liability_difference,
            "reported_equity_difference": (
                reported_equity_difference
            ),
            "adjusted_equity_difference": (
                adjusted_equity_difference
            ),
            "liabilities_and_equity_difference": (
                liabilities_and_equity_difference
            ),
            "accounting_equation_difference": (
                accounting_equation_difference
            ),
        },
        "controls": {
            "reporting_layer_only": True,
            "validated_balance_sheet_preserved": True,
            "financial_recalculation_performed": False,
            "trial_balance_is_detail_source": True,
            "posting_accounts_only": True,
            "balance_sheet_accounts_only": True,
            "missing_accounts_not_invented": True,
            "hierarchy_metadata_preserved": True,
            "current_period_result_preserved": True,
            "reconciliation_required": True,
        },
    }


def _build_report_lines(
    *,
    category: str,
    trial_balance: dict[str, dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build detailed posting-account lines while preserving
    Chart of Accounts hierarchy metadata.
    """

    lines: list[dict[str, Any]] = []

    for account_number, account in accounts_by_number.items():
        if account.get("financial_category") != category:
            continue

        if account.get("income_balance") != "Balance Sheet":
            continue

        if account.get("is_posting_account") is not True:
            continue

        normalized_account_number = str(
            account_number
        ).strip()

        balance_record = trial_balance.get(
            normalized_account_number,
            {},
        ) or {}

        debit = _to_float(
            balance_record.get(
                "total_debit"
            )
        )

        credit = _to_float(
            balance_record.get(
                "total_credit"
            )
        )

        normal_balance = account.get(
            "normal_balance"
        )

        if normal_balance == "Debit":
            amount = debit - credit

        elif normal_balance == "Credit":
            amount = credit - debit

        else:
            amount = 0.0

        lines.append(
            {
                "account_number": normalized_account_number,
                "account_name": str(
                    account.get("account_name")
                    or balance_record.get("account_name")
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
                "normal_balance": normal_balance,
                "amount": round(
                    amount,
                    2,
                ),
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
    because ERP Chart of Accounts numbering normally carries
    the intended reporting order.
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


def _validated_value(
    balance_sheet: dict[str, Any],
    key: str,
) -> float:
    return round(
        _to_float(
            balance_sheet.get(
                key
            )
        ),
        2,
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