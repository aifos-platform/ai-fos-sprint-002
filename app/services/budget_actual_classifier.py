from __future__ import annotations

from typing import Any


class BudgetActualClassifier:
    """
    Determine how a General Ledger transaction should
    be treated for Budget and Grant reporting.

    Accounting treatment and budget treatment are kept
    separate intentionally.

    Examples:
    - Normal expense -> budget consuming
    - Capital asset purchase -> budget consuming
    - Year-end closing entry -> not budget consuming
    - Depreciation/amortization -> normally not budget consuming
    - Revenue -> not budget consuming
    """

    CLOSING_PATTERNS = (
        "close income statement",
        "closing income statement",
        "income statement closing",
        "close profit and loss",
        "profit and loss closing",
        "p&l closing",
        "year end closing",
        "year-end closing",
        "closing entry",
        "close expense accounts",
        "close revenue accounts",
    )

    DEPRECIATION_PATTERNS = (
        "depreciation",
        "amortization",
        "amortisation",
    )

    def classify(
        self,
        transaction: dict[str, Any],
        accounts_by_number: dict[
            str,
            dict[str, Any],
        ]
        | None = None,
    ) -> dict[str, Any]:
        """
        Classify one GL transaction for Budget Actual.
        """

        accounts_by_number = (
            accounts_by_number or {}
        )

        account_number = self._clean(
            transaction.get("account_number")
            or transaction.get("account")
        )

        account_name = self._clean(
            transaction.get("account_name")
        )

        description = self._clean(
            transaction.get("description")
        )

        document_type = self._clean(
            transaction.get("document_type")
        )

        combined_text = " ".join(
            value
            for value in [
                account_name,
                description,
                document_type,
            ]
            if value
        ).lower()

        account = (
            accounts_by_number.get(
                account_number or "",
                {},
            )
        )

        financial_category = self._clean(
            account.get("financial_category")
            or account.get("category")
        )

        financial_subcategory = self._clean(
            account.get("financial_subcategory")
            or account.get("subcategory")
        )

        financial_category_lower = (
            financial_category.lower()
            if financial_category
            else ""
        )

        financial_subcategory_lower = (
            financial_subcategory.lower()
            if financial_subcategory
            else ""
        )

        is_closing_entry = any(
            pattern in combined_text
            for pattern in self.CLOSING_PATTERNS
        )

        is_depreciation = any(
            pattern in combined_text
            for pattern in self.DEPRECIATION_PATTERNS
        )

        is_expense = (
            financial_category_lower
            == "expense"
        )

        is_asset = (
            financial_category_lower
            == "asset"
        )

        is_revenue = (
            financial_category_lower
            == "revenue"
        )

        budget_line_code = self._clean(
            transaction.get(
                "budget_line_code"
            )
            or transaction.get(
                "budget_line"
            )
        )

        amount = self._movement_amount(
            transaction
        )

        #
        # Closing entries
        #
        if is_closing_entry:
            return self._result(
                is_budget_consuming=False,
                budget_actual_amount=0.0,
                treatment="closing_entry",
                reason=(
                    "Year-end or income-statement "
                    "closing entry."
                ),
                is_closing_entry=True,
                account_category=financial_category,
                budget_line_code=budget_line_code,
            )

        #
        # Depreciation / amortization
        #
        if is_depreciation:
            return self._result(
                is_budget_consuming=False,
                budget_actual_amount=0.0,
                treatment="depreciation",
                reason=(
                    "Depreciation or amortization "
                    "does not consume budget when "
                    "the capital purchase is already "
                    "recognized as budget spending."
                ),
                is_closing_entry=False,
                account_category=financial_category,
                budget_line_code=budget_line_code,
            )

        #
        # Expense accounts
        #
        if is_expense:
            return self._result(
                is_budget_consuming=True,
                budget_actual_amount=amount,
                treatment="operating_expense",
                reason=(
                    "Expense transaction consumes "
                    "budget."
                ),
                is_closing_entry=False,
                account_category=financial_category,
                budget_line_code=budget_line_code,
            )

        #
        # Capital asset purchases
        #
        capital_asset_subcategories = {
            "equipment",
            "fixed asset",
            "fixed assets",
            "furniture",
            "vehicle",
            "vehicles",
            "computer equipment",
            "office equipment",
            "leasehold improvement",
            "leasehold improvements",
        }

        is_capital_asset = (
            is_asset
            and financial_subcategory_lower
            in capital_asset_subcategories
        )

        if is_capital_asset and budget_line_code:
            return self._result(
                is_budget_consuming=True,
                budget_actual_amount=amount,
                treatment="capital_purchase",
                reason=(
                    "Capital asset transaction carries a "
                    "Budget Line and is treated as "
                    "capital budget expenditure."
                ),
                is_closing_entry=False,
                account_category=financial_category,
                budget_line_code=budget_line_code,
            )
        
        #
        # Revenue
        #
        if is_revenue:
            return self._result(
                is_budget_consuming=False,
                budget_actual_amount=0.0,
                treatment="revenue",
                reason=(
                    "Revenue does not represent "
                    "budget expenditure."
                ),
                is_closing_entry=False,
                account_category=financial_category,
                budget_line_code=budget_line_code,
            )

        #
        # Unknown / other accounting entries
        #
        return self._result(
            is_budget_consuming=False,
            budget_actual_amount=0.0,
            treatment="non_budget",
            reason=(
                "Transaction is not currently "
                "classified as budget-consuming."
            ),
            is_closing_entry=False,
            account_category=financial_category,
            budget_line_code=budget_line_code,
        )

    @staticmethod
    def _movement_amount(
        transaction: dict[str, Any],
    ) -> float:
        """
        Return debit minus credit when available.
        """

        debit = BudgetActualClassifier._to_float(
            transaction.get("debit_amount")
            if transaction.get(
                "debit_amount"
            )
            is not None
            else transaction.get("debit")
        )

        credit = BudgetActualClassifier._to_float(
            transaction.get("credit_amount")
            if transaction.get(
                "credit_amount"
            )
            is not None
            else transaction.get("credit")
        )

        if (
            debit != 0.0
            or credit != 0.0
        ):
            return debit - credit

        return BudgetActualClassifier._to_float(
            transaction.get("amount")
        )

    @staticmethod
    def _result(
        is_budget_consuming: bool,
        budget_actual_amount: float,
        treatment: str,
        reason: str,
        is_closing_entry: bool,
        account_category: str | None,
        budget_line_code: str | None,
    ) -> dict[str, Any]:

        return {
            "is_budget_consuming": (
                is_budget_consuming
            ),
            "budget_actual_amount": round(
                budget_actual_amount,
                2,
            ),
            "budget_treatment": treatment,
            "reason": reason,
            "is_closing_entry": (
                is_closing_entry
            ),
            "account_category": (
                account_category
            ),
            "budget_line_code": (
                budget_line_code
            ),
        }

    @staticmethod
    def _clean(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        cleaned = str(value).strip()

        return cleaned or None

    @staticmethod
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