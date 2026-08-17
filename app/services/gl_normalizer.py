from __future__ import annotations

from datetime import datetime
from typing import Any


class GLNormalizer:
    """
    Converts General Ledger transactions from source-specific
    field names into the AI-FOS canonical transaction model.
    """

    FIELD_ALIASES = {
        "posting_date": [
            "posting_date",
            "posting date",
            "transaction_date",
            "transaction date",
            "date",
        ],
        "account_number": [
            "account_number",
            "account",
            "account number",
            "g/l account no.",
            "g/l account no",
            "gl account no",
            "gl account",
            "account no",
        ],
        "account_name": [
            "account_name",
            "account name",
            "g/l account name",
            "gl account name",
        ],
        "amount": [
            "amount",
            "amount_lcy",
            "amount (lcy)",
            "amount lcy",
        ],
        "debit_amount": [
            "debit_amount",
            "debit",
            "debit amount",
            "debit amount (lcy)",
        ],
        "credit_amount": [
            "credit_amount",
            "credit",
            "credit amount",
            "credit amount (lcy)",
        ],
        "document_number": [
            "document_number",
            "document number",
            "document no.",
            "document no",
        ],
        "document_type": [
            "document_type",
            "document type",
        ],
        "description": [
            "description",
        ],
        "fund_code": [
            "fund_code",
            "fund code",
            "fund",
            "grant code",
            "grant id",
        ],
        "donor_code": [
            "donor_code",
            "donor code",
            "funder_code",
            "funder code",
            "donor",
            "funder",
            "sponsor",
        ],
        "program_code": [
            "program_code",
            "program code",
            "programs_code",
            "programs code",
            "program",
            "programme code",
        ],
        "category_code": [
            "category_code",
            "category code",
            "category",
        ],
        "budget_line_code": [
            "budget_line_code",
            "budget line code",
            "budget line",
            "budget code",
        ],
        "donor_line_code": [
            "donor_line_code",
            "donor line code",
            "donor line",
            "funder line code",
        ],
        "company_code": [
            "company_code",
            "company code",
            "company",
        ],
        "currency": [
            "currency",
            "currency code",
        ],
        "source_system": [
            "source_system",
            "source system",
        ],
    }

    def normalize_transactions(
        self,
        transactions: list[dict[str, Any]],
        company_code: str | None = None,
        source_system: str | None = None,
    ) -> list[dict[str, Any]]:
        normalized_transactions: list[dict[str, Any]] = []

        for index, transaction in enumerate(transactions):
            normalized = self.normalize_transaction(
                transaction=transaction,
                transaction_index=index,
                company_code=company_code,
                source_system=source_system,
            )

            normalized_transactions.append(normalized)

        return normalized_transactions

    def normalize_transaction(
        self,
        transaction: dict[str, Any],
        transaction_index: int = 0,
        company_code: str | None = None,
        source_system: str | None = None,
    ) -> dict[str, Any]:
        normalized_lookup = {
            self._normalize_key(key): key for key in transaction.keys()
        }

        result: dict[str, Any] = {}

        for canonical_field, aliases in self.FIELD_ALIASES.items():
            source_key = self._find_source_key(
                normalized_lookup=normalized_lookup,
                aliases=aliases,
            )

            value = transaction.get(source_key) if source_key is not None else None

            result[canonical_field] = self._clean_value(value)

        result["posting_date"] = self._normalize_date(result.get("posting_date"))

        result["amount"] = self._normalize_number(result.get("amount"))

        result["debit_amount"] = self._normalize_number(result.get("debit_amount"))

        result["credit_amount"] = self._normalize_number(result.get("credit_amount"))

        if not result.get("company_code") and company_code:
            result["company_code"] = company_code

        if not result.get("source_system") and source_system:
            result["source_system"] = source_system

        result["transaction_id"] = (
            f"{result.get('company_code') or 'ORG'}-" f"{transaction_index + 1}"
        )

        return result

    def _find_source_key(
        self,
        normalized_lookup: dict[str, str],
        aliases: list[str],
    ) -> str | None:
        for alias in aliases:
            normalized_alias = self._normalize_key(alias)

            if normalized_alias in normalized_lookup:
                return normalized_lookup[normalized_alias]

        return None

    @staticmethod
    def _normalize_key(value: Any) -> str:
        return (
            str(value)
            .strip()
            .lower()
            .replace("/", " ")
            .replace("\\", " ")
            .replace("-", " ")
            .replace("_", " ")
            .replace(".", "")
        )

    @staticmethod
    def _clean_value(value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            cleaned = value.strip()

            if cleaned.lower() in {
                "",
                "none",
                "null",
                "nan",
            }:
                return None

            return cleaned

        return value

    @staticmethod
    def _normalize_number(
        value: Any,
    ) -> float | None:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()

        if not text:
            return None

        text = text.replace(",", "")

        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _normalize_date(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date().isoformat()

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
                parsed = datetime.strptime(
                    text,
                    format_string,
                )

                return parsed.date().isoformat()

            except ValueError:
                continue

        try:
            return datetime.fromisoformat(text).date().isoformat()

        except ValueError:
            return text
