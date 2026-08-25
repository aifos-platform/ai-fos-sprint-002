from __future__ import annotations

from typing import Any


class BudgetNormalizer:
    """
    Converts imported budget rows into the
    AI-FOS canonical budget model.

    Budget dimensions intentionally use the same
    canonical field names as FACT_GL wherever possible
    so Budget vs Actual analysis can join directly
    across the financial model.
    """

    def normalize_line(
        self,
        account_number: str | None = None,
        budget_line_code: str | None = None,
        budget_line_name: str | None = None,
        original_budget: float | int | str | None = None,
        remaining_secured_budget: float | int | str | None = None,
        revised_budget: float | int | str | None = None,
     

        # Canonical dimensions
        fund_code: str | None = None,
        donor_code: str | None = None,
        program_code: str | None = None,
        category_code: str | None = None,
        donor_line_code: str | None = None,
        project_code: str | None = None,

        # Descriptive fields
        fund_name: str | None = None,
        donor_name: str | None = None,
        program_name: str | None = None,
        category_name: str | None = None,
        project_name: str | None = None,
        grant_start_date: Any = None,
        grant_end_date: Any = None, 

        # Currency / period
        original_currency: str | None = None,
        reporting_currency: str | None = None,
        exchange_rate: float | int | str | None = None,
        current_budget_usd: float | int | str | None = None,
        fiscal_year: int | str | None = None,
        period_amounts: list[dict[str, Any]] | None = None,

        notes: str | None = None,

        # Backward-compatible aliases
        fund: str | None = None,
        donor: str | None = None,
        project: str | None = None,
    ) -> dict[str, Any]:
        """
        Normalize one imported budget row.
        """

        resolved_fund_code = self._clean(
            fund_code or fund
        )

        resolved_donor_code = self._clean(
            donor_code or donor
        )

        resolved_project_code = self._clean(
            project_code or project
        )

        original_amount = self._to_float(
            original_budget
        )

        remaining_secured_amount = (
            self._to_float(
                remaining_secured_budget
            )
            if not self._is_blank(
                remaining_secured_budget
            )
            else None
        )        

        revised_amount = (
            self._to_float(revised_budget)
            if not self._is_blank(revised_budget)
            else original_amount
        )

        normalized_exchange_rate = (
            self._to_float(exchange_rate)
            if not self._is_blank(exchange_rate)
            else None
        )

        normalized_current_budget_usd = (
            self._to_float(current_budget_usd)
            if not self._is_blank(current_budget_usd)
            else None
        )

        normalized_period_amounts: list[
            dict[str, Any]
        ] = []

        for period_amount in (
            period_amounts or []
        ):
            normalized_period_amounts.append(
                {
                    "header": self._clean(
                        period_amount.get(
                            "header"
                        )
                    ),
                    "type": self._clean(
                        period_amount.get(
                            "type"
                        )
                    ),
                    "fiscal_year": self._to_int(
                        period_amount.get(
                            "fiscal_year"
                        )
                    ),
                    "amount": (
                        None
                        if self._is_blank(
                            period_amount.get(
                                "amount"
                            )
                        )
                        else self._to_float(
                            period_amount.get(
                                "amount"
                            )
                        )
                    ),
                }
            )

        requires_review = False
        review_reasons: list[str] = []

        if not self._clean(
            budget_line_code
        ):
            requires_review = True

            review_reasons.append(
                "Missing budget line code."
            )

        if not resolved_fund_code:
            requires_review = True

            review_reasons.append(
                "Missing fund code."
            )

        if (
            revised_amount < 0
            or original_amount < 0
        ):
            review_reasons.append(
                "Budget contains a negative amount."
            )

        return {
            # Core identifiers
            "account_number": self._clean(
                account_number
            ),
            "budget_line_code": self._clean(
                budget_line_code
            ),
            "budget_line_name": self._clean(
                budget_line_name
            ),

            # Canonical dimensions
            "fund_code": resolved_fund_code,
            "donor_code": resolved_donor_code,
            "program_code": self._clean(
                program_code
            ),
            "category_code": self._clean(
                category_code
            ),
            "donor_line_code": self._clean(
                donor_line_code
            ),
            "project_code": (
                resolved_project_code
            ),

            # Descriptive attributes
            "fund_name": self._clean(
                fund_name
            ),
            "donor_name": self._clean(
                donor_name
            ),
            "program_name": self._clean(
                program_name
            ),
            "category_name": self._clean(
                category_name
            ),
            "project_name": self._clean(
                project_name
            ),

            # Budget amounts
            "original_budget": (
                original_amount
            ),

            "remaining_secured_budget": (
                remaining_secured_amount
            ),

            "revised_budget": (
                revised_amount
            ),
            "current_budget": (
                revised_amount
            ),
            "current_budget_usd": (
                normalized_current_budget_usd
            ),

            # Currency
            "original_currency": self._clean(
                original_currency
            ),
            "reporting_currency": self._clean(
                reporting_currency
            ),
            "exchange_rate": (
                normalized_exchange_rate
            ),

            # Grant period
            "grant_start_date": self._normalize_date(
                grant_start_date
            ),
            "grant_end_date": self._normalize_date(
                grant_end_date
            ),

            # Period
            "fiscal_year": self._to_int(
                fiscal_year
            ),
            "period_amounts": (
                normalized_period_amounts
            ),

            # Data quality
            "notes": self._clean(
                notes
            ),
            "requires_review": (
                requires_review
            ),
            "review_reasons": (
                review_reasons
            ),
        }

    @staticmethod
    def _is_blank(
        value: Any,
    ) -> bool:
        if value is None:
            return True

        if isinstance(
            value,
            str,
        ):
            return not value.strip()

        return False

    @staticmethod
    def _clean(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(
            value
        ).strip()

        if not cleaned:
            return None

        if cleaned.lower() in {
            "none",
            "null",
            "nan",
        }:
            return None

        return cleaned

    @staticmethod
    def _normalize_date(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if hasattr(value, "date"):
            try:
                return value.date().isoformat()
            except Exception:
                pass

        if hasattr(value, "isoformat"):
            try:
                return value.isoformat()
            except Exception:
                pass

        text = str(value).strip()

        if not text:
            return None

        if text.lower() in {
            "none",
            "null",
            "nan",
        }:
            return None

        return text    

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float:
        if value is None:
            return 0.0

        if isinstance(
            value,
            str,
        ):
            cleaned = (
                value
                .replace(
                    ",",
                    "",
                )
                .replace(
                    "$",
                    "",
                )
                .strip()
            )

            if not cleaned:
                return 0.0

            if (
                cleaned.startswith("(")
                and cleaned.endswith(")")
            ):
                cleaned = (
                    "-"
                    + cleaned[1:-1]
                )

            value = cleaned

        try:
            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int | None:
        if value is None:
            return None

        if isinstance(
            value,
            str,
        ):
            value = value.strip()

            if not value:
                return None

        try:
            return int(
                float(
                    value
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            return None