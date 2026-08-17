from __future__ import annotations

from datetime import date, datetime
from typing import Any


class GLDateValidator:
    """
    Performs date-quality checks on normalized
    General Ledger transactions.

    The validator does not modify or remove transactions.
    It identifies date issues so AI-FOS can distinguish
    source data from transactions appropriate for
    current-period financial analysis.
    """

    def validate(
        self,
        transactions: list[dict[str, Any]],
        reporting_date: date | None = None,
    ) -> dict[str, Any]:

        if reporting_date is None:
            reporting_date = date.today()

        valid_date_count = 0
        missing_date_count = 0
        invalid_date_count = 0

        future_transactions: list[dict[str, Any]] = []

        earliest_date: date | None = None
        latest_date: date | None = None

        for transaction in transactions:

            raw_date = transaction.get("posting_date")

            if raw_date is None or str(raw_date).strip() == "":
                missing_date_count += 1
                continue

            posting_date = self._parse_date(raw_date)

            if posting_date is None:
                invalid_date_count += 1
                continue

            valid_date_count += 1

            if earliest_date is None or posting_date < earliest_date:
                earliest_date = posting_date

            if latest_date is None or posting_date > latest_date:
                latest_date = posting_date

            if posting_date > reporting_date:
                future_transactions.append(
                    {
                        "transaction_id": transaction.get(
                            "transaction_id"
                        ),
                        "posting_date": posting_date.isoformat(),
                        "account_number": transaction.get(
                            "account_number"
                        ),
                        "account_name": transaction.get(
                            "account_name"
                        ),
                        "document_number": transaction.get(
                            "document_number"
                        ),
                        "description": transaction.get(
                            "description"
                        ),
                        "amount": transaction.get(
                            "amount"
                        ),
                        "fund_code": transaction.get(
                            "fund_code"
                        ),
                        "donor_code": transaction.get(
                            "donor_code"
                        ),
                    }
                )

        future_transactions.sort(
            key=lambda item: item["posting_date"]
        )

        future_transaction_count = len(
            future_transactions
        )

        current_or_historical_count = (
            valid_date_count - future_transaction_count
        )

        warnings: list[str] = []

        if missing_date_count:
            warnings.append(
                f"{missing_date_count} transaction(s) "
                "have no posting date."
            )

        if invalid_date_count:
            warnings.append(
                f"{invalid_date_count} transaction(s) "
                "have an invalid posting date."
            )

        if future_transaction_count:
            warnings.append(
                f"{future_transaction_count} transaction(s) "
                f"are dated after the reporting date "
                f"{reporting_date.isoformat()}."
            )

        return {
            "status": (
                "warning"
                if warnings
                else "valid"
            ),
            "reporting_date": reporting_date.isoformat(),
            "summary": {
                "transaction_count": len(transactions),
                "valid_date_count": valid_date_count,
                "missing_date_count": missing_date_count,
                "invalid_date_count": invalid_date_count,
                "current_or_historical_count": (
                    current_or_historical_count
                ),
                "future_transaction_count": (
                    future_transaction_count
                ),
                "earliest_posting_date": (
                    earliest_date.isoformat()
                    if earliest_date
                    else None
                ),
                "latest_posting_date": (
                    latest_date.isoformat()
                    if latest_date
                    else None
                ),
            },
            "warnings": warnings,
            "future_transactions": future_transactions,
        }

    @staticmethod
    def _parse_date(
        value: Any,
    ) -> date | None:

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        text = str(value).strip()

        if not text:
            return None

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]

        for format_string in formats:
            try:
                return datetime.strptime(
                    text,
                    format_string,
                ).date()

            except ValueError:
                continue

        try:
            return datetime.fromisoformat(
                text
            ).date()

        except ValueError:
            return None