from __future__ import annotations

from typing import Any


class NeededBudget:
    """
    Represents one imported AI-FOS Needed Budget.

    Needed Budget describes what an organization needs
    financially for a fiscal period. It is intentionally
    separate from the Available / Grant Budget because
    required funding does not necessarily belong to a
    donor, fund, or grant.

    The model remains generic so organizations may use:
    - Available Budget only
    - Needed Budget only
    - Both
    - Neither
    """

    def __init__(self) -> None:

        self.lines: list[dict[str, Any]] = []

        self.by_budget_line: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_program: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_category: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_fiscal_year: dict[
            str,
            list[dict[str, Any]],
        ] = {}

    def load_budget(
        self,
        budget_lines: list[dict[str, Any]],
    ) -> None:
        """
        Store normalized Needed Budget lines and rebuild
        the relevant planning-dimension indexes.
        """

        self.lines = budget_lines

        self.by_budget_line = {}
        self.by_program = {}
        self.by_category = {}
        self.by_fiscal_year = {}

        for line in budget_lines:

            self._index_line(
                index=self.by_budget_line,
                key=self._get_value(
                    line,
                    "budget_line_code",
                ),
                line=line,
            )

            self._index_line(
                index=self.by_program,
                key=self._get_value(
                    line,
                    "program_code",
                    "program",
                ),
                line=line,
            )

            self._index_line(
                index=self.by_category,
                key=self._get_value(
                    line,
                    "category_code",
                    "category",
                ),
                line=line,
            )

            fiscal_year = line.get(
                "fiscal_year"
            )

            self._index_line(
                index=self.by_fiscal_year,
                key=(
                    str(fiscal_year)
                    if fiscal_year is not None
                    else None
                ),
                line=line,
            )

    def get_budget_line(
        self,
        budget_line_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_budget_line,
            budget_line_code,
        )

    def get_program_budget(
        self,
        program_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_program,
            program_code,
        )

    def get_category_budget(
        self,
        category_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_category,
            category_code,
        )

    def get_fiscal_year_budget(
        self,
        fiscal_year: int | str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_fiscal_year,
            str(fiscal_year),
        )

    def budget_line_count(self) -> int:
        return len(self.by_budget_line)

    def program_count(self) -> int:
        return len(self.by_program)

    def category_count(self) -> int:
        return len(self.by_category)

    def fiscal_year_count(self) -> int:
        return len(self.by_fiscal_year)

    def total_needed_budget(
        self,
        fiscal_year: int | str | None = None,
    ) -> float:
        """
        Return total Needed Budget.

        If fiscal_year is supplied, calculate the total
        only for that fiscal year.
        """

        if fiscal_year is None:
            records = self.lines
        else:
            records = self.get_fiscal_year_budget(
                fiscal_year
            )

        return round(
            sum(
                self._to_float(
                    line.get("needed_budget")
                )
                for line in records
            ),
            2,
        )

    @staticmethod
    def _index_line(
        index: dict[
            str,
            list[dict[str, Any]],
        ],
        key: str | None,
        line: dict[str, Any],
    ) -> None:

        if not key:
            return

        index.setdefault(
            key,
            [],
        ).append(line)

    @staticmethod
    def _get_index_records(
        index: dict[
            str,
            list[dict[str, Any]],
        ],
        value: Any,
    ) -> list[dict[str, Any]]:

        key = str(value).strip()

        if not key:
            return []

        return index.get(
            key,
            [],
        )

    @staticmethod
    def _get_value(
        record: dict[str, Any],
        *field_names: str,
    ) -> str | None:

        for field_name in field_names:

            value = record.get(field_name)

            if value is None:
                continue

            cleaned = str(value).strip()

            if cleaned:
                return cleaned

        return None

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float:

        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        text = (
            str(value)
            .replace(",", "")
            .replace("$", "")
            .strip()
        )

        if not text:
            return 0.0

        try:
            return float(text)

        except ValueError:
            return 0.0