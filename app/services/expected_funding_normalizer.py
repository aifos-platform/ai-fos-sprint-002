from __future__ import annotations

from datetime import date, datetime
from typing import Any


class ExpectedFundingNormalizer:
    """
    Normalize prospective / expected funding records.

    Expected Funding is intentionally separate from
    secured / available funding.

    It represents prospective funding that may or may not
    materialize and must never be treated as secured
    funding automatically.
    """

    def normalize_line(
        self,
        expected_funding_code: Any = None,
        funding_name: Any = None,
        donor_code: Any = None,
        donor_name: Any = None,
        stage: Any = None,
        probability_percentage: Any = None,
        minimum_amount: Any = None,
        most_likely_amount: Any = None,
        maximum_amount: Any = None,
        expected_decision_date: Any = None,
        expected_first_payment_date: Any = None,
        original_currency: Any = None,
        reporting_currency: Any = None,
        program_code: Any = None,
        project_code: Any = None,
        budget_line_code: Any = None,
        notes: Any = None,
    ) -> dict[str, Any]:
        """
        Normalize one Expected Funding record.
        """

        normalized_probability = (
            None
            if self._is_blank(
                probability_percentage
            )
            else self._to_float(
                probability_percentage
            )
        )

        normalized_minimum_amount = (
            None
            if self._is_blank(
                minimum_amount
            )
            else self._to_float(
                minimum_amount
            )
        )

        normalized_most_likely_amount = (
            None
            if self._is_blank(
                most_likely_amount
            )
            else self._to_float(
                most_likely_amount
            )
        )

        normalized_maximum_amount = (
            None
            if self._is_blank(
                maximum_amount
            )
            else self._to_float(
                maximum_amount
            )
        )

        requires_review = False
        review_reasons: list[str] = []

        if not self._clean(
            expected_funding_code
        ):
            requires_review = True

            review_reasons.append(
                "Missing expected funding code."
            )

        if normalized_probability is None:
            requires_review = True

            review_reasons.append(
                "Missing probability percentage."
            )

        elif not (
            0
            <= normalized_probability
            <= 100
        ):
            requires_review = True

            review_reasons.append(
                (
                    "Probability percentage must be "
                    "between 0 and 100."
                )
            )

        if normalized_most_likely_amount is None:
            requires_review = True

            review_reasons.append(
                "Missing most likely amount."
            )

        for amount in (
            normalized_minimum_amount,
            normalized_most_likely_amount,
            normalized_maximum_amount,
        ):
            if (
                amount is not None
                and amount < 0
            ):
                requires_review = True

                if (
                    "Expected funding amount cannot be negative."
                    not in review_reasons
                ):
                    review_reasons.append(
                        (
                            "Expected funding amount "
                            "cannot be negative."
                        )
                    )

        return {
            "expected_funding_code": self._clean(
                expected_funding_code
            ),
            "funding_name": self._clean(
                funding_name
            ),
            "donor_code": self._clean(
                donor_code
            ),
            "donor_name": self._clean(
                donor_name
            ),
            "stage": self._clean(
                stage
            ),
            "probability_percentage": (
                normalized_probability
            ),
            "minimum_amount": (
                normalized_minimum_amount
            ),
            "most_likely_amount": (
                normalized_most_likely_amount
            ),
            "maximum_amount": (
                normalized_maximum_amount
            ),
            "expected_decision_date": (
                self._normalize_date(
                    expected_decision_date
                )
            ),
            "expected_first_payment_date": (
                self._normalize_date(
                    expected_first_payment_date
                )
            ),
            "original_currency": self._clean(
                original_currency
            ),
            "reporting_currency": self._clean(
                reporting_currency
            ),
            "program_code": self._clean(
                program_code
            ),
            "project_code": self._clean(
                project_code
            ),
            "budget_line_code": self._clean(
                budget_line_code
            ),
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
            .replace("%", "")
            .strip()
        )

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

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _normalize_date(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value.date().isoformat()

        if isinstance(
            value,
            date,
        ):
            return value.isoformat()

        text = str(
            value
        ).strip()

        if not text:
            return None

        try:
            return datetime.fromisoformat(
                text
            ).date().isoformat()

        except ValueError:
            return text