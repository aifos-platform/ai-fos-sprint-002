from app.services.financial_model_service import FinancialModelService


def test_standard_cash_flow_statement_persists_separately(tmp_path):
    standard_cash_flow_statement = {
        "status": "available",
        "statement_name": "Standard Cash Flow Statement",
        "sections": {
            "operating_activities": {
                "amount": 100000.0,
            },
            "investing_activities": {
                "amount": -30000.0,
            },
            "financing_activities": {
                "amount": 15000.0,
            },
        },
        "net_change_in_cash": 85000.0,
    }

    saved_files = FinancialModelService.save_financial_outputs(
        financial_model_folder=tmp_path,
        trial_balance={},
        income_statement={},
        standard_income_statement={},
        balance_sheet={},
        standard_balance_sheet={},
        cash_flow={},
        standard_cash_flow_statement=standard_cash_flow_statement,
        liquidity={},
        financial_facts={},
        financial_analysis={},
        financial_trends={},
        financial_forecast={},
    )

    standard_path = tmp_path / "standard_cash_flow_statement.json"

    assert standard_path.exists()

    assert (
        saved_files["standard_cash_flow_statement"]
        == str(standard_path)
    )

    persisted = FinancialModelService.load_json(
        financial_model_folder=tmp_path,
        filename="standard_cash_flow_statement.json",
    )

    assert persisted == standard_cash_flow_statement