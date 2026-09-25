from __future__ import annotations

from typing import Any


def generate_standard_cash_flow_statement(
    cash_flow: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the standardized AI-FOS cash flow statement from the verified
    transaction-level cash-flow output.

    The existing cash-flow engine remains the source of truth for
    operating, investing, financing, and unclassified cash movements.
    """

    operating_activities = _to_float(
        cash_flow.get("operating_activities")
    )
    investing_activities = _to_float(
        cash_flow.get("investing_activities")
    )
    financing_activities = _to_float(
        cash_flow.get("financing_activities")
    )
    unclassified_activities = _to_float(
        cash_flow.get("unclassified_activities")
    )
    net_change_in_cash = _to_float(
        cash_flow.get("net_change_in_cash")
    )

    classified_net_change = (
        operating_activities
        + investing_activities
        + financing_activities
        + unclassified_activities
    )

    reconciliation_difference = (
        net_change_in_cash - classified_net_change
    )

    is_reconciled = abs(reconciliation_difference) < 0.01

    return {
        "statement_type": "standard_cash_flow_statement",
        "version": "v1",
        "method": cash_flow.get(
            "method",
            "transaction_counter_account_analysis",
        ),
        "sections": {
            "operating_activities": {
                "label": "Cash Flows from Operating Activities",
                "amount": round(operating_activities, 2),
            },
            "investing_activities": {
                "label": "Cash Flows from Investing Activities",
                "amount": round(investing_activities, 2),
            },
            "financing_activities": {
                "label": "Cash Flows from Financing Activities",
                "amount": round(financing_activities, 2),
            },
        },
        "net_change_in_cash": round(net_change_in_cash, 2),
        "unclassified_cash_movement": round(
            unclassified_activities,
            2,
        ),
        "reconciliation": {
            "classified_net_change": round(
                classified_net_change,
                2,
            ),
            "net_change_in_cash": round(
                net_change_in_cash,
                2,
            ),
            "difference": round(
                reconciliation_difference,
                2,
            ),
            "is_reconciled": is_reconciled,
        },
        "cash_accounts": cash_flow.get("cash_accounts", []),
        "classification_diagnostics": {
            "document_count": cash_flow.get(
                "document_count",
                0,
            ),
            "classified_document_count": cash_flow.get(
                "classified_document_count",
                0,
            ),
            "unclassified_document_count": cash_flow.get(
                "unclassified_document_count",
                0,
            ),
            "activity_detail_count": cash_flow.get(
                "activity_detail_count",
                0,
            ),
        },
        "validation": {
            "status": "validated" if is_reconciled else "review_required",
            "reconciled": is_reconciled,
            "has_unclassified_cash_movement": (
                abs(unclassified_activities) >= 0.01
            ),
        },
        "note": (
            "Standard Cash Flow Statement v1 uses the verified AI-FOS "
            "transaction-level cash-flow classification as its source. "
            "Opening and closing cash balances are not presented unless "
            "they can be supported by verified balance data."
        ),
    }


def _to_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0