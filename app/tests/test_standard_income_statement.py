from copy import deepcopy

from app.services.standard_income_statement import (
    generate_standard_income_statement,
)


def _accounts():
    return {
        "700100": {
            "account_number": "700100",
            "account_name": "Grant Revenue",
            "parent_account": "700000",
            "level": 3,
            "financial_category": "Revenue",
            "financial_subcategory": "Grant Revenue",
            "income_balance": "Income Statement",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
        "700200": {
            "account_number": "700200",
            "account_name": "Other Revenue",
            "parent_account": "700000",
            "level": 3,
            "financial_category": "Revenue",
            "financial_subcategory": "Other Revenue",
            "income_balance": "Income Statement",
            "normal_balance": "Credit",
            "is_posting_account": True,
        },
        "600100": {
            "account_number": "600100",
            "account_name": "Personnel Expense",
            "parent_account": "600000",
            "level": 3,
            "financial_category": "Expense",
            "financial_subcategory": "Personnel",
            "income_balance": "Income Statement",
            "normal_balance": "Debit",
            "is_posting_account": True,
        },
        "600200": {
            "account_number": "600200",
            "account_name": "Program Expense",
            "parent_account": "600000",
            "level": 3,
            "financial_category": "Expense",
            "financial_subcategory": "Programs",
            "income_balance": "Income Statement",
            "normal_balance": "Debit",
            "is_posting_account": True,
        },
        "600000": {
            "account_number": "600000",
            "account_name": "Expenses",
            "parent_account": None,
            "level": 2,
            "financial_category": "Expense",
            "financial_subcategory": None,
            "income_balance": "Income Statement",
            "normal_balance": "Debit",
            "is_posting_account": False,
        },
        "200100": {
            "account_number": "200100",
            "account_name": "Cash",
            "parent_account": "200000",
            "level": 3,
            "financial_category": "Asset",
            "financial_subcategory": "Cash",
            "income_balance": "Balance Sheet",
            "normal_balance": "Debit",
            "is_posting_account": True,
        },
    }


def _transactions():
    return [
        {
            "posting_date": "2026-01-10",
            "account_number": "700100",
            "debit_amount": 0,
            "credit_amount": 1000,
        },
        {
            "posting_date": "2026-02-10",
            "account_number": "700200",
            "debit_amount": 0,
            "credit_amount": 200,
        },
        {
            "posting_date": "2026-01-15",
            "account_number": "600100",
            "debit_amount": 400,
            "credit_amount": 0,
        },
        {
            "posting_date": "2026-02-15",
            "account_number": "600200",
            "debit_amount": 300,
            "credit_amount": 0,
        },
        {
            "posting_date": "2026-02-20",
            "account_number": "200100",
            "debit_amount": 500,
            "credit_amount": 0,
        },
    ]


def _validated_income_statement():
    return {
        "revenue": 1200.0,
        "expenses": 700.0,
        "net_profit": 500.0,
        "latest_closing_date": None,
        "current_period_revenue": 1200.0,
        "current_period_expenses": 700.0,
        "current_period_result": 500.0,
    }


def test_standard_income_statement_reconciles():
    report = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=_validated_income_statement(),
    )

    assert report["status"] == "available"

    assert report["totals"] == {
        "revenue": 1200.0,
        "expenses": 700.0,
        "net_result": 500.0,
    }

    assert report["reconciliation"]["reconciled"] is True
    assert report["reconciliation"]["revenue_difference"] == 0.0
    assert report["reconciliation"]["expense_difference"] == 0.0
    assert report["reconciliation"]["net_result_difference"] == 0.0


def test_standard_income_statement_preserves_account_detail():
    report = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=_validated_income_statement(),
    )

    revenue_section = report["sections"][0]
    expense_section = report["sections"][1]

    assert revenue_section["section"] == "Revenue"
    assert expense_section["section"] == "Expenses"

    assert len(revenue_section["lines"]) == 2
    assert len(expense_section["lines"]) == 2

    grant_revenue = revenue_section["lines"][0]

    assert grant_revenue["account_number"] == "700100"
    assert grant_revenue["account_name"] == "Grant Revenue"
    assert grant_revenue["parent_account"] == "700000"
    assert grant_revenue["level"] == 3
    assert grant_revenue["financial_subcategory"] == "Grant Revenue"
    assert grant_revenue["amount"] == 1000.0


def test_standard_income_statement_excludes_balance_sheet_accounts():
    report = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=_validated_income_statement(),
    )

    account_numbers = {
        line["account_number"]
        for section in report["sections"]
        for line in section["lines"]
    }

    assert "200100" not in account_numbers


def test_standard_income_statement_excludes_non_posting_accounts():
    report = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=_validated_income_statement(),
    )

    account_numbers = {
        line["account_number"]
        for section in report["sections"]
        for line in section["lines"]
    }

    assert "600000" not in account_numbers


def test_standard_income_statement_detects_reconciliation_failure():
    validated = _validated_income_statement()

    validated["current_period_expenses"] = 750.0
    validated["current_period_result"] = 450.0

    report = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=validated,
    )

    assert report["status"] == "reconciliation_failed"
    assert report["reconciliation"]["reconciled"] is False
    assert report["reconciliation"]["expense_difference"] == -50.0
    assert report["reconciliation"]["net_result_difference"] == 50.0


def test_standard_income_statement_uses_current_period_after_closing_date():
    transactions = [
        {
            "posting_date": "2025-12-20",
            "account_number": "700100",
            "debit_amount": 0,
            "credit_amount": 5000,
        },
        {
            "posting_date": "2026-01-10",
            "account_number": "700100",
            "debit_amount": 0,
            "credit_amount": 1000,
        },
        {
            "posting_date": "2026-01-15",
            "account_number": "600100",
            "debit_amount": 400,
            "credit_amount": 0,
        },
    ]

    validated = {
        "revenue": 6000.0,
        "expenses": 400.0,
        "net_profit": 5600.0,
        "latest_closing_date": "2025-12-31",
        "current_period_revenue": 1000.0,
        "current_period_expenses": 400.0,
        "current_period_result": 600.0,
    }

    report = generate_standard_income_statement(
        transactions=transactions,
        accounts_by_number=_accounts(),
        validated_income_statement=validated,
    )

    assert report["status"] == "available"
    assert report["totals"]["revenue"] == 1000.0
    assert report["totals"]["expenses"] == 400.0
    assert report["totals"]["net_result"] == 600.0


def test_standard_income_statement_does_not_mutate_validated_inputs():
    transactions = _transactions()
    accounts = _accounts()
    validated = _validated_income_statement()

    original_transactions = deepcopy(transactions)
    original_accounts = deepcopy(accounts)
    original_validated = deepcopy(validated)

    generate_standard_income_statement(
        transactions=transactions,
        accounts_by_number=accounts,
        validated_income_statement=validated,
    )

    assert transactions == original_transactions
    assert accounts == original_accounts
    assert validated == original_validated


def test_standard_income_statement_controls_are_protected():
    report = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=_validated_income_statement(),
    )

    controls = report["controls"]

    assert controls["reporting_layer_only"] is True
    assert controls["validated_income_statement_preserved"] is True
    assert controls["financial_recalculation_performed"] is False
    assert controls["posting_accounts_only"] is True
    assert controls["income_statement_accounts_only"] is True
    assert controls["missing_accounts_not_invented"] is True
    assert controls["hierarchy_metadata_preserved"] is True
    assert controls["reconciliation_required"] is True

def test_organization_exposes_standard_income_statement():
    from app.organization import Organization

    assert hasattr(
        Organization,
        "process_financials",
    )

    source = __import__(
        "inspect"
    ).getsource(
        Organization.process_financials
    )

    assert (
        "generate_standard_income_statement"
        in source
    )

    assert (
        "validated_income_statement=self.income_statement"
        in source
    )


def test_standard_income_statement_is_generated_after_validated_income_statement():
    from app.organization import Organization
    import inspect

    source = inspect.getsource(
        Organization.process_financials
    )

    validated_position = source.find(
        "self.income_statement = generate_income_statement"
    )

    standard_position = source.find(
        "self.standard_income_statement ="
    )

    balance_sheet_position = source.find(
        "self.balance_sheet = generate_balance_sheet"
    )

    assert validated_position != -1
    assert standard_position != -1
    assert balance_sheet_position != -1

    assert (
        validated_position
        < standard_position
        < balance_sheet_position
    )

def test_standard_income_statement_persists_separately(
    tmp_path,
):
    from app.services.financial_model_service import (
        FinancialModelService,
    )

    validated = _validated_income_statement()

    standard = generate_standard_income_statement(
        transactions=_transactions(),
        accounts_by_number=_accounts(),
        validated_income_statement=validated,
    )

    saved_files = (
        FinancialModelService.save_financial_outputs(
            financial_model_folder=tmp_path,
            trial_balance={},
            income_statement=validated,
            standard_income_statement=standard,
            balance_sheet={},
            standard_balance_sheet={},
            cash_flow={},
            standard_cash_flow_statement={},
            liquidity={},
            financial_facts={},
            financial_analysis={},
            financial_trends={},
            financial_forecast={},
        )
    )

    validated_path = (
        tmp_path / "income_statement.json"
    )

    standard_path = (
        tmp_path
        / "standard_income_statement.json"
    )

    assert validated_path.exists()
    assert standard_path.exists()

    assert (
        saved_files["income_statement"]
        == str(validated_path)
    )

    assert (
        saved_files["standard_income_statement"]
        == str(standard_path)
    )

    validated_persisted = (
        FinancialModelService.load_json(
            tmp_path,
            "income_statement.json",
        )
    )

    standard_persisted = (
        FinancialModelService.load_json(
            tmp_path,
            "standard_income_statement.json",
        )
    )

    assert validated_persisted == validated

    assert (
        standard_persisted["status"]
        == "available"
    )

    assert (
        standard_persisted["reconciliation"][
            "reconciled"
        ]
        is True
    )

    assert (
        standard_persisted["totals"][
            "net_result"
        ]
        == 500.0
    )

    assert (
        standard_persisted
        != validated_persisted
    )        