from __future__ import annotations

from collections import defaultdict
from typing import Any


class BudgetPeriodResolver:
    """
    Resolve dynamic, period-aware Budget amounts into
    a canonical AI-FOS structure.

    This service intentionally separates:

    - approved / budget amounts
    - requested / required amounts
    - spending plans
    - forecasts

    It does not assume that these concepts are
    financially interchangeable.

    Example source headings:

    - Requested 2026
    - Required Funding FY26
    - Spending Plan (2027)
    - FY28 Budget
    - Approved Allocation 2029
    - Forecast 2030
    """

    def resolve_line(
        self,
        budget_line: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve one normalized Budget line into
        year-aware semantic amounts.
        """

        period_amounts = (
            budget_line.get(
                "period_amounts"
            )
            or []
        )

        resolved_periods: list[
            dict[str, Any]
        ] = []

        by_year: dict[
            int,
            dict[str, list[dict[str, Any]]],
        ] = defaultdict(
            lambda: defaultdict(list)
        )

        for period_amount in period_amounts:

            fiscal_year = self._to_int(
                period_amount.get(
                    "fiscal_year"
                )
            )

            period_type = self._clean(
                period_amount.get(
                    "type"
                )
            )

            header = self._clean(
                period_amount.get(
                    "header"
                )
            )

            amount = self._nullable_float(
                period_amount.get(
                    "amount"
                )
            )

            if fiscal_year is None:
                continue

            if not period_type:
                continue

            resolved = {
                "header": header,
                "type": period_type,
                "fiscal_year": fiscal_year,
                "amount": amount,
            }

            resolved_periods.append(
                resolved
            )

            by_year[
                fiscal_year
            ][
                period_type
            ].append(
                resolved
            )

        canonical_by_year: dict[
            int,
            dict[str, Any],
        ] = {}

        for (
            fiscal_year,
            type_groups,
        ) in by_year.items():

            canonical_by_year[
                fiscal_year
            ] = {
                "requested": self._resolve_type_amount(
                    type_groups.get(
                        "requested",
                        [],
                    )
                ),
                "spending_plan": self._resolve_type_amount(
                    type_groups.get(
                        "spending_plan",
                        [],
                    )
                ),
                "budget": self._resolve_type_amount(
                    type_groups.get(
                        "budget",
                        [],
                    )
                ),
                "forecast": self._resolve_type_amount(
                    type_groups.get(
                        "forecast",
                        [],
                    )
                ),
            }

        return {
            "periods": resolved_periods,
            "by_year": canonical_by_year,
        }

    def get_year(
        self,
        budget_line: dict[str, Any],
        fiscal_year: int,
    ) -> dict[str, Any]:
        """
        Return resolved Budget information for one
        fiscal year.
        """

        resolved = self.resolve_line(
            budget_line
        )

        return (
            resolved.get(
                "by_year",
                {},
            ).get(
                fiscal_year,
                {},
            )
        )

    def get_amount(
        self,
        budget_line: dict[str, Any],
        fiscal_year: int,
        period_type: str,
    ) -> float | None:
        """
        Return one semantic amount for a fiscal year.

        Examples:

        period_type="requested"
        period_type="spending_plan"
        period_type="budget"
        period_type="forecast"
        """

        year_data = self.get_year(
            budget_line=budget_line,
            fiscal_year=fiscal_year,
        )

        normalized_type = (
            self._clean(
                period_type
            )
        )

        if not normalized_type:
            return None

        value = year_data.get(
            normalized_type
        )

        return self._nullable_float(
            value
        )

    @staticmethod
    def _resolve_type_amount(
        records: list[dict[str, Any]],
    ) -> float | None:
        """
        Resolve multiple source columns representing
        the same semantic type and fiscal year.

        Blank values remain null.

        If multiple populated columns of the same type
        exist, their values are summed.

        This preserves source flexibility without
        treating different semantic types as the same
        financial concept.
        """

        populated_amounts: list[
            float
        ] = []

        saw_record = False

        for record in records:
            saw_record = True

            amount = BudgetPeriodResolver._nullable_float(
                record.get(
                    "amount"
                )
            )

            if amount is None:
                continue

            populated_amounts.append(
                amount
            )

        if populated_amounts:
            return round(
                sum(
                    populated_amounts
                ),
                2,
            )

        if saw_record:
            return None

        return None

    @staticmethod
    def _nullable_float(
        value: Any,
    ) -> float | None:
        """
        Convert a financial value to float while
        preserving blank values as None.

        This distinguishes:

        None -> no amount provided
        0.0  -> explicit zero
        """

        if value is None:
            return None

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
                return None

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
            return None

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

        return cleaned.lower()