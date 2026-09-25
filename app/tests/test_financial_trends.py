from app.services.financial_trends import generate_financial_trends


def _accounts() -> dict:
    return {
        "4000": {
            "income_balance": "Income Statement",
            "is_posting_account": True,
            "financial_category": "Revenue",
        },
        "6000": {
            "income_balance": "Income Statement",
            "is_posting_account": True,
            "financial_category": "Expense",
        },
        "1000": {
            "income_balance": "Balance Sheet",
            "is_posting_account": True,
            "financial_category": "Asset",
        },
    }


def test_financial_trends_build_monthly_series():
    transactions = [
        {
            "posting_date": "2026-01-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        },
        {
            "posting_date": "2026-01-15",
            "account_number": "6000",
            "debit": 600,
            "credit": 0,
        },
        {
            "posting_date": "2026-02-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1200,
        },
        {
            "posting_date": "2026-02-15",
            "account_number": "6000",
            "debit": 700,
            "credit": 0,
        },
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    assert result["status"] == "available"
    assert len(result["monthly_series"]) == 2

    january = result["monthly_series"][0]
    february = result["monthly_series"][1]

    assert january["period"] == "2026-01"
    assert january["revenue"] == 1000.0
    assert january["expenses"] == 600.0
    assert january["net_result"] == 400.0

    assert february["period"] == "2026-02"
    assert february["revenue"] == 1200.0
    assert february["expenses"] == 700.0
    assert february["net_result"] == 500.0


def test_financial_trends_build_annual_series():
    transactions = [
        {
            "posting_date": "2025-12-15",
            "account_number": "4000",
            "debit": 0,
            "credit": 800,
        },
        {
            "posting_date": "2025-12-20",
            "account_number": "6000",
            "debit": 500,
            "credit": 0,
        },
        {
            "posting_date": "2026-01-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        },
        {
            "posting_date": "2026-01-20",
            "account_number": "6000",
            "debit": 650,
            "credit": 0,
        },
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    assert len(result["annual_series"]) == 2

    assert result["annual_series"][0] == {
        "period": "2025",
        "revenue": 800.0,
        "expenses": 500.0,
        "net_result": 300.0,
    }

    assert result["annual_series"][1] == {
        "period": "2026",
        "revenue": 1000.0,
        "expenses": 650.0,
        "net_result": 350.0,
    }


def test_latest_month_comparison_reports_direction_and_change():
    transactions = [
        {
            "posting_date": "2026-01-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        },
        {
            "posting_date": "2026-01-15",
            "account_number": "6000",
            "debit": 600,
            "credit": 0,
        },
        {
            "posting_date": "2026-02-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1200,
        },
        {
            "posting_date": "2026-02-15",
            "account_number": "6000",
            "debit": 500,
            "credit": 0,
        },
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    comparison = result["latest_month_comparison"]

    assert comparison["current_period"] == "2026-02"
    assert comparison["previous_period"] == "2026-01"

    assert comparison["revenue"]["direction"] == "increased"
    assert comparison["revenue"]["change_amount"] == 200.0
    assert comparison["revenue"]["change_percentage"] == 20.0

    assert comparison["expenses"]["direction"] == "decreased"
    assert comparison["expenses"]["change_amount"] == -100.0

    assert comparison["net_result"]["direction"] == "increased"


def test_zero_previous_value_does_not_invent_percentage():
    transactions = [
        {
            "posting_date": "2026-01-10",
            "account_number": "6000",
            "debit": 500,
            "credit": 0,
        },
        {
            "posting_date": "2026-02-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        },
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    comparison = result["latest_month_comparison"]

    assert comparison["revenue"]["previous_value"] == 0.0
    assert comparison["revenue"]["change_percentage"] is None


def test_balance_sheet_accounts_are_excluded():
    transactions = [
        {
            "posting_date": "2026-01-10",
            "account_number": "1000",
            "debit": 5000,
            "credit": 0,
        },
        {
            "posting_date": "2026-01-11",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        },
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    january = result["monthly_series"][0]

    assert january["revenue"] == 1000.0
    assert january["expenses"] == 0.0
    assert january["net_result"] == 1000.0
    assert result["quality"]["included_transaction_count"] == 1


def test_invalid_and_missing_dates_are_reported():
    transactions = [
        {
            "posting_date": None,
            "account_number": "4000",
            "debit": 0,
            "credit": 500,
        },
        {
            "posting_date": "not-a-date",
            "account_number": "6000",
            "debit": 200,
            "credit": 0,
        },
        {
            "posting_date": "2026-01-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        },
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    assert result["quality"]["skipped_missing_date_count"] == 1
    assert result["quality"]["skipped_invalid_date_count"] == 1
    assert result["quality"]["included_transaction_count"] == 1


def test_single_observed_period_has_no_comparison():
    transactions = [
        {
            "posting_date": "2026-01-10",
            "account_number": "4000",
            "debit": 0,
            "credit": 1000,
        }
    ]

    result = generate_financial_trends(
        transactions=transactions,
        accounts_by_number=_accounts(),
    )

    assert result["latest_month_comparison"] is None
    assert result["latest_year_comparison"] is None