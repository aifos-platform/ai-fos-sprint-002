from __future__ import annotations

from collections import Counter
from typing import Any


class GLIntegrityValidator:
    """
    Validates the structural and accounting integrity
    of normalized General Ledger transactions.

    The validator does not modify transactions.
    It reports errors and warnings so AI-FOS can decide
    whether the uploaded ledger is safe to use for
    financial analysis.
    """

    DEFAULT_TOLERANCE = 0.01
    SAMPLE_LIMIT = 50

    def validate(
        self,
        transactions: list[dict[str, Any]],
        accounts_by_number: dict[str, Any] | None = None,
        tolerance: float = DEFAULT_TOLERANCE,
    ) -> dict[str, Any]:

        accounts_by_number = accounts_by_number or {}

        total_debit = 0.0
        total_credit = 0.0
        total_amount = 0.0

        missing_account_count = 0
        unknown_account_count = 0
        missing_amount_count = 0
        amount_mismatch_count = 0
        both_debit_credit_count = 0
        zero_value_count = 0
        missing_account_name_count = 0

        unknown_accounts: Counter[str] = Counter()

        missing_account_samples: list[dict[str, Any]] = []
        unknown_account_samples: list[dict[str, Any]] = []
        amount_mismatch_samples: list[dict[str, Any]] = []
        both_debit_credit_samples: list[dict[str, Any]] = []

        for transaction in transactions:

            account_number = self._clean_text(
                transaction.get("account_number")
            )

            account_name = self._clean_text(
                transaction.get("account_name")
            )

            amount = self._to_number(
                transaction.get("amount")
            )

            debit = self._to_number(
                transaction.get("debit_amount")
            )

            credit = self._to_number(
                transaction.get("credit_amount")
            )

            if amount is not None:
                total_amount += amount

            if debit is not None:
                total_debit += debit

            if credit is not None:
                total_credit += credit

            if not account_number:
                missing_account_count += 1

                self._append_sample(
                    missing_account_samples,
                    transaction,
                )

            elif (
                accounts_by_number
                and account_number
                not in accounts_by_number
            ):
                unknown_account_count += 1
                unknown_accounts[
                    account_number
                ] += 1

                self._append_sample(
                    unknown_account_samples,
                    transaction,
                )

            if not account_name:
                missing_account_name_count += 1

            if (
                amount is None
                and debit is None
                and credit is None
            ):
                missing_amount_count += 1

            if (
                debit is not None
                and credit is not None
                and abs(debit) > tolerance
                and abs(credit) > tolerance
            ):
                both_debit_credit_count += 1

                self._append_sample(
                    both_debit_credit_samples,
                    transaction,
                )

            if (
                amount is not None
                and debit is not None
                and credit is not None
            ):
                expected_amount = (
                    debit - credit
                )

                difference = (
                    amount
                    - expected_amount
                )

                if abs(difference) > tolerance:
                    amount_mismatch_count += 1

                    mismatch_record = {
                        "transaction_id": (
                            transaction.get(
                                "transaction_id"
                            )
                        ),
                        "posting_date": (
                            transaction.get(
                                "posting_date"
                            )
                        ),
                        "document_number": (
                            transaction.get(
                                "document_number"
                            )
                        ),
                        "account_number": (
                            account_number
                        ),
                        "account_name": (
                            account_name
                        ),
                        "amount": amount,
                        "debit_amount": debit,
                        "credit_amount": credit,
                        "expected_amount": (
                            expected_amount
                        ),
                        "difference": (
                            difference
                        ),
                    }

                    if (
                        len(
                            amount_mismatch_samples
                        )
                        < self.SAMPLE_LIMIT
                    ):
                        amount_mismatch_samples.append(
                            mismatch_record
                        )

            debit_value = (
                debit
                if debit is not None
                else 0.0
            )

            credit_value = (
                credit
                if credit is not None
                else 0.0
            )

            amount_value = (
                amount
                if amount is not None
                else 0.0
            )

            if (
                abs(debit_value) <= tolerance
                and abs(credit_value) <= tolerance
                and abs(amount_value) <= tolerance
            ):
                zero_value_count += 1

        debit_credit_difference = (
            total_debit - total_credit
        )

        errors: list[str] = []
        warnings: list[str] = []

        if missing_account_count:
            errors.append(
                f"{missing_account_count} "
                "transaction(s) have no "
                "G/L account number."
            )

        if unknown_account_count:
            errors.append(
                f"{unknown_account_count} "
                "transaction(s) reference "
                "G/L accounts that are not "
                "present in DIM_ACCOUNT."
            )

        if amount_mismatch_count:
            errors.append(
                f"{amount_mismatch_count} "
                "transaction(s) do not satisfy "
                "Amount = Debit - Credit."
            )

        if (
            abs(
                debit_credit_difference
            )
            > tolerance
        ):
            errors.append(
                "The General Ledger is not "
                "balanced. Total debit differs "
                "from total credit by "
                f"{debit_credit_difference:.2f}."
            )

        if missing_amount_count:
            warnings.append(
                f"{missing_amount_count} "
                "transaction(s) have no amount, "
                "debit, or credit value."
            )

        if both_debit_credit_count:
            warnings.append(
                f"{both_debit_credit_count} "
                "transaction(s) contain both "
                "a debit and credit value."
            )

        if zero_value_count:
            warnings.append(
                f"{zero_value_count} "
                "transaction(s) have zero "
                "financial value."
            )

        if missing_account_name_count:
            warnings.append(
                f"{missing_account_name_count} "
                "transaction(s) have no "
                "account name."
            )

        if errors:
            status = "error"
        elif warnings:
            status = "warning"
        else:
            status = "valid"

        return {
            "status": status,
            "tolerance": tolerance,
            "summary": {
                "transaction_count": (
                    len(transactions)
                ),
                "total_debit": round(
                    total_debit,
                    2,
                ),
                "total_credit": round(
                    total_credit,
                    2,
                ),
                "debit_credit_difference": round(
                    debit_credit_difference,
                    2,
                ),
                "total_amount": round(
                    total_amount,
                    2,
                ),
                "missing_account_count": (
                    missing_account_count
                ),
                "unknown_account_count": (
                    unknown_account_count
                ),
                "missing_amount_count": (
                    missing_amount_count
                ),
                "amount_mismatch_count": (
                    amount_mismatch_count
                ),
                "both_debit_credit_count": (
                    both_debit_credit_count
                ),
                "zero_value_count": (
                    zero_value_count
                ),
                "missing_account_name_count": (
                    missing_account_name_count
                ),
            },
            "errors": errors,
            "warnings": warnings,
            "unknown_accounts": [
                {
                    "account_number": account,
                    "transaction_count": count,
                }
                for account, count
                in unknown_accounts.most_common()
            ],
            "samples": {
                "missing_accounts": (
                    missing_account_samples
                ),
                "unknown_accounts": (
                    unknown_account_samples
                ),
                "amount_mismatches": (
                    amount_mismatch_samples
                ),
                "both_debit_and_credit": (
                    both_debit_credit_samples
                ),
            },
        }

    def _append_sample(
        self,
        samples: list[dict[str, Any]],
        transaction: dict[str, Any],
    ) -> None:

        if len(samples) >= self.SAMPLE_LIMIT:
            return

        samples.append(
            {
                "transaction_id": (
                    transaction.get(
                        "transaction_id"
                    )
                ),
                "posting_date": (
                    transaction.get(
                        "posting_date"
                    )
                ),
                "document_number": (
                    transaction.get(
                        "document_number"
                    )
                ),
                "account_number": (
                    transaction.get(
                        "account_number"
                    )
                ),
                "account_name": (
                    transaction.get(
                        "account_name"
                    )
                ),
                "amount": (
                    transaction.get(
                        "amount"
                    )
                ),
                "debit_amount": (
                    transaction.get(
                        "debit_amount"
                    )
                ),
                "credit_amount": (
                    transaction.get(
                        "credit_amount"
                    )
                ),
            }
        )

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        cleaned = str(value).strip()

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
    def _to_number(
        value: Any,
    ) -> float | None:

        if value is None:
            return None

        if isinstance(
            value,
            (int, float),
        ):
            return float(value)

        text = str(value).strip()

        if not text:
            return None

        text = text.replace(
            ",",
            "",
        )

        try:
            return float(text)

        except ValueError:
            return None