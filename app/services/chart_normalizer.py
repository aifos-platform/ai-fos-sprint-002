from typing import Any


class ChartNormalizer:
    """
    Converts imported Chart of Accounts data into AI-FOS's
    standard internal structure and provides account lookups.
    """

    CATEGORY_ALIASES = {
        "asset": "Asset",
        "assets": "Asset",
        "liability": "Liability",
        "liabilities": "Liability",
        "equity": "Equity",
        "capital": "Equity",
        "income": "Revenue",
        "revenue": "Revenue",
        "revenues": "Revenue",
        "expense": "Expense",
        "expenses": "Expense",
        "cost of goods sold": "Expense",
    }

    NON_POSTING_TYPES = {
        "begin-total",
        "end-total",
        "heading",
        "total",
    }

    def __init__(self):
        self.accounts_by_number: dict[str, dict[str, Any]] = {}

    def normalize_account(
        self,
        account_number: str,
        account_name: str,
        parent_account: str | None = None,
        level: int | None = None,
        active: bool = True,
        financial_category: str | None = None,
        financial_subcategory: str | None = None,
        income_balance: str | None = None,
        account_type: str | None = None,
        totaling: str | None = None,
        liquidity_status: str | None = None,
        balance: float | None = None,
    ) -> dict[str, Any]:
        """
        Convert one imported ERP account into AI-FOS's standard structure.
        """

        normalized_category = self._normalize_category(
            financial_category
        )

        normalized_account_type = (
            str(account_type).strip()
            if account_type
            else None
        )

        is_posting_account = self._is_posting_account(
            normalized_account_type
        )

        normal_balance = self._determine_normal_balance(
            normalized_category
        )

        normalized_liquidity_status = (
            self._normalize_liquidity_status(
                liquidity_status
            )
        )

        return {
            "account_number": str(account_number).strip(),
            "account_name": str(account_name).strip(),
            "parent_account": parent_account,
            "level": level,
            "active": active,
            "financial_category": normalized_category,
            "financial_subcategory": (
                str(financial_subcategory).strip()
                if financial_subcategory
                else None
            ),
            "income_balance": (
                str(income_balance).strip()
                if income_balance
                else None
            ),
            "account_type": normalized_account_type,
            "totaling": (
                str(totaling).strip()
                if totaling
                else None
            ),
            "normal_balance": normal_balance,
            "is_posting_account": is_posting_account,
            "liquidity_status": normalized_liquidity_status,
            "balance": balance,
            "classification_confidence": (
                1.0 if normalized_category else None
            ),
            "requires_review": normalized_category is None,
        }

    def register_accounts(
        self,
        accounts: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """
        Store normalized accounts by account number for fast lookup.
        """

        self.accounts_by_number = {
            str(account["account_number"]).strip(): account
            for account in accounts
            if account.get("account_number")
        }

        return self.accounts_by_number

    def get_account(
        self,
        account_number: str,
    ) -> dict[str, Any] | None:
        """
        Return an imported account using its account number.
        """

        normalized_number = str(account_number).strip()

        return self.accounts_by_number.get(normalized_number)

    def get_all_accounts(self) -> dict[str, dict[str, Any]]:
        """
        Return all registered accounts.
        """

        return self.accounts_by_number

    def _normalize_category(
        self,
        category: str | None,
    ) -> str | None:
        """
        Convert ERP category labels into AI-FOS category labels.
        """

        if not category:
            return None

        normalized_value = str(category).strip().lower()

        return self.CATEGORY_ALIASES.get(normalized_value)

    def _normalize_liquidity_status(
        self,
        liquidity_status: str | None,
    ) -> str | None:
        """
        Normalize imported liquidity-status labels into
        AI-FOS canonical values.
        """

        if not liquidity_status:
            return None

        normalized_value = (
            str(liquidity_status)
            .strip()
            .lower()
        )

        aliases = {
            "available": "Available",
            "blocked": "Blocked",
            "not applicable": "Not Applicable",
            "n/a": "Not Applicable",
            "na": "Not Applicable",
        }

        return aliases.get(normalized_value)    
    
    def _is_posting_account(
        self,
        account_type: str | None,
    ) -> bool | None:
        """
        Determine whether transactions may be posted to the account.
        """

        if not account_type:
            return None

        normalized_type = account_type.strip().lower()

        return normalized_type not in self.NON_POSTING_TYPES

    def _determine_normal_balance(
        self,
        category: str | None,
    ) -> str | None:
        """
        Determine the usual debit or credit balance by category.
        """

        if category in {"Asset", "Expense"}:
            return "Debit"

        if category in {"Liability", "Equity", "Revenue"}:
            return "Credit"

        return None