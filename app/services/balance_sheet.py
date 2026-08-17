from typing import Any


def generate_balance_sheet(
    trial_balance: dict[str, dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
    current_period_result: float = 0,
) -> dict[str, float]:
    """
    Generate the Balance Sheet from the Trial Balance.

    Current-period profit or loss is included in equity
    so the accounting equation remains complete before
    year-end closing entries are posted.
    """

    assets = 0
    liabilities = 0
    equity = 0

    for account_number, balance_record in trial_balance.items():
        imported_account = accounts_by_number.get(
            str(account_number).strip()
        )

        if imported_account is None:
            continue

        if imported_account.get("is_posting_account") is False:
            continue

        category = imported_account.get(
            "financial_category"
        )

        normal_balance = imported_account.get(
            "normal_balance"
        )

        debit = (
            balance_record.get(
                "total_debit",
                0,
            )
            or 0
        )

        credit = (
            balance_record.get(
                "total_credit",
                0,
            )
            or 0
        )

        if normal_balance == "Debit":
            balance = debit - credit

        elif normal_balance == "Credit":
            balance = credit - debit

        else:
            continue

        if category == "Asset":
            assets += balance

        elif category == "Liability":
            liabilities += balance

        elif category == "Equity":
            equity += balance

    reported_equity = equity

    adjusted_equity = (
        reported_equity
        + current_period_result
    )

    liabilities_and_equity = (
        liabilities
        + adjusted_equity
    )

    return {
        "assets": round(
            assets,
            2,
        ),
        "liabilities": round(
            liabilities,
            2,
        ),
        "reported_equity": round(
            reported_equity,
            2,
        ),
        "current_period_result": round(
            current_period_result,
            2,
        ),
        "equity": round(
            adjusted_equity,
            2,
        ),
        "liabilities_and_equity": round(
            liabilities_and_equity,
            2,
        ),
        "difference": round(
            assets
            - liabilities_and_equity,
            2,
        ),
    }