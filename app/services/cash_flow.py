from collections import defaultdict
from typing import Any

CASH_SUBCATEGORIES = {
    "cash",
    "bank",
    "cash and bank",
    "cash & bank",
    "cash and cash equivalents",
}

FINANCING_KEYWORDS = {
    "loan",
    "borrowing",
    "debt",
    "finance lease",
    "capital",
    "share capital",
    "equity",
}

INVESTING_KEYWORDS = {
    "fixed asset",
    "property",
    "equipment",
    "furniture",
    "vehicle",
    "software",
    "intangible",
    "investment",
    "asset acquisition",
}


def generate_cash_flow_statement(
    transactions: list[dict[str, Any]],
    trial_balance: dict[str, dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate a transaction-level cash-flow report.

    Transactions are grouped by document number. Cash movements are
    classified using the financial metadata of their counter-accounts.
    """

    operating_activities = 0.0
    investing_activities = 0.0
    financing_activities = 0.0
    unclassified_activities = 0.0

    activity_details: list[dict[str, Any]] = []
    documents: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for index, transaction in enumerate(transactions):
        document_number = str(transaction.get("document_no") or "").strip()

        if not document_number:
            document_number = f"UNIDENTIFIED-{index}"

        documents[document_number].append(transaction)

    for document_number, document_lines in documents.items():
        cash_lines: list[dict[str, Any]] = []
        counter_lines: list[dict[str, Any]] = []

        for line in document_lines:
            account_number = str(line.get("account") or "").strip()

            metadata = accounts_by_number.get(account_number)

            if metadata is None:
                counter_lines.append(line)
                continue

            if _is_cash_account(metadata):
                cash_lines.append(line)
            else:
                counter_lines.append(line)

        if not cash_lines:
            continue

        cash_movement = sum(
            _to_float(line.get("debit")) - _to_float(line.get("credit"))
            for line in cash_lines
        )

        if abs(cash_movement) < 0.005:
            continue

        activity = _classify_document(
            counter_lines=counter_lines,
            accounts_by_number=accounts_by_number,
        )

        if activity == "Operating":
            operating_activities += cash_movement
        elif activity == "Investing":
            investing_activities += cash_movement
        elif activity == "Financing":
            financing_activities += cash_movement
        else:
            unclassified_activities += cash_movement

        activity_details.append(
            {
                "document_no": document_number,
                "transaction_date": _first_value(
                    document_lines,
                    "transaction_date",
                ),
                "description": _first_value(
                    document_lines,
                    "description",
                ),
                "activity": activity,
                "cash_movement": round(cash_movement, 2),
                "cash_accounts": _account_numbers(cash_lines),
                "counter_accounts": _account_numbers(counter_lines),
            }
        )

    cash_accounts = _build_cash_account_summary(
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    net_change_in_cash = sum(account["net_movement"] for account in cash_accounts)

    classified_net_change = (
        operating_activities
        + investing_activities
        + financing_activities
        + unclassified_activities
    )

    return {
        "method": "transaction_counter_account_analysis",
        "operating_activities": round(
            operating_activities,
            2,
        ),
        "investing_activities": round(
            investing_activities,
            2,
        ),
        "financing_activities": round(
            financing_activities,
            2,
        ),
        "unclassified_activities": round(
            unclassified_activities,
            2,
        ),
        "classified_net_change": round(
            classified_net_change,
            2,
        ),
        "net_change_in_cash": round(
            net_change_in_cash,
            2,
        ),
        "reconciliation_difference": round(
            net_change_in_cash - classified_net_change,
            2,
        ),
        "cash_accounts": cash_accounts,
        "activity_details": activity_details[:100],
        "activity_detail_count": len(activity_details),
        "document_count": len(documents),
        "classified_document_count": sum(
            detail["activity"] != "Unclassified" for detail in activity_details
        ),
        "unclassified_document_count": sum(
            detail["activity"] == "Unclassified" for detail in activity_details
        ),
        "note": (
            "This is a first transaction-level classification. "
            "Documents with mixed or unclear counter-accounts remain "
            "unclassified for review."
        ),
    }


def _classify_document(
    counter_lines: list[dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> str:
    classifications: set[str] = set()

    for line in counter_lines:
        account_number = str(line.get("account") or "").strip()

        metadata = accounts_by_number.get(account_number)

        if metadata is None:
            continue

        category = str(metadata.get("financial_category") or "").strip()

        subcategory = str(metadata.get("financial_subcategory") or "").strip()

        account_name = str(
            metadata.get("account_name") or line.get("account_name") or ""
        ).strip()

        searchable_text = (f"{subcategory} {account_name}").lower()

        if category == "Equity":
            classifications.add("Financing")

        elif category == "Liability":
            if _contains_keyword(
                searchable_text,
                FINANCING_KEYWORDS,
            ):
                classifications.add("Financing")
            else:
                classifications.add("Operating")

        elif category == "Asset":
            if _contains_keyword(
                searchable_text,
                INVESTING_KEYWORDS,
            ):
                classifications.add("Investing")
            else:
                classifications.add("Operating")

        elif category in {"Revenue", "Expense"}:
            classifications.add("Operating")

    if len(classifications) == 1:
        return classifications.pop()

    return "Unclassified"


def _is_cash_account(
    metadata: dict[str, Any],
) -> bool:
    category = str(metadata.get("financial_category") or "").strip()

    subcategory = str(metadata.get("financial_subcategory") or "").strip().lower()

    account_name = str(metadata.get("account_name") or "").strip().lower()

    if category != "Asset":
        return False

    if subcategory in CASH_SUBCATEGORIES:
        return True

    return (
        "cash in hand" in account_name
        or "petty cash" in account_name
        or account_name.startswith("bank")
        or account_name.startswith("banks")
    )


def _build_cash_account_summary(
    trial_balance: dict[str, dict[str, Any]],
    accounts_by_number: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    cash_accounts: list[dict[str, Any]] = []

    for account_number, balance_record in trial_balance.items():
        normalized_number = str(account_number).strip()
        metadata = accounts_by_number.get(normalized_number)

        if metadata is None:
            continue

        if not _is_cash_account(metadata):
            continue

        debit = _to_float(balance_record.get("total_debit"))

        credit = _to_float(balance_record.get("total_credit"))

        cash_accounts.append(
            {
                "account_number": normalized_number,
                "account_name": metadata.get("account_name"),
                "financial_subcategory": metadata.get("financial_subcategory"),
                "debit": round(debit, 2),
                "credit": round(credit, 2),
                "net_movement": round(
                    debit - credit,
                    2,
                ),
            }
        )

    return cash_accounts


def _account_numbers(
    lines: list[dict[str, Any]],
) -> list[str]:
    return sorted(
        {
            str(line.get("account") or "").strip()
            for line in lines
            if line.get("account")
        }
    )


def _first_value(
    lines: list[dict[str, Any]],
    field_name: str,
) -> Any:
    for line in lines:
        value = line.get(field_name)

        if value not in {None, ""}:
            return value

    return None


def _contains_keyword(
    text: str,
    keywords: set[str],
) -> bool:
    return any(keyword in text for keyword in keywords)


def _to_float(value: Any) -> float:
    if value in {None, ""}:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
