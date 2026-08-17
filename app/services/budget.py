from __future__ import annotations

from typing import Any


class Budget:
    """
    Represents one imported AI-FOS budget.

    Stores normalized budget lines and maintains
    indexes across the financial dimensions used
    by Budget vs Actual and Grant Intelligence.
    """

    def __init__(self) -> None:

        self.lines: list[dict[str, Any]] = []

        self.by_account: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_budget_line: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_fund: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_donor: dict[
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

        self.by_donor_line: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.by_project: dict[
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
        Store normalized budget lines and rebuild
        all dimension indexes.
        """

        self.lines = budget_lines

        self.by_account = {}
        self.by_budget_line = {}
        self.by_fund = {}
        self.by_donor = {}
        self.by_program = {}
        self.by_category = {}
        self.by_donor_line = {}
        self.by_project = {}
        self.by_fiscal_year = {}

        for line in budget_lines:

            self._index_line(
                index=self.by_account,
                key=self._get_value(
                    line,
                    "account_number",
                ),
                line=line,
            )

            self._index_line(
                index=self.by_budget_line,
                key=self._get_value(
                    line,
                    "budget_line_code",
                ),
                line=line,
            )

            self._index_line(
                index=self.by_fund,
                key=self._get_value(
                    line,
                    "fund_code",
                    "fund",
                ),
                line=line,
            )

            self._index_line(
                index=self.by_donor,
                key=self._get_value(
                    line,
                    "donor_code",
                    "donor",
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

            self._index_line(
                index=self.by_donor_line,
                key=self._get_value(
                    line,
                    "donor_line_code",
                    "donor_line",
                ),
                line=line,
            )

            self._index_line(
                index=self.by_project,
                key=self._get_value(
                    line,
                    "project_code",
                    "project",
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

    def get_account_budget(
        self,
        account_number: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_account,
            account_number,
        )

    def get_budget_line(
        self,
        budget_line_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_budget_line,
            budget_line_code,
        )

    def get_fund_budget(
        self,
        fund_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_fund,
            fund_code,
        )

    def get_donor_budget(
        self,
        donor_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_donor,
            donor_code,
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

    def get_donor_line_budget(
        self,
        donor_line_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_donor_line,
            donor_line_code,
        )

    def get_project_budget(
        self,
        project_code: str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_project,
            project_code,
        )

    def get_fiscal_year_budget(
        self,
        fiscal_year: int | str,
    ) -> list[dict[str, Any]]:

        return self._get_index_records(
            self.by_fiscal_year,
            str(fiscal_year),
        )

    def account_count(self) -> int:
        return len(self.by_account)

    def budget_line_count(self) -> int:
        return len(self.by_budget_line)

    def fund_count(self) -> int:
        return len(self.by_fund)

    def donor_count(self) -> int:
        return len(self.by_donor)

    def program_count(self) -> int:
        return len(self.by_program)

    def category_count(self) -> int:
        return len(self.by_category)

    def donor_line_count(self) -> int:
        return len(self.by_donor_line)

    def project_count(self) -> int:
        return len(self.by_project)

    def total_original_budget(self) -> float:

        return round(
            sum(
                self._to_float(
                    line.get("original_budget")
                )
                for line in self.lines
            ),
            2,
        )

    def total_revised_budget(self) -> float:

        return round(
            sum(
                self._to_float(
                    line.get("revised_budget")
                )
                for line in self.lines
            ),
            2,
        )

    def total_current_budget(self) -> float:

        return round(
            sum(
                self._to_float(
                    line.get(
                        "current_budget",
                        line.get("revised_budget"),
                    )
                )
                for line in self.lines
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