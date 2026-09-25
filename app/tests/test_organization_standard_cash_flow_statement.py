from app.organization import Organization


def test_organization_initializes_standard_cash_flow_statement():
    organization = Organization()

    assert organization.standard_cash_flow_statement is None


def test_organization_builds_standard_cash_flow_statement_from_cash_flow():
    organization = Organization()

    organization.cash_flow = {
        "method": "transaction_counter_account_analysis",
        "operating_activities": 125000.0,
        "investing_activities": -30000.0,
        "financing_activities": 15000.0,
        "unclassified_activities": 5000.0,
        "classified_net_change": 115000.0,
        "net_change_in_cash": 115000.0,
        "reconciliation_difference": 0.0,
        "cash_accounts": [
            {
                "account_number": "210001",
                "account_name": "Bank Account",
                "financial_subcategory": "Cash and Cash Equivalents",
                "debit": 200000.0,
                "credit": 85000.0,
                "net_movement": 115000.0,
            }
        ],
        "activity_detail_count": 12,
        "document_count": 12,
        "classified_document_count": 11,
        "unclassified_document_count": 1,
    }

    # Build only the new reporting layer. The authoritative cash-flow
    # result must remain unchanged.
    original_cash_flow = {
        **organization.cash_flow,
        "cash_accounts": [
            dict(account)
            for account in organization.cash_flow["cash_accounts"]
        ],
    }

    from app.services.standard_cash_flow_statement import (
        generate_standard_cash_flow_statement,
    )

    organization.standard_cash_flow_statement = (
        generate_standard_cash_flow_statement(
            cash_flow=organization.cash_flow,
        )
    )

    statement = organization.standard_cash_flow_statement

    assert statement["statement_type"] == "standard_cash_flow_statement"
    assert statement["version"] == "v1"

    assert (
        statement["sections"]["operating_activities"]["amount"]
        == 125000.0
    )
    assert (
        statement["sections"]["investing_activities"]["amount"]
        == -30000.0
    )
    assert (
        statement["sections"]["financing_activities"]["amount"]
        == 15000.0
    )

    assert statement["unclassified_cash_movement"] == 5000.0
    assert statement["net_change_in_cash"] == 115000.0

    assert statement["reconciliation"]["difference"] == 0.0
    assert statement["reconciliation"]["is_reconciled"] is True

    assert statement["validation"]["status"] == "validated"
    assert (
        statement["validation"]["has_unclassified_cash_movement"]
        is True
    )

    assert organization.cash_flow == original_cash_flow