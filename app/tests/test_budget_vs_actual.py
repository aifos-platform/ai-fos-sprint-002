from app.services.budget_vs_actual import generate_budget_vs_actual


EXPENSE_ACCOUNTS = {
    "6000": {
        "account_number": "6000",
        "account_name": "Program Expenses",
        "financial_category": "Expense",
    }
}


def test_fiscal_year_budget_remains_separate_from_spending_plan():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "Spending Plan (2026)",
                    "type": "spending_plan",
                    "fiscal_year": 2026,
                    "amount": 50000,
                },
            ],
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=[],
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["fiscal_year"] == 2026
    assert line["budget"] is None
    assert line["spending_plan"] == 50000.0
    assert line["variance"] is None
    assert line["utilization_percentage"] is None
    assert line["status"] == "Budget Not Identified"


def test_fiscal_year_requested_amount_is_not_treated_as_budget():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "Requested 2026",
                    "type": "requested",
                    "fiscal_year": 2026,
                    "amount": 75000,
                },
            ],
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=[],
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["fiscal_year"] == 2026
    assert line["budget"] is None
    assert line["requested"] == 75000.0
    assert line["status"] == "Budget Not Identified"


def test_fiscal_year_forecast_is_not_treated_as_budget():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "Forecast 2027",
                    "type": "forecast",
                    "fiscal_year": 2027,
                    "amount": 90000,
                },
            ],
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=[],
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["fiscal_year"] == 2027
    assert line["budget"] is None
    assert line["forecast"] == 90000.0
    assert line["variance"] is None
    assert line["utilization_percentage"] is None
    assert line["status"] == "Budget Not Identified"


def test_fiscal_year_budget_amount_drives_variance_and_utilization():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "Budget 2026",
                    "type": "budget",
                    "fiscal_year": 2026,
                    "amount": 100000,
                },
            ],
        },
    ]

    transactions = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "account_number": "6000",
            "fiscal_year": 2026,
            "debit_amount": 60000,
            "credit_amount": 0,
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["fiscal_year"] == 2026
    assert line["budget"] == 100000.0
    assert line["actual"] == 60000.0
    assert line["variance"] == 40000.0
    assert line["utilization_percentage"] == 60.0
    assert line["status"] == "Within Budget"


def test_fiscal_year_budget_can_be_over_budget():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "FY26 Budget",
                    "type": "budget",
                    "fiscal_year": 2026,
                    "amount": 100000,
                },
            ],
        },
    ]

    transactions = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "account_number": "6000",
            "fiscal_year": 2026,
            "debit_amount": 120000,
            "credit_amount": 0,
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["budget"] == 100000.0
    assert line["actual"] == 120000.0
    assert line["variance"] == -20000.0
    assert line["utilization_percentage"] == 120.0
    assert line["status"] == "Over Budget"


def test_fiscal_year_actual_can_be_derived_from_posting_date():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "Budget 2025",
                    "type": "budget",
                    "fiscal_year": 2025,
                    "amount": 50000,
                },
            ],
        },
    ]

    transactions = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "account_number": "6000",
            "posting_date": "2025-06-30",
            "debit_amount": 25000,
            "credit_amount": 0,
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["fiscal_year"] == 2025
    assert line["actual"] == 25000.0
    assert line["utilization_percentage"] == 50.0


def test_fiscal_year_backward_compatibility_with_explicit_fiscal_year():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "fiscal_year": 2024,
            "original_budget": 80000,
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=[],
    )

    line = result["by_fiscal_year"]["lines"][0]

    assert line["fiscal_year"] == 2024
    assert line["budget"] == 80000.0
    assert line["actual"] == 0.0
    assert line["variance"] == 80000.0
    assert line["utilization_percentage"] == 0.0
    assert line["status"] == "Within Budget"


def test_fiscal_year_summary_counts_semantic_years_correctly():
    budget_lines = [
        {
            "fund_code": "FUND-1",
            "budget_line_code": "BL-1",
            "period_amounts": [
                {
                    "header": "Requested 2026",
                    "type": "requested",
                    "fiscal_year": 2026,
                    "amount": 50000,
                },
                {
                    "header": "Spending Plan (2027)",
                    "type": "spending_plan",
                    "fiscal_year": 2027,
                    "amount": 30000,
                },
                {
                    "header": "Budget 2028",
                    "type": "budget",
                    "fiscal_year": 2028,
                    "amount": 70000,
                },
                {
                    "header": "Forecast 2029",
                    "type": "forecast",
                    "fiscal_year": 2029,
                    "amount": 90000,
                },
            ],
        },
    ]

    result = generate_budget_vs_actual(
        budget_lines=budget_lines,
        transactions=[],
    )

    summary = result["by_fiscal_year"]["summary"]

    assert summary["year_count"] == 4
    assert summary["budget_year_count"] == 1
    assert summary["requested_year_count"] == 1
    assert summary["spending_plan_year_count"] == 1
    assert summary["forecast_year_count"] == 1