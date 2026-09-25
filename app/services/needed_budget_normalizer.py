from __future__ import annotations

from typing import Any


class NeededBudgetNormalizer:
    """
    Normalize organisation-level annual budget needs.

    Needed Budget is intentionally separate from
    grant/available budget because it represents what
    the organisation requires for a fiscal year,
    regardless of whether funding has been secured.

    It therefore does not require:
    - Fund Code
    - Donor Code
    - Donor Line Code
    """

    def normalize_line(
        self,
        program_code: Any = None,
        program_name: Any = None,
        category_code: Any = None,
        category_name: Any = None,
        budget_line_code: Any = None,
        budget_line_name: Any = None,
        budget_notes: Any = None,
        employee_responsible: Any = None,
        fiscal_year: Any = None,
        needed_budget: Any = None,
    ) -> dict[str, Any]:
        """
        Normalize one Needed Budget row.
        """

        normalized_year = self._to_int(
            fiscal_year
        )

        normalized_amount = (
            None
            if self._is_blank(
                needed_budget
            )
            else self._to_float(
                needed_budget
            )
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

        if normalized_year is None:
            requires_review = True

            review_reasons.append(
                "Missing fiscal year."
            )

        if normalized_amount is None:
            requires_review = True

            review_reasons.append(
                "Missing needed budget amount."
            )

        if (
            normalized_amount is not None
            and normalized_amount < 0
        ):
            requires_review = True

            review_reasons.append(
                "Needed budget contains a negative amount."
            )

        return {
            "program_code": self._clean(
                program_code
            ),
            "program_name": self._clean(
                program_name
            ),
            "category_code": self._clean(
                category_code
            ),
            "category_name": self._clean(
                category_name
            ),
            "budget_line_code": self._clean(
                budget_line_code
            ),
            "budget_line_name": self._clean(
                budget_line_name
            ),
            "budget_notes": self._clean(
                budget_notes
            ),
            "employee_responsible": self._clean(
                employee_responsible
            ),
            "fiscal_year": normalized_year,
            "needed_budget": normalized_amount,
            "requires_review": requires_review,
            "review_reasons": review_reasons,
        }

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
    def _to_float(
        value: Any,
    ) -> float:

        if value is None:
            return 0.0

        if isinstance(
            value,
            (int, float),
        ):
            return float(
                value
            )

        text = (
            str(value)
            .replace(",", "")
            .replace("$", "")
            .strip()
        )

        if not text:
            return 0.0

        if (
            text.startswith("(")
            and text.endswith(")")
        ):
            text = (
                "-"
                + text[1:-1]
            )

        try:
            return float(
                text
            )

        except ValueError:
            return 0.0

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int | None:

        if value is None:
            return None

        if isinstance(
            value,
            int,
        ):
            return value

        if isinstance(
            value,
            float,
        ):
            return int(
                value
            )

        text = str(
            value
        ).strip()

        if not text:
            return None

        try:
            return int(
                float(text)
            )

        except ValueError:
            return None