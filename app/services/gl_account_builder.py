from typing import Any

from app.services.account_classifier import classify_account
from app.services.chart_normalizer import ChartNormalizer


class GLAccountBuilder:
    """
    Build a minimal Chart of Accounts from normalized General Ledger
    transactions when no explicit Chart of Accounts has been supplied.
    """

    def __init__(self) -> None:
        self.normalizer = ChartNormalizer()

    def build(
        self,
        transactions: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        accounts: list[dict[str, Any]] = []
        seen_account_numbers: set[str] = set()

        for transaction in transactions or []:
            account_number = str(
                transaction.get("account_number") or ""
            ).strip()

            if not account_number:
                continue

            if account_number in seen_account_numbers:
                continue

            account_name = str(
                transaction.get("account_name") or ""
            ).strip()

            classification = classify_account(
                account_number=account_number,
                account_name=account_name,
            )

            account = self.normalizer.normalize_account(
                account_number=account_number,
                account_name=account_name,
                financial_category=classification.get(
                    "financial_category"
                ),
                financial_subcategory=classification.get(
                    "financial_subcategory"
                ),
                account_type="Posting",
            )

            account["normal_balance"] = classification.get(
                "normal_balance"
            )
            account["classification_confidence"] = (
                classification.get(
                    "classification_confidence"
                )
            )
            account["requires_review"] = (
                not account.get("financial_category")
                or account.get("financial_category")
                == "Unknown"
            )

            accounts.append(account)
            seen_account_numbers.add(account_number)

        accounts_by_number = self.normalizer.register_accounts(
            accounts
        )

        return {
            "accounts": accounts,
            "accounts_by_number": accounts_by_number,
        }
