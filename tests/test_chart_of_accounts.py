from app.services.chart_of_accounts import ChartOfAccounts


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