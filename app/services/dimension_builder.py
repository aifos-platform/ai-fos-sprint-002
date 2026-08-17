import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class DimensionBuilder:
    """
    Builds AI-FOS financial dimensions automatically
    from normalized General Ledger transactions.

    Dimension files are rebuilt from the supplied
    transaction set so they remain synchronized with
    FACT_GL and do not retain stale historical values.
    """

    DIMENSION_CONFIG = {
        "fund": {
            "file": "dim_fund.json",
            "candidate_fields": [
                "fund_code",
                "fund",
                "grant_code",
                "grant_id",
            ],
        },
        "donor": {
            "file": "dim_donor.json",
            "candidate_fields": [
                "donor_code",
                "funder_code",
                "donor",
                "funder",
                "sponsor",
            ],
        },
        "program": {
            "file": "dim_program.json",
            "candidate_fields": [
                "program_code",
                "programs_code",
                "program",
                "programme_code",
            ],
        },
        "category": {
            "file": "dim_category.json",
            "candidate_fields": [
                "category_code",
                "category",
            ],
        },
        "budget_line": {
            "file": "dim_budget_line.json",
            "candidate_fields": [
                "budget_line_code",
                "budget_line",
                "budget_code",
            ],
        },
        "donor_line": {
            "file": "dim_donor_line.json",
            "candidate_fields": [
                "donor_line_code",
                "donor_line",
                "funder_line_code",
            ],
        },
    }

    DATE_FIELDS = [
        "posting_date",
        "transaction_date",
        "date",
    ]

    def build_all_dimensions(
        self,
        financial_model_folder: Path,
        transactions: list[dict[str, Any]],
    ) -> dict[str, Any]:

        financial_model_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        summary: dict[str, Any] = {
            "dimensions": {},
        }

        for (
            dimension_name,
            config,
        ) in self.DIMENSION_CONFIG.items():

            result = self._build_dimension(
                financial_model_folder=financial_model_folder,
                transactions=transactions,
                dimension_name=dimension_name,
                file_name=config["file"],
                candidate_fields=config["candidate_fields"],
            )

            summary["dimensions"][
                dimension_name
            ] = result

        calendar_result = self._build_calendar(
            financial_model_folder=financial_model_folder,
            transactions=transactions,
        )

        summary["dimensions"][
            "calendar"
        ] = calendar_result

        return summary

    def _build_dimension(
        self,
        financial_model_folder: Path,
        transactions: list[dict[str, Any]],
        dimension_name: str,
        file_name: str,
        candidate_fields: list[str],
    ) -> dict[str, Any]:

        detected_field = self._find_field(
            transactions=transactions,
            candidate_fields=candidate_fields,
        )

        output_file = (
            financial_model_folder
            / file_name
        )

        if detected_field is None:
            self._save_json(
                output_file,
                [],
            )

            return {
                "file": str(output_file),
                "detected_field": None,
                "total_count": 0,
                "status": "field_not_detected",
            }

        discovered_values: set[str] = set()

        for transaction in transactions:
            value = transaction.get(
                detected_field
            )

            cleaned_value = self._clean_value(
                value
            )

            if cleaned_value:
                discovered_values.add(
                    cleaned_value
                )

        dimension_records = [
            {
                "code": value,
                "dimension": dimension_name,
                "active": True,
            }
            for value in sorted(
                discovered_values
            )
        ]

        self._save_json(
            output_file,
            dimension_records,
        )

        return {
            "file": str(output_file),
            "detected_field": detected_field,
            "total_count": len(
                discovered_values
            ),
            "values": sorted(
                discovered_values
            ),
            "status": "rebuilt",
        }

    def _build_calendar(
        self,
        financial_model_folder: Path,
        transactions: list[dict[str, Any]],
    ) -> dict[str, Any]:

        output_file = (
            financial_model_folder
            / "dim_calendar.json"
        )

        detected_field = self._find_field(
            transactions=transactions,
            candidate_fields=self.DATE_FIELDS,
        )

        if detected_field is None:
            self._save_json(
                output_file,
                [],
            )

            return {
                "file": str(output_file),
                "detected_field": None,
                "total_count": 0,
                "status": "date_field_not_detected",
            }

        transaction_dates: list[datetime] = []

        for transaction in transactions:
            value = transaction.get(
                detected_field
            )

            parsed_date = self._parse_date(
                value
            )

            if parsed_date:
                transaction_dates.append(
                    parsed_date
                )

        if not transaction_dates:
            self._save_json(
                output_file,
                [],
            )

            return {
                "file": str(output_file),
                "detected_field": detected_field,
                "total_count": 0,
                "status": "no_valid_dates",
            }

        minimum_date = min(
            transaction_dates
        ).date()

        maximum_date = max(
            transaction_dates
        ).date()

        calendar_records = []

        current_date = minimum_date

        while current_date <= maximum_date:

            quarter = (
                (current_date.month - 1)
                // 3
            ) + 1

            calendar_records.append(
                {
                    "date": (
                        current_date.isoformat()
                    ),
                    "year": current_date.year,
                    "quarter": quarter,
                    "quarter_name": (
                        f"Q{quarter}"
                    ),
                    "month": (
                        current_date.month
                    ),
                    "month_name": (
                        current_date.strftime(
                            "%B"
                        )
                    ),
                    "year_month": (
                        current_date.strftime(
                            "%Y-%m"
                        )
                    ),
                    "day": current_date.day,
                    "day_name": (
                        current_date.strftime(
                            "%A"
                        )
                    ),
                    "week": int(
                        current_date.strftime(
                            "%W"
                        )
                    ),
                }
            )

            current_date += timedelta(
                days=1
            )

        self._save_json(
            output_file,
            calendar_records,
        )

        return {
            "file": str(output_file),
            "detected_field": detected_field,
            "minimum_date": (
                minimum_date.isoformat()
            ),
            "maximum_date": (
                maximum_date.isoformat()
            ),
            "transaction_date_count": len(
                {
                    date_value.date()
                    for date_value
                    in transaction_dates
                }
            ),
            "total_count": len(
                calendar_records
            ),
            "status": "rebuilt",
        }

    @staticmethod
    def _find_field(
        transactions: list[dict[str, Any]],
        candidate_fields: list[str],
    ) -> str | None:

        if not transactions:
            return None

        available_fields: set[str] = set()

        for transaction in transactions[
            :100
        ]:
            available_fields.update(
                transaction.keys()
            )

        normalized_lookup = {
            str(field)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("/", "_"):
            field
            for field in available_fields
        }

        for candidate in candidate_fields:

            normalized_candidate = (
                candidate
                .strip()
                .lower()
                .replace(" ", "_")
                .replace("/", "_")
            )

            if (
                normalized_candidate
                in normalized_lookup
            ):
                return normalized_lookup[
                    normalized_candidate
                ]

        return None

    @staticmethod
    def _clean_value(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        cleaned = str(value).strip()

        if not cleaned:
            return None

        if cleaned.lower() in {
            "none",
            "nan",
            "null",
        }:
            return None

        return cleaned

    @staticmethod
    def _parse_date(
        value: Any,
    ) -> datetime | None:

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value

        text = str(value).strip()

        if not text:
            return None

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]

        for format_string in formats:
            try:
                return datetime.strptime(
                    text,
                    format_string,
                )
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(
                text
            )

        except ValueError:
            return None

    @staticmethod
    def _save_json(
        path: Path,
        data: list,
    ) -> None:

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )