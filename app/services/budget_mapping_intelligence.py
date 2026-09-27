from typing import Any

from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)


BROADER_MATCH_STATUS = "Broader Budget Match - Review Required"
BLANK_BUDGET_LINE_STATUS = (
    "Broader Budget Envelope - No Specific Budget Line - "
    "Review Required"
)
MULTIPLE_CANDIDATES_STATUS = (

    "Broader Budget Envelope - Multiple Possible Budget Lines - "
    "Review Required"
)
NO_BUDGET_IDENTIFIED_STATUS = (
    "No Budget Identified - Review Required"
)


def _value(
    record: dict[str, Any],
    *fields: str,
) -> Any:
    for field in fields:
        value = record.get(field)
        if value not in (None, ""):
            return value

    return None


def _clean_code(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _dimension_key(
    record: dict[str, Any],
) -> tuple[str, str, str, str]:
    return (
        _clean_code(
            _value(record, "fund_code", "fund")
        ),
        _clean_code(
            _value(
                record,
                "donor_line_code",
                "donor_line",
            )
        ),
        _clean_code(
            _value(record, "program_code", "program")
        ),
        _clean_code(
            _value(record, "category_code", "category")
        ),
    )


def _budget_line_code(
    record: dict[str, Any],
) -> str:
    return _clean_code(
        _value(
            record,
            "budget_line_code",
            "budget_line",
        )
    )

def _budget_amount(
    budget_line: dict[str, Any],
) -> float:
    for field_name in [
        "current_budget",
        "revised_budget",
        "original_budget",
    ]:
        value = budget_line.get(field_name)

        if value not in (None, ""):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

    return 0.0


def _actual_amount(
    transaction: dict[str, Any],
) -> float:
    value = transaction.get(
        "budget_actual_amount",
        transaction.get("amount", 0.0),
    )

    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _prepare_budget_transactions(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[
        str,
        dict[str, Any],
    ] | None,
) -> list[dict[str, Any]]:
    budget_fund_codes = {
        _clean_code(
            _value(
                budget_line,
                "fund_code",
                "fund",
            )
        )
        for budget_line in budget_lines
        if _clean_code(
            _value(
                budget_line,
                "fund_code",
                "fund",
            )
        )
    }

    classifier = BudgetActualClassifier()
    accounts_by_number = accounts_by_number or {}

    prepared_transactions: list[
        dict[str, Any]
    ] = []

    for transaction in transactions:
        transaction_fund = _clean_code(
            _value(
                transaction,
                "fund_code",
                "fund",
            )
        )

        if transaction_fund not in budget_fund_codes:
            continue

        if "budget_actual_amount" in transaction:
            prepared_transaction = dict(transaction)

        else:
            classification = classifier.classify(
                transaction=transaction,
                accounts_by_number=accounts_by_number,
            )

            if not classification[
                "is_budget_consuming"
            ]:
                continue

            prepared_transaction = dict(transaction)

            prepared_transaction[
                "budget_actual_amount"
            ] = classification[
                "budget_actual_amount"
            ]

            prepared_transaction[
                "budget_treatment"
            ] = classification[
                "budget_treatment"
            ]

            prepared_transaction[
                "is_closing_entry"
            ] = classification[
                "is_closing_entry"
            ]

        prepared_transactions.append(
            prepared_transaction
        )

    return prepared_transactions


def generate_budget_mapping_intelligence(
    budget_lines: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
    accounts_by_number: dict[
        str,
        dict[str, Any],
    ] | None = None,
) -> dict[str, Any]:
    """
    Explain exact Budget vs Actual budget-line exceptions.

    The engine uses the same strict Budget Fund scope as Budget vs
    Actual and classifies raw GL transactions before analysis.

    It does not change Budget vs Actual. Broader matches remain
    review items until confirmed by finance.
    """

    prepared_transactions = (
        _prepare_budget_transactions(
            budget_lines=budget_lines,
            transactions=transactions,
            accounts_by_number=accounts_by_number,
        )
    )

    budget_by_dimension: dict[
        tuple[str, str, str, str],
        list[dict[str, Any]],
    ] = {}

    budget_amount_by_exact_key: dict[
        tuple[str, str, str, str, str],
        float,
    ] = {}
    budget_amount_by_line_code: dict[
        str,
        float,
    ] = {}
    for budget_line in budget_lines:
        dimension_key = _dimension_key(
            budget_line
        )
        line_code = _budget_line_code(
            budget_line
        )

        if line_code:
            budget_amount_by_line_code[
                line_code
            ] = (
                budget_amount_by_line_code.get(
                    line_code,
                    0.0,
                )
                + _budget_amount(budget_line)
            )        

        budget_by_dimension.setdefault(
            dimension_key,
            [],
        ).append(budget_line)

        exact_key = (
            *dimension_key,
            line_code,
        )

        budget_amount_by_exact_key[
            exact_key
        ] = (
            budget_amount_by_exact_key.get(
                exact_key,
                0.0,
            )
            + _budget_amount(budget_line)
        )

    items: list[dict[str, Any]] = []

    broader_match_count = 0
    broader_match_actual = 0.0
    no_budget_identified_count = 0
    no_budget_identified_actual = 0.0

    aggregated_transactions: dict[
        tuple[str, str, str, str, str],
        dict[str, Any],
    ] = {}

    for transaction in prepared_transactions:
        dimension_key = _dimension_key(
            transaction
        )
        actual_line_code = _budget_line_code(
            transaction
        )

        aggregation_key = (
            *dimension_key,
            actual_line_code,
        )

        actual = _actual_amount(transaction)

        if aggregation_key not in aggregated_transactions:
            aggregated_transaction = dict(
                transaction
            )
            aggregated_transaction[
                "budget_actual_amount"
            ] = actual
            aggregated_transactions[
                aggregation_key
            ] = aggregated_transaction
        else:
            aggregated_transactions[
                aggregation_key
            ][
                "budget_actual_amount"
            ] += actual

    for transaction in aggregated_transactions.values():
        dimension_key = _dimension_key(
            transaction
        )
        actual_line_code = _budget_line_code(
            transaction
        )

        if not actual_line_code:
            continue

        portfolio_budget_amount = (
            budget_amount_by_line_code.get(
                actual_line_code,
                0.0,
            )
        )

        if abs(portfolio_budget_amount) >= 0.01:
            continue

        exact_key = (
            *dimension_key,
            actual_line_code,
        )

        exact_budget_amount = (
            budget_amount_by_exact_key.get(
                exact_key,
                0.0,
            )
        )

        if abs(exact_budget_amount) >= 0.01:
            continue

        actual = _actual_amount(transaction)

        if abs(actual) < 0.01:
            continue

        if (
            exact_key in budget_amount_by_exact_key
            and abs(exact_budget_amount) < 0.01
        ):
            item = {
                "status": (
                    NO_BUDGET_IDENTIFIED_STATUS
                ),
                "actual_budget_line_code": (
                    actual_line_code
                ),
                "matched_budget_line_code": None,
                "candidate_budget_line_codes": [],
                "actual": actual,
            }

            no_budget_identified_count += 1
            no_budget_identified_actual += actual

            items.append(item)
            continue        

        broader_candidates = (
            budget_by_dimension.get(
                dimension_key,
                [],
            )
        )

        candidate_codes = sorted(
            {
                _budget_line_code(candidate)
                for candidate in broader_candidates
                if _budget_line_code(candidate)
            }
        )

        if len(candidate_codes) == 1:
            item = {
                "status": BROADER_MATCH_STATUS,
                "actual_budget_line_code": (
                    actual_line_code
                ),
                "matched_budget_line_code": (
                    candidate_codes[0]
                ),
                "candidate_budget_line_codes": (
                    candidate_codes
                ),
                "actual": actual,
            }

            broader_match_count += 1
            broader_match_actual += actual

        elif len(candidate_codes) > 1:
            item = {
                "status": MULTIPLE_CANDIDATES_STATUS,
                "actual_budget_line_code": (
                    actual_line_code
                ),
                "matched_budget_line_code": None,
                "candidate_budget_line_codes": (
                    candidate_codes
                ),
                "actual": actual,
            }

            broader_match_count += 1
            broader_match_actual += actual

        elif broader_candidates:
            item = {
                "status": BLANK_BUDGET_LINE_STATUS,
                "actual_budget_line_code": (
                    actual_line_code
                ),
                "matched_budget_line_code": None,
                "candidate_budget_line_codes": [],
                "actual": actual,
            }

            broader_match_count += 1
            broader_match_actual += actual

        else:
            item = {
                "status": (
                    NO_BUDGET_IDENTIFIED_STATUS
                ),
                "actual_budget_line_code": (
                    actual_line_code
                ),
                "matched_budget_line_code": None,
                "candidate_budget_line_codes": [],
                "actual": actual,
            }

            no_budget_identified_count += 1
            no_budget_identified_actual += actual

        items.append(item)

    unique_exception_budget_line_codes = sorted(
        {
            item["actual_budget_line_code"]
            for item in items
            if item.get("actual_budget_line_code")
        }
    )

    return {
        "summary": {
            "exception_budget_line_count": len(
                unique_exception_budget_line_codes
            ),
            "exception_budget_line_codes": (
                unique_exception_budget_line_codes
            ),
            "evidence_item_count": len(items),
            "broader_match_evidence_count": (
                broader_match_count
            ),
            "broader_match_actual": round(
                broader_match_actual,
                2,
            ),
            "no_budget_identified_evidence_count": (
                no_budget_identified_count
            ),
            "no_budget_identified_actual": round(
                no_budget_identified_actual,
                2,
            ),
            "total_exception_actual": round(
                broader_match_actual
                + no_budget_identified_actual,
                2,
            ),
        },
        "items": items,
    }