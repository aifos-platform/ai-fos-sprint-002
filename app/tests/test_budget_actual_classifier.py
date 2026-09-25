from app.services.budget_actual_classifier import BudgetActualClassifier


def test_capital_asset_purchase_with_budget_line_is_budget_consuming():
    classifier = BudgetActualClassifier()

    transaction = {
        "account_number": "250001",
        "amount": 2500.00,
        "budget_line_code": "BL-EQUIPMENT",
    }

    accounts_by_number = {
        "250001": {
            "financial_category": "Asset",
            "financial_subcategory": "Computer Equipment",
        }
    }

    result = classifier.classify(
        transaction,
        accounts_by_number,
    )

    assert result["is_budget_consuming"] is True
    assert result["budget_actual_amount"] == 2500.00
    assert result["budget_treatment"] == "capital_purchase"
    assert result["account_category"] == "Asset"
    assert result["budget_line_code"] == "BL-EQUIPMENT"
