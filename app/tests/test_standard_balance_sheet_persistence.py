from app.services.financial_model_service import FinancialModelService


def test_standard_balance_sheet_persists_separately(tmp_path):
    standard_balance_sheet = {
        "status": "available",
        "report_type": "standard_balance_sheet",
        "totals": {
            "assets": 1500.0,
            "liabilities": 500.0,
            "equity": 1000.0,
        },
        "sections": [],
        "reconciliation": {
            "reconciled": True,
        },
    }

    saved_files = FinancialModelService.save_financial_outputs(
        financial_model_folder=tmp_path,
        trial_balance={},
        income_statement={},
        standard_income_statement={},
        balance_sheet={},
        standard_balance_sheet=standard_balance_sheet,
        cash_flow={},
        standard_cash_flow_statement={},
        liquidity={},
        financial_facts={},
        financial_analysis={},
        financial_trends={},
        financial_forecast={},
    )

    standard_path = tmp_path / "standard_balance_sheet.json"

    assert standard_path.exists()

    assert (
        saved_files["standard_balance_sheet"]
        == str(standard_path)
    )

    persisted = FinancialModelService.load_json(
        financial_model_folder=tmp_path,
        filename="standard_balance_sheet.json",
    )

    assert persisted == standard_balance_sheet