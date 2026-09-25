from __future__ import annotations

from typing import Any


class CoreCostCoverageNormalizer:
    """
    Normalize Core Cost Coverage input records.
    """

    def normalize_line(
        self,
        coverage_type: Any = None,
        fund_code: Any = None,
        budget_line_code: Any = None,
        amount: Any = None,
    ) -> dict[str, Any]:
        """
        Normalize one Core Cost Coverage record.
        """
        normalized_coverage_type = self._normalize_text(
            coverage_type
        )

        allowed_coverage_types = {
            "direct_grant_coverage",
            "indirect_recovery_allocation",
            "unrestricted_core_funding",
            "available_indirect_recovery",
            "used_indirect_recovery",
        }

        requires_review = False
        review_reasons = []

        if normalized_coverage_type is None:
            requires_review = True
            review_reasons.append(
                "Missing coverage type."
            )

        elif (
            normalized_coverage_type
            not in allowed_coverage_types
        ):
            requires_review = True
            review_reasons.append(
                "Unknown coverage type."
            )            

        if amount is None or (
            isinstance(amount, str)
            and not amount.strip()
        ):
            requires_review = True
            review_reasons.append(
                "Missing amount."
            )

        normalized_amount = self._to_float(
            amount
        )

        amount_is_invalid = False

        if not (
            amount is None
            or (
                isinstance(amount, str)
                and not amount.strip()
            )
        ):
            try:
                float(amount)
            except (TypeError, ValueError):
                amount_is_invalid = True

        if amount_is_invalid:
            requires_review = True
            review_reasons.append(
                "Invalid amount."
            )

        if normalized_amount < 0:
            requires_review = True
            review_reasons.append(
                "Core cost coverage amount cannot be negative."
            ) 

        normalized_fund_code = self._normalize_text(
            fund_code
        )

        if (
            normalized_coverage_type
            in {
                "direct_grant_coverage",
                "indirect_recovery_allocation",
                "unrestricted_core_funding",
                "available_indirect_recovery",
            }
            and normalized_fund_code is None
        ):
            requires_review = True
            review_reasons.append(
                "Missing fund code."
            )          

        normalized_budget_line_code = self._normalize_text(
            budget_line_code
        )

        if (
            normalized_coverage_type
            in {
                "direct_grant_coverage",
                "indirect_recovery_allocation",
                "unrestricted_core_funding",
                "used_indirect_recovery",
            }
            and normalized_budget_line_code is None
        ):
            requires_review = True
            review_reasons.append(
                "Missing budget line code."
            )                    

        return {
            "coverage_type": normalized_coverage_type,
            
            "fund_code": normalized_fund_code,
            "budget_line_code": normalized_budget_line_code,
            "amount": normalized_amount,
            "requires_review": requires_review,
            "review_reasons": review_reasons,
        }

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0