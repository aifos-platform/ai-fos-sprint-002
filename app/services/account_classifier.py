from typing import Optional


VALID_CATEGORIES = {
    "Asset",
    "Liability",
    "Equity",
    "Revenue",
    "Expense",
    "Unknown",
}


def classify_account(
    account_number: Optional[str],
    account_name: Optional[str] = None,
) -> dict[str, str | float | None]:
    """
    Temporarily classify an account according to the current organization's
    Chart of Accounts structure.

    Later, these values will come from the organization's imported
    Chart of Accounts rather than fixed numbering rules.
    """

    number = str(account_number or "").strip()
    name = str(account_name or "").strip().lower()

    result: dict[str, str | float | None] = {
        "financial_category": "Unknown",
        "financial_subcategory": None,
        "normal_balance": None,
        "classification_confidence": 0.0,
    }

    if not number:
        return result

    first_digit = number[0]

    if first_digit == "1":
        result.update(
            {
                "financial_category": "Equity",
                "financial_subcategory": "Capital and Equity",
                "normal_balance": "Credit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "2":
        result.update(
            {
                "financial_category": "Asset",
                "financial_subcategory": "Other Assets",
                "normal_balance": "Debit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "3":
        result.update(
            {
                "financial_category": "Asset",
                "financial_subcategory": "Inventory",
                "normal_balance": "Debit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "4":
        result.update(
            {
                "financial_category": "Liability",
                "financial_subcategory": "Liabilities",
                "normal_balance": "Credit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "5":
        result.update(
            {
                "financial_category": "Asset",
                "financial_subcategory": "Cash and Bank",
                "normal_balance": "Debit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "6":
        result.update(
            {
                "financial_category": "Expense",
                "financial_subcategory": "Operating Expenses",
                "normal_balance": "Debit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "7":
        result.update(
            {
                "financial_category": "Revenue",
                "financial_subcategory": "Revenue",
                "normal_balance": "Credit",
                "classification_confidence": 1.0,
            }
        )

    elif first_digit == "8":
        result.update(
            {
                "financial_category": "Unknown",
                "financial_subcategory": "Unused",
                "normal_balance": None,
                "classification_confidence": 1.0,
            }
        )
    return result