from app.services.standard_cash_flow_statement import (
    generate_standard_cash_flow_statement,
)


def _cash_flow() -> dict:
    return {
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


def test_standard_cash_flow_statement_structure() -> None:
    statement = generate_standard_cash_flow_statement(_cash_flow())

    assert statement["statement_type"] == "standard_cash_flow_statement"
    assert statement["version"] == "v1"
    assert statement["method"] == "transaction_counter_account_analysis"

    assert "sections" in statement
    assert "operating_activities" in statement["sections"]
    assert "investing_activities" in statement["sections"]
    assert "financing_activities" in statement["sections"]


def test_standard_cash_flow_statement_amounts() -> None:
    statement = generate_standard_cash_flow_statement(_cash_flow())

    assert statement["sections"]["operating_activities"]["amount"] == 125000.0
    assert statement["sections"]["investing_activities"]["amount"] == -30000.0
    assert statement["sections"]["financing_activities"]["amount"] == 15000.0

    assert statement["unclassified_cash_movement"] == 5000.0
    assert statement["net_change_in_cash"] == 115000.0


def test_standard_cash_flow_statement_reconciles() -> None:
    statement = generate_standard_cash_flow_statement(_cash_flow())

    reconciliation = statement["reconciliation"]

    assert reconciliation["classified_net_change"] == 115000.0
    assert reconciliation["net_change_in_cash"] == 115000.0
    assert reconciliation["difference"] == 0.0
    assert reconciliation["is_reconciled"] is True

    assert statement["validation"]["status"] == "validated"
    assert statement["validation"]["reconciled"] is True


def test_standard_cash_flow_statement_flags_difference() -> None:
    cash_flow = _cash_flow()
    cash_flow["net_change_in_cash"] = 120000.0

    statement = generate_standard_cash_flow_statement(cash_flow)

    assert statement["reconciliation"]["classified_net_change"] == 115000.0
    assert statement["reconciliation"]["net_change_in_cash"] == 120000.0
    assert statement["reconciliation"]["difference"] == 5000.0
    assert statement["reconciliation"]["is_reconciled"] is False

    assert statement["validation"]["status"] == "review_required"
    assert statement["validation"]["reconciled"] is False


def test_standard_cash_flow_statement_flags_unclassified_cash() -> None:
    statement = generate_standard_cash_flow_statement(_cash_flow())

    assert (
        statement["validation"]["has_unclassified_cash_movement"]
        is True
    )


def test_standard_cash_flow_statement_preserves_cash_accounts() -> None:
    statement = generate_standard_cash_flow_statement(_cash_flow())

    assert len(statement["cash_accounts"]) == 1
    assert statement["cash_accounts"][0]["account_number"] == "210001"
    assert statement["cash_accounts"][0]["net_movement"] == 115000.0


def test_standard_cash_flow_statement_preserves_diagnostics() -> None:
    statement = generate_standard_cash_flow_statement(_cash_flow())

    diagnostics = statement["classification_diagnostics"]

    assert diagnostics["document_count"] == 12
    assert diagnostics["classified_document_count"] == 11
    assert diagnostics["unclassified_document_count"] == 1
    assert diagnostics["activity_detail_count"] == 12


def test_standard_cash_flow_statement_handles_missing_values() -> None:
    statement = generate_standard_cash_flow_statement({})

    assert statement["sections"]["operating_activities"]["amount"] == 0.0
    assert statement["sections"]["investing_activities"]["amount"] == 0.0
    assert statement["sections"]["financing_activities"]["amount"] == 0.0
    assert statement["unclassified_cash_movement"] == 0.0
    assert statement["net_change_in_cash"] == 0.0

    assert statement["reconciliation"]["difference"] == 0.0
    assert statement["reconciliation"]["is_reconciled"] is True