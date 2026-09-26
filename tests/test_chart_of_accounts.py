from app.services.chart_of_accounts import ChartOfAccounts
from app.services.chart_normalizer import ChartNormalizer
import pandas as pd

def test_chart_of_accounts_import():
    chart = ChartOfAccounts()

    chart.load_chart("uploads/Chart of Accounts (31).xlsx")

    detected_columns = chart.detect_columns()
    validation = chart.validate_chart()
    accounts = chart.build_hierarchy()

    print("\nDetected columns:")
    print(detected_columns)

    print("\nValidation:")
    print(validation)

    print("\nFirst five accounts:")
    print(accounts[:5])

    assert detected_columns["account_number"] is not None
    assert detected_columns["account_name"] is not None
    assert len(accounts) > 0

def test_enrich_accounts_preserves_imported_liquidity_status():
    chart = ChartOfAccounts()

    chart.accounts = [
        {
            "account_number": "101000",
            "account_name": "Blocked Bank Account",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Blocked",
        },
        {
            "account_number": "102000",
            "account_name": "Available Bank Account",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": "Available",
        },
    ]

    accounts = chart.enrich_accounts()

    blocked_account = next(
        account
        for account in accounts
        if account["account_number"] == "101000"
    )

    available_account = next(
        account
        for account in accounts
        if account["account_number"] == "102000"
    )

    assert blocked_account["liquidity_status"] == "Blocked"
    assert available_account["liquidity_status"] == "Available"   

def test_chart_normalizer_normalizes_liquidity_status():
    normalizer = ChartNormalizer()

    blocked = normalizer.normalize_account(
        account_number="101000",
        account_name="Blocked Bank",
        liquidity_status="blocked",
    )

    available = normalizer.normalize_account(
        account_number="102000",
        account_name="Available Bank",
        liquidity_status="available",
    )

    not_applicable = normalizer.normalize_account(
        account_number="103000",
        account_name="Non Cash Account",
        liquidity_status="N/A",
    )

    assert blocked["liquidity_status"] == "Blocked"
    assert available["liquidity_status"] == "Available"
    assert (
        not_applicable["liquidity_status"]
        == "Not Applicable"
    )

def test_chart_import_preserves_liquidity_status(tmp_path):
    file_path = tmp_path / "chart_with_liquidity.xlsx"

    source_data = pd.DataFrame(
        [
            {
                "Account Number": "101000",
                "Account Name": "Blocked Bank Account",
                "Account Category": "Asset",
                "Account Subcategory": "Cash and Bank",
                "Account Type": "Posting",
                "Liquidity Status": "Blocked",
            },
            {
                "Account Number": "102000",
                "Account Name": "Available Bank Account",
                "Account Category": "Asset",
                "Account Subcategory": "Cash and Bank",
                "Account Type": "Posting",
                "Liquidity Status": "Available",
            },
        ]
    )

    source_data.to_excel(
        file_path,
        index=False,
    )

    chart = ChartOfAccounts()

    chart.load_chart(str(file_path))
    detected_columns = chart.detect_columns()
    chart.build_hierarchy()
    accounts = chart.enrich_accounts()

    assert (
        detected_columns["liquidity_status"]
        == "Liquidity Status"
    )

    blocked_account = next(
        account
        for account in accounts
        if account["account_number"] == "101000"
    )

    available_account = next(
        account
        for account in accounts
        if account["account_number"] == "102000"
    )

    assert (
        blocked_account["liquidity_status"]
        == "Blocked"
    )

    assert (
        available_account["liquidity_status"]
        == "Available"
    )

def test_enrich_accounts_detects_blocked_cash_from_account_name():
    chart = ChartOfAccounts()

    chart.accounts = [
        {
            "account_number": "512400",
            "account_name": "Banks Account - Blocked",
            "financial_category": "Asset",
            "financial_subcategory": "Cash and Bank",
            "is_posting_account": True,
            "liquidity_status": None,
        },
    ]

    accounts = chart.enrich_accounts()

    blocked_account = accounts[0]

    assert (
        blocked_account["liquidity_status"]
        == "Blocked"
    )

def test_chart_import_preserves_account_balance(tmp_path):
    import pandas as pd

    file_path = tmp_path / "chart_with_balance.xlsx"

    source_data = pd.DataFrame(
        [
            {
                "No.": "512400",
                "Name": "Banks Account - Blocked",
                "Account Category": "Assets",
                "Account Type": "Posting",
                "Balance": 1311780.78,
            },
        ]
    )

    source_data.to_excel(
        file_path,
        index=False,
    )

    chart = ChartOfAccounts()

    chart.load_chart(
        str(file_path)
    )

    chart.detect_columns()

    accounts = chart.build_hierarchy()

    account = next(
        item
        for item in accounts
        if item["account_number"] == "512400"
    )

    assert account["balance"] == 1311780.78        
