from copy import deepcopy

from app.services.standard_balance_sheet import (
    generate_standard_balance_sheet,
)


def _accounts():
    return {
        "200000": {
            "account_number": "200000",
            "account_name": "Assets",
            "parent_account": None,
            "level": 0,
            "financial_category": "Asset",
            "financial_subcategory": "Assets",
            "income_balance": "Balance Sheet",
            "normal_balance": "Debit",
            "is_posting_account": False,
        },
        "201100": {
            "account_number": "201100",
            "account_name": "Cash at Bank",
            "parent_account": "200000",
            "level": 1,
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Cash Equivalents",
            "income_balance": "Balance Sheet",
            "normal_balance": "Debit",
            "is_posting_account": True,
        },
        "201200": {
            "account_number": "201200",
            "account_name": "Receivables",
            "parent_account": "200000",
            "level": 1,
            "financial_category": "Asset",
            "financial_subcategory": "Receivables",
            "income_balance": "Balance Sheet",
            "normal_balance": "Debit",
            "is_posting_account": True,
        },
        "400000": {
            "account_number": "400000",
            "account_name": "Liabilities",
            "parent_account": None,
            "level": 0,
            "financial_category": "Liability",
            "financial_subcategory": "Liabilities",
            "income_balance": "Balance Sheet",
            "normal_balance": "Credit",
            "is_posting_account": False,
        },
        "401100": {
            "account_number": "401100",
            "account_name": "Accounts Payable",
            "parent_account": "400000",
            "level": 1,
            "financial_category": "Liability",
            "financial_subcategory": "Accounts Payable",
            "income_balance": "Balance Sheet",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
        "100000": {
            "account_number": "100000",
            "account_name": "Equity",
            "parent_account": None,
            "level": 0,
            "financial_category": "Equity",
            "financial_subcategory": "Equity",
            "income_balance": "Balance Sheet",
            "normal_balance": "Credit",
            "is_posting_account": False,
        },
        "101100": {
            "account_number": "101100",
            "account_name": "Accumulated Equity",
            "parent_account": "100000",
            "level": 1,
            "financial_category": "Equity",
            "financial_subcategory": "Capital and Equity",
            "income_balance": "Balance Sheet",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
        "701000": {
            "account_number": "701000",
            "account_name": "Donor Revenue",
            "parent_account": None,
            "level": 1,
            "financial_category": "Revenue",
            "financial_subcategory": "Revenue",
            "income_balance": "Income Statement",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
    }


def _trial_balance():
    return {
        "201100": {
            "account_name": "Cash at Bank",
            "total_debit": 1000.0,
            "total_credit": 0.0,
        },
        "201200": {
            "account_name": "Receivables",
            "total_debit": 500.0,
            "total_credit": 0.0,
        },
        "401100": {
            "account_name": "Accounts Payable",
            "total_debit": 0.0,
            "total_credit": 900.0,
        },
        "101100": {
            "account_name": "Accumulated Equity",
            "total_debit": 0.0,
            "total_credit": 400.0,
        },
        "701000": {
            "account_name": "Donor Revenue",
            "total_debit": 0.0,
            "total_credit": 200.0,
        },
    }


def _validated_balance_sheet():
    return {
        "assets": 1500.0,
        "liabilities": 900.0,
        "reported_equity": 400.0,
        "current_period_result": 200.0,
        "equity": 600.0,
        "liabilities_and_equity": 1500.0,
        "difference": 0.0,
    }


def test_standard_balance_sheet_reconciles_to_validated_balance_sheet():
    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=_validated_balance_sheet(),
    )

    assert result["status"] == "available"
    assert result["reconciliation"]["reconciled"] is True

    assert result["totals"]["assets"] == 1500.0
    assert result["totals"]["liabilities"] == 900.0
    assert result["totals"]["reported_equity"] == 400.0
    assert result["totals"]["current_period_result"] == 200.0
    assert result["totals"]["equity"] == 600.0
    assert result["totals"]["liabilities_and_equity"] == 1500.0
    assert result["totals"]["difference"] == 0.0


def test_standard_balance_sheet_preserves_detailed_account_lines():
    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=_validated_balance_sheet(),
    )

    assets = result["sections"][0]["lines"]

    assert len(assets) == 2

    assert assets[0]["account_number"] == "201100"
    assert assets[0]["account_name"] == "Cash at Bank"
    assert assets[0]["parent_account"] == "200000"
    assert assets[0]["level"] == 1
    assert assets[0]["amount"] == 1000.0

    assert assets[1]["account_number"] == "201200"
    assert assets[1]["amount"] == 500.0


def test_standard_balance_sheet_excludes_non_posting_accounts():
    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=_validated_balance_sheet(),
    )

    account_numbers = {
        line["account_number"]
        for section in result["sections"]
        for line in section["lines"]
    }

    assert "200000" not in account_numbers
    assert "400000" not in account_numbers
    assert "100000" not in account_numbers


def test_standard_balance_sheet_excludes_income_statement_accounts():
    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=_validated_balance_sheet(),
    )

    account_numbers = {
        line["account_number"]
        for section in result["sections"]
        for line in section["lines"]
    }

    assert "701000" not in account_numbers


def test_standard_balance_sheet_preserves_current_period_result():
    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=_validated_balance_sheet(),
    )

    equity_section = result["sections"][2]

    assert equity_section["reported_equity"] == 400.0
    assert equity_section["current_period_result"] == 200.0
    assert equity_section["total"] == 600.0


def test_standard_balance_sheet_reports_reconciliation_failure():
    validated = _validated_balance_sheet()
    validated["assets"] = 1600.0

    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=validated,
    )

    assert result["status"] == "reconciliation_failed"
    assert result["reconciliation"]["reconciled"] is False
    assert result["reconciliation"]["asset_difference"] == -100.0

    # Detailed source result must not be changed merely to force agreement.
    assert result["totals"]["assets"] == 1500.0


def test_standard_balance_sheet_does_not_mutate_inputs():
    trial_balance = _trial_balance()
    accounts = _accounts()
    validated = _validated_balance_sheet()

    original_trial_balance = deepcopy(trial_balance)
    original_accounts = deepcopy(accounts)
    original_validated = deepcopy(validated)

    generate_standard_balance_sheet(
        trial_balance=trial_balance,
        accounts_by_number=accounts,
        validated_balance_sheet=validated,
    )

    assert trial_balance == original_trial_balance
    assert accounts == original_accounts
    assert validated == original_validated


def test_standard_balance_sheet_controls_protect_validated_finance():
    result = generate_standard_balance_sheet(
        trial_balance=_trial_balance(),
        accounts_by_number=_accounts(),
        validated_balance_sheet=_validated_balance_sheet(),
    )

    controls = result["controls"]

    assert controls["reporting_layer_only"] is True
    assert controls["validated_balance_sheet_preserved"] is True
    assert controls["financial_recalculation_performed"] is False
    assert controls["missing_accounts_not_invented"] is True
    assert controls["reconciliation_required"] is True