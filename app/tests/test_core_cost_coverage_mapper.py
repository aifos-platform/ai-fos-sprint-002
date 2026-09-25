from app.services.core_cost_coverage_mapper import (
    map_core_cost_coverage_columns,
)


def test_maps_standard_core_cost_coverage_headers():
    headers = [
        "Coverage Type",
        "Fund Code",
        "Budget Line Code",
        "Amount",
    ]

    mapping = map_core_cost_coverage_columns(
        headers
    )

    assert mapping == {
        "coverage_type": "Coverage Type",
        "fund_code": "Fund Code",
        "budget_line_code": "Budget Line Code",
        "amount": "Amount",
    }

def test_maps_core_cost_coverage_header_aliases():
    headers = [
        "Core Cost Coverage Type",
        "Grant Code",
        "Budget Line Code",
        "Coverage Amount",
    ]

    mapping = map_core_cost_coverage_columns(
        headers
    )

    assert mapping == {
        "coverage_type": "Core Cost Coverage Type",
        "fund_code": "Grant Code",
        "budget_line_code": "Budget Line Code",
        "amount": "Coverage Amount",
    } 

def test_ignores_unrelated_core_cost_coverage_headers():
    headers = [
        "Coverage Type",
        "Fund Code",
        "Budget Line Code",
        "Amount",
        "Donor Name",
        "Description",
        "Notes",
        "Employee Name",
    ]

    mapping = map_core_cost_coverage_columns(
        headers
    )

    assert mapping == {
        "coverage_type": "Coverage Type",
        "fund_code": "Fund Code",
        "budget_line_code": "Budget Line Code",
        "amount": "Amount",
    }       