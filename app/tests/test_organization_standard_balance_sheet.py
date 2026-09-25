from app.organization import Organization


def test_organization_initializes_standard_balance_sheet():
    organization = Organization()

    assert organization.standard_balance_sheet is None


def test_organization_builds_standard_balance_sheet_from_validated_balance_sheet():
    organization = Organization()

    organization.trial_balance = {
        "201100": {
            "account_name": "Cash",
            "total_debit": 1500.0,
            "total_credit": 0.0,
        },
        "401100": {
            "account_name": "Accounts Payable",
            "total_debit": 0.0,
            "total_credit": 900.0,
        },
        "101100": {
            "account_name": "Equity",
            "total_debit": 0.0,
            "total_credit": 400.0,
        },
    }

    organization.accounts_by_number = {
        "201100": {
            "account_number": "201100",
            "account_name": "Cash",
            "parent_account": None,
            "level": 1,
            "financial_category": "Asset",
            "income_balance": "Balance Sheet",
            "normal_balance": "Debit",
            "is_posting_account": True,
        },
        "401100": {
            "account_number": "401100",
            "account_name": "Accounts Payable",
            "parent_account": None,
            "level": 1,
            "financial_category": "Liability",
            "income_balance": "Balance Sheet",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
        "101100": {
            "account_number": "101100",
            "account_name": "Equity",
            "parent_account": None,
            "level": 1,
            "financial_category": "Equity",
            "income_balance": "Balance Sheet",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
    }

    organization.balance_sheet = {
        "assets": 1500.0,
        "liabilities": 900.0,
        "reported_equity": 400.0,
        "current_period_result": 200.0,
        "equity": 600.0,
        "liabilities_and_equity": 1500.0,
        "difference": 0.0,
    }

    # Build only the new reporting layer. The authoritative validated
    # Balance Sheet must remain unchanged.
    original_balance_sheet = dict(organization.balance_sheet)

    from app.services.standard_balance_sheet import (
        generate_standard_balance_sheet,
    )

    organization.standard_balance_sheet = (
        generate_standard_balance_sheet(
            trial_balance=organization.trial_balance,
            accounts_by_number=organization.accounts_by_number,
            validated_balance_sheet=organization.balance_sheet,
        )
    )

    assert organization.standard_balance_sheet["status"] == "available"

    assert (
        organization.standard_balance_sheet["reconciliation"]["reconciled"]
        is True
    )

    assert organization.standard_balance_sheet["totals"]["assets"] == 1500.0
    assert organization.standard_balance_sheet["totals"]["liabilities"] == 900.0

    assert (
        organization.standard_balance_sheet["totals"]["reported_equity"]
        == 400.0
    )

    assert (
        organization.standard_balance_sheet["totals"]["current_period_result"]
        == 200.0
    )

    assert organization.standard_balance_sheet["totals"]["equity"] == 600.0

    assert organization.balance_sheet == original_balance_sheet