from app.services.liquidity import calculate_liquidity


def test_calculate_liquidity_separates_available_and_blocked_cash():
    trial_balance = {
        "101000": {
            "total_debit": 150000.0,
            "total_credit": 50000.0,
        },
        "102000": {
            "total_debit": 250000.0,
            "total_credit": 50000.0,
        },
    }

    accounts_by_number = {
        "101000": {
            "account_number": "101000",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Available",
        },
        "102000": {
            "account_number": "102000",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Blocked",
        },
    }

    result = calculate_liquidity(
        transactions=[],
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    assert result["available_cash"] == 100000.0
    assert result["blocked_cash"] == 200000.0
    assert result["total_cash"] == 300000.0
    assert result["available_account_count"] == 1
    assert result["blocked_account_count"] == 1

def test_calculate_liquidity_uses_coa_balance_when_cash_account_missing_from_gl():
    trial_balance = {
        "101000": {
            "total_debit": 150000.0,
            "total_credit": 50000.0,
        },
    }

    accounts_by_number = {
        "101000": {
            "account_number": "101000",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Available",
            "balance": 100000.0,
        },
        "102000": {
            "account_number": "102000",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Blocked",
            "balance": 200000.0,
        },
    }

    result = calculate_liquidity(
        transactions=[],
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    assert result["available_cash"] == 100000.0
    assert result["blocked_cash"] == 200000.0
    assert result["total_cash"] == 300000.0

    assert result["available_account_count"] == 1
    assert result["blocked_account_count"] == 1  

def test_calculate_liquidity_does_not_use_coa_fallback_when_account_exists_in_gl():
    trial_balance = {
        "102000": {
            "total_debit": 0.0,
            "total_credit": 0.0,
        },
    }

    accounts_by_number = {
        "102000": {
            "account_number": "102000",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Blocked",
            "balance": 200000.0,
        },
    }

    result = calculate_liquidity(
        transactions=[],
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    assert result["blocked_cash"] == 0.0
    assert result["total_cash"] == 0.0
    assert result["blocked_account_count"] == 1

def test_calculate_liquidity_prefers_gl_when_all_cash_accounts_exist_in_gl():
    trial_balance = {
        "512100": {
            "total_debit": 500000.0,
            "total_credit": 143987.0,
        },
        "512400": {
            "total_debit": 1311810.50,
            "total_credit": 29.72,
        },
    }

    accounts_by_number = {
        "512100": {
            "account_number": "512100",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Available",
            "balance": 999999.0,
        },
        "512400": {
            "account_number": "512400",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Blocked",
            "balance": 999999.0,
        },
    }

    result = calculate_liquidity(
        transactions=[],
        trial_balance=trial_balance,
        accounts_by_number=accounts_by_number,
    )

    assert result["available_cash"] == 356013.0
    assert result["blocked_cash"] == 1311780.78
    assert result["total_cash"] == 1667793.78

    assert result["available_account_count"] == 1
    assert result["blocked_account_count"] == 1          