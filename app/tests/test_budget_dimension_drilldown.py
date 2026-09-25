from app.services.budget_dimension_drilldown import (
    generate_budget_dimension_drilldown,
)


EXPENSE_ACCOUNTS = {
    "6000": {
        "account_number": "6000",
        "account_name": "Program Expenses",
        "financial_category": "Expense",
    }
}


def test_fund_drilldown_builds_program_view():
    budget_lines = [
        {
            "fund_code": "F1",
            "fund_name": "Fund One",
            "program_code": "P1",
            "program_name": "Program One",
            "current_budget": 1000,
        },
        {
            "fund_code": "F1",
            "fund_name": "Fund One",
            "program_code": "P2",
            "program_name": "Program Two",
            "current_budget": 2000,
        },
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P1",
            "debit_amount": 800,
            "credit_amount": 0,
        },
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P2",
            "debit_amount": 2500,
            "credit_amount": 0,
        },
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    fund_records = result["fund"]["records"]

    assert len(fund_records) == 1
    assert fund_records[0]["code"] == "F1"
    assert fund_records[0]["name"] == "Fund One"

    program_view = fund_records[0][
        "drilldown"
    ]["program"]

    assert program_view["dimension"] == "program"
    assert len(program_view["lines"]) == 2


def test_fund_program_drilldown_preserves_budget_actual_variance():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "program_name": "Program One",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P1",
            "debit_amount": 1200,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    line = result["fund"]["records"][0][
        "drilldown"
    ]["program"]["lines"][0]

    assert line["code"] == "P1"
    assert line["name"] == "Program One"
    assert line["budget"] == 1000
    assert line["actual"] == 1200
    assert line["variance"] == -200
    assert line["utilization_percentage"] == 120
    assert line["status"] == "Over Budget"


def test_donor_can_drill_down_to_fund():
    budget_lines = [
        {
            "donor_code": "D1",
            "fund_code": "F1",
            "fund_name": "Fund One",
            "current_budget": 1500,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "donor_code": "D1",
            "fund_code": "F1",
            "debit_amount": 1000,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    donor_record = result["donor"][
        "records"
    ][0]

    fund_view = donor_record[
        "drilldown"
    ]["fund"]

    assert fund_view["lines"][0]["code"] == "F1"
    assert fund_view["lines"][0]["name"] == "Fund One"
    assert fund_view["lines"][0]["budget"] == 1500
    assert fund_view["lines"][0]["actual"] == 1000


def test_program_can_drill_down_to_budget_line():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "budget_line_code": "BL1",
            "budget_line_name": "Travel",
            "current_budget": 500,
        },
        {
            "fund_code": "F1",
            "program_code": "P1",
            "budget_line_code": "BL2",
            "budget_line_name": "Training",
            "current_budget": 700,
        },
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P1",
            "budget_line_code": "BL1",
            "debit_amount": 600,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    program_record = result["program"][
        "records"
    ][0]

    budget_line_view = program_record[
        "drilldown"
    ]["budget_line"]

    codes = {
        line["code"]
        for line in budget_line_view["lines"]
    }

    assert codes == {"BL1", "BL2"}


def test_no_budget_child_record_is_preserved():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P2",
            "debit_amount": 300,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    program_lines = result["fund"][
        "records"
    ][0]["drilldown"]["program"]["lines"]

    p2 = next(
        line
        for line in program_lines
        if line["code"] == "P2"
    )

    assert p2["budget"] == 0
    assert p2["actual"] == 300
    assert p2["variance"] == -300
    assert p2["utilization_percentage"] is None
    assert p2["status"] == "No Budget"


def test_non_budget_consuming_transactions_are_excluded():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "current_budget": 1000,
        }
    ]

    accounts = {
        "1000": {
            "account_number": "1000",
            "account_name": "Cash",
            "financial_category": "Asset",
        }
    }

    transactions = [
        {
            "account_number": "1000",
            "fund_code": "F1",
            "program_code": "P1",
            "debit_amount": 900,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=accounts,
    )

    program_line = result["fund"][
        "records"
    ][0]["drilldown"]["program"]["lines"][0]

    assert program_line["budget"] == 1000
    assert program_line["actual"] == 0
    assert program_line["variance"] == 1000
    assert program_line["status"] == "Within Budget"


def test_transactions_outside_budget_funds_are_excluded():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F2",
            "program_code": "P2",
            "debit_amount": 500,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    fund_records = result["fund"][
        "records"
    ]

    assert len(fund_records) == 1
    assert fund_records[0]["code"] == "F1"

    program_lines = fund_records[0][
        "drilldown"
    ]["program"]["lines"]

    assert len(program_lines) == 1
    assert program_lines[0]["code"] == "P1"
    assert program_lines[0]["actual"] == 0


def test_child_summary_is_correct():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "current_budget": 1000,
        },
        {
            "fund_code": "F1",
            "program_code": "P2",
            "current_budget": 2000,
        },
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P1",
            "debit_amount": 1200,
            "credit_amount": 0,
        },
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P2",
            "debit_amount": 1500,
            "credit_amount": 0,
        },
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    summary = result["fund"][
        "records"
    ][0]["drilldown"]["program"]["summary"]

    assert summary["total_budget"] == 3000
    assert summary["total_actual"] == 2700
    assert summary["total_variance"] == 300
    assert summary["line_count"] == 2
    assert summary["over_budget_count"] == 1
    assert summary["within_budget_count"] == 1
    assert summary["no_budget_count"] == 0


def test_empty_inputs_return_empty_drilldown():
    result = generate_budget_dimension_drilldown(
        budget_lines=[],
        transactions=[],
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    assert result == {}

def test_category_can_drill_down_to_budget_line():
    budget_lines = [
        {
            "fund_code": "F1",
            "category_code": "CAT1",
            "category_name": "Programs",
            "budget_line_code": "BL1",
            "budget_line_name": "Travel",
            "current_budget": 500,
        },
        {
            "fund_code": "F1",
            "category_code": "CAT1",
            "category_name": "Programs",
            "budget_line_code": "BL2",
            "budget_line_name": "Training",
            "current_budget": 700,
        },
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "category_code": "CAT1",
            "budget_line_code": "BL1",
            "debit_amount": 600,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    category_record = result["category"]["records"][0]

    budget_line_view = category_record[
        "drilldown"
    ]["budget_line"]

    codes = {
        line["code"]
        for line in budget_line_view["lines"]
    }

    assert codes == {"BL1", "BL2"}


def test_donor_line_can_drill_down_to_budget_line():
    budget_lines = [
        {
            "fund_code": "F1",
            "donor_line_code": "DL1",
            "budget_line_code": "BL1",
            "budget_line_name": "Travel",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "donor_line_code": "DL1",
            "budget_line_code": "BL1",
            "debit_amount": 800,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    donor_line_record = result[
        "donor_line"
    ]["records"][0]

    budget_line_view = donor_line_record[
        "drilldown"
    ]["budget_line"]

    line = budget_line_view["lines"][0]

    assert line["code"] == "BL1"
    assert line["budget"] == 1000
    assert line["actual"] == 800
    assert line["variance"] == 200


def test_project_dimension_is_available_when_project_data_exists():
    budget_lines = [
        {
            "fund_code": "F1",
            "project_code": "PR1",
            "project_name": "Project One",
            "budget_line_code": "BL1",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "project_code": "PR1",
            "budget_line_code": "BL1",
            "debit_amount": 900,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    assert "project" in result

    project_record = result["project"]["records"][0]

    assert project_record["code"] == "PR1"
    assert project_record["name"] == "Project One"


def test_project_dimension_is_not_fabricated_when_project_data_missing():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P1",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P1",
            "debit_amount": 800,
            "credit_amount": 0,
        }
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    assert "project" not in result


def test_drilldown_ordering_is_deterministic():
    budget_lines = [
        {
            "fund_code": "F1",
            "program_code": "P3",
            "current_budget": 300,
        },
        {
            "fund_code": "F1",
            "program_code": "P1",
            "current_budget": 100,
        },
        {
            "fund_code": "F1",
            "program_code": "P2",
            "current_budget": 200,
        },
    ]

    first_result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=[],
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    second_result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=[],
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    first_codes = [
        line["code"]
        for line in first_result["fund"][
            "records"
        ][0]["drilldown"]["program"]["lines"]
    ]

    second_codes = [
        line["code"]
        for line in second_result["fund"][
            "records"
        ][0]["drilldown"]["program"]["lines"]
    ]

    assert first_codes == second_codes  

def test_missing_child_dimension_actual_is_preserved_as_unassigned():
    budget_lines = [
        {
            "fund_code": "F1",
            "fund_name": "Fund One",
            "program_code": "P1",
            "program_name": "Program One",
            "current_budget": 1000,
        }
    ]

    transactions = [
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": "P1",
            "debit_amount": 800,
            "credit_amount": 0,
        },
        {
            "account_number": "6000",
            "fund_code": "F1",
            "program_code": None,
            "debit_amount": 300,
            "credit_amount": 0,
        },
    ]

    result = generate_budget_dimension_drilldown(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=EXPENSE_ACCOUNTS,
    )

    program_view = result["fund"][
        "records"
    ][0]["drilldown"]["program"]

    assert program_view["summary"]["total_budget"] == 1000
    assert program_view["summary"]["total_actual"] == 1100
    assert program_view["summary"]["total_variance"] == -100

    unassigned = next(
        line
        for line in program_view["lines"]
        if line["code"] == "__UNASSIGNED__"
    )

    assert unassigned["name"] == "Unassigned"
    assert unassigned["budget"] == 0
    assert unassigned["actual"] == 300
    assert unassigned["variance"] == -300
    assert unassigned["utilization_percentage"] is None
    assert unassigned["status"] == "No Budget"      