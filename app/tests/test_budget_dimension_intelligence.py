from app.services.budget_dimension_intelligence import (
    generate_budget_dimension_intelligence,
)


def test_skips_empty_dimensions():
    dashboard = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "FUND-1",
                    "fund_name": "Fund One",
                    "budget": 1000,
                    "actual": 900,
                    "variance": 100,
                    "utilization_percentage": 90,
                    "status": "Within Budget",
                }
            ]
        },
        "by_project": {
            "lines": [],
        },
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    assert "fund" in result
    assert "project" not in result


def test_counts_over_budget_records():
    dashboard = {
        "by_program": {
            "lines": [
                {
                    "program_code": "P1",
                    "program_name": "Program One",
                    "budget": 1000,
                    "actual": 1200,
                    "variance": -200,
                    "utilization_percentage": 120,
                    "status": "Over Budget",
                },
                {
                    "program_code": "P2",
                    "program_name": "Program Two",
                    "budget": 1000,
                    "actual": 700,
                    "variance": 300,
                    "utilization_percentage": 70,
                    "status": "Within Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    program = result["program"]

    assert program["record_count"] == 2
    assert program["over_budget_count"] == 1


def test_counts_no_budget_records_with_actual_spending():
    dashboard = {
        "by_budget_line": {
            "lines": [
                {
                    "budget_line_code": "BL1",
                    "budget_line_name": "Travel",
                    "budget": 0,
                    "actual": 500,
                    "variance": -500,
                    "utilization_percentage": None,
                    "status": "No Budget",
                },
                {
                    "budget_line_code": "BL2",
                    "budget_line_name": "Training",
                    "budget": 0,
                    "actual": 0,
                    "variance": 0,
                    "utilization_percentage": None,
                    "status": "No Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    budget_line = result["budget_line"]

    assert budget_line["no_budget_count"] == 1
    assert budget_line["no_budget_actual"] == 500


def test_identifies_largest_unfavorable_variance():
    dashboard = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "F1",
                    "fund_name": "Fund One",
                    "budget": 1000,
                    "actual": 1300,
                    "variance": -300,
                    "utilization_percentage": 130,
                    "status": "Over Budget",
                },
                {
                    "fund_code": "F2",
                    "fund_name": "Fund Two",
                    "budget": 2000,
                    "actual": 2600,
                    "variance": -600,
                    "utilization_percentage": 130,
                    "status": "Over Budget",
                },
                {
                    "fund_code": "F3",
                    "fund_name": "Fund Three",
                    "budget": 1000,
                    "actual": 500,
                    "variance": 500,
                    "utilization_percentage": 50,
                    "status": "Within Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    item = result["fund"][
        "largest_unfavorable_variance"
    ]

    assert item["code"] == "F2"
    assert item["name"] == "Fund Two"
    assert item["variance"] == -600


def test_identifies_highest_utilization_only_with_positive_budget():
    dashboard = {
        "by_donor": {
            "lines": [
                {
                    "donor_code": "D1",
                    "donor_name": "Donor One",
                    "budget": 100,
                    "actual": 500,
                    "variance": -400,
                    "utilization_percentage": 500,
                    "status": "Over Budget",
                },
                {
                    "donor_code": "D2",
                    "donor_name": "Donor Two",
                    "budget": 0,
                    "actual": 1000,
                    "variance": -1000,
                    "utilization_percentage": None,
                    "status": "No Budget",
                },
                {
                    "donor_code": "D3",
                    "donor_name": "Donor Three",
                    "budget": 1000,
                    "actual": 900,
                    "variance": 100,
                    "utilization_percentage": 90,
                    "status": "Within Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    item = result["donor"]["highest_utilization"]

    assert item["code"] == "D1"
    assert item["utilization_percentage"] == 500


def test_identifies_lowest_utilization_only_with_positive_budget():
    dashboard = {
        "by_category": {
            "lines": [
                {
                    "category_code": "C1",
                    "category_name": "Personnel",
                    "budget": 1000,
                    "actual": 900,
                    "variance": 100,
                    "utilization_percentage": 90,
                    "status": "Within Budget",
                },
                {
                    "category_code": "C2",
                    "category_name": "Programs",
                    "budget": 2000,
                    "actual": 200,
                    "variance": 1800,
                    "utilization_percentage": 10,
                    "status": "Within Budget",
                },
                {
                    "category_code": "C3",
                    "category_name": "No Budget",
                    "budget": 0,
                    "actual": 400,
                    "variance": -400,
                    "utilization_percentage": None,
                    "status": "No Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    item = result["category"]["lowest_utilization"]

    assert item["code"] == "C2"
    assert item["utilization_percentage"] == 10


def test_priority_items_include_over_budget_and_no_budget_records():
    dashboard = {
        "by_program": {
            "lines": [
                {
                    "program_code": "P1",
                    "program_name": "Overspent Program",
                    "budget": 1000,
                    "actual": 1500,
                    "variance": -500,
                    "utilization_percentage": 150,
                    "status": "Over Budget",
                },
                {
                    "program_code": "P2",
                    "program_name": "Unbudgeted Program",
                    "budget": 0,
                    "actual": 800,
                    "variance": -800,
                    "utilization_percentage": None,
                    "status": "No Budget",
                },
                {
                    "program_code": "P3",
                    "program_name": "Healthy Program",
                    "budget": 1000,
                    "actual": 700,
                    "variance": 300,
                    "utilization_percentage": 70,
                    "status": "Within Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    priority_items = result["program"][
        "priority_items"
    ]

    codes = {
        item["code"]
        for item in priority_items
    }

    assert "P1" in codes
    assert "P2" in codes
    assert "P3" not in codes


def test_priority_items_are_limited_to_five():
    lines = []

    for index in range(10):
        lines.append(
            {
                "budget_line_code": f"BL{index}",
                "budget_line_name": f"Line {index}",
                "budget": 100,
                "actual": 200 + index,
                "variance": -(100 + index),
                "utilization_percentage": 200 + index,
                "status": "Over Budget",
            }
        )

    dashboard = {
        "by_budget_line": {
            "lines": lines,
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    assert (
        len(
            result["budget_line"][
                "priority_items"
            ]
        )
        == 5
    )


def test_totals_are_derived_from_dimension_lines():
    dashboard = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "F1",
                    "fund_name": "Fund One",
                    "budget": 1000,
                    "actual": 800,
                    "variance": 200,
                    "utilization_percentage": 80,
                    "status": "Within Budget",
                },
                {
                    "fund_code": "F2",
                    "fund_name": "Fund Two",
                    "budget": 2000,
                    "actual": 2500,
                    "variance": -500,
                    "utilization_percentage": 125,
                    "status": "Over Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    fund = result["fund"]

    assert fund["total_budget"] == 3000
    assert fund["total_actual"] == 3300


def test_empty_dashboard_returns_empty_intelligence():
    result = generate_budget_dimension_intelligence(
        {}
    )

    assert result == {}

def test_priority_item_preserves_validated_financial_fields():
    dashboard = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "F1",
                    "fund_name": "Fund One",
                    "budget": 1000,
                    "actual": 1400,
                    "variance": -400,
                    "utilization_percentage": 140,
                    "status": "Over Budget",
                }
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    item = result["fund"]["priority_items"][0]

    assert item["code"] == "F1"
    assert item["name"] == "Fund One"
    assert item["budget"] == 1000
    assert item["actual"] == 1400
    assert item["variance"] == -400
    assert item["utilization_percentage"] == 140
    assert item["status"] == "Over Budget"


def test_no_priority_items_when_dimension_has_no_exceptions():
    dashboard = {
        "by_program": {
            "lines": [
                {
                    "program_code": "P1",
                    "program_name": "Program One",
                    "budget": 1000,
                    "actual": 700,
                    "variance": 300,
                    "utilization_percentage": 70,
                    "status": "Within Budget",
                },
                {
                    "program_code": "P2",
                    "program_name": "Program Two",
                    "budget": 2000,
                    "actual": 1000,
                    "variance": 1000,
                    "utilization_percentage": 50,
                    "status": "Within Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    assert (
        result["program"]["priority_items"]
        == []
    )


def test_priority_items_remain_independent_by_dimension():
    dashboard = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "F1",
                    "fund_name": "Fund One",
                    "budget": 100,
                    "actual": 200,
                    "variance": -100,
                    "utilization_percentage": 200,
                    "status": "Over Budget",
                }
            ]
        },
        "by_program": {
            "lines": [
                {
                    "program_code": "P1",
                    "program_name": "Program One",
                    "budget": 500,
                    "actual": 900,
                    "variance": -400,
                    "utilization_percentage": 180,
                    "status": "Over Budget",
                }
            ]
        },
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    fund_items = result["fund"][
        "priority_items"
    ]

    program_items = result["program"][
        "priority_items"
    ]

    assert len(fund_items) == 1
    assert fund_items[0]["code"] == "F1"

    assert len(program_items) == 1
    assert program_items[0]["code"] == "P1"


def test_no_budget_priority_is_ranked_before_over_budget():
    dashboard = {
        "by_budget_line": {
            "lines": [
                {
                    "budget_line_code": "OVER",
                    "budget_line_name": "Over Budget Line",
                    "budget": 1000,
                    "actual": 5000,
                    "variance": -4000,
                    "utilization_percentage": 500,
                    "status": "Over Budget",
                },
                {
                    "budget_line_code": "NONE",
                    "budget_line_name": "No Budget Line",
                    "budget": 0,
                    "actual": 100,
                    "variance": -100,
                    "utilization_percentage": None,
                    "status": "No Budget",
                },
            ]
        }
    }

    result = generate_budget_dimension_intelligence(
        dashboard
    )

    items = result["budget_line"][
        "priority_items"
    ]

    assert items[0]["code"] == "NONE"
    assert items[0]["status"] == "No Budget"

    assert items[1]["code"] == "OVER"
    assert items[1]["status"] == "Over Budget"


def test_priority_item_order_is_deterministic():
    dashboard = {
        "by_donor": {
            "lines": [
                {
                    "donor_code": "D1",
                    "donor_name": "Donor One",
                    "budget": 1000,
                    "actual": 1500,
                    "variance": -500,
                    "utilization_percentage": 150,
                    "status": "Over Budget",
                },
                {
                    "donor_code": "D2",
                    "donor_name": "Donor Two",
                    "budget": 1000,
                    "actual": 2500,
                    "variance": -1500,
                    "utilization_percentage": 250,
                    "status": "Over Budget",
                },
                {
                    "donor_code": "D3",
                    "donor_name": "Donor Three",
                    "budget": 1000,
                    "actual": 2000,
                    "variance": -1000,
                    "utilization_percentage": 200,
                    "status": "Over Budget",
                },
            ]
        }
    }

    first_result = (
        generate_budget_dimension_intelligence(
            dashboard
        )
    )

    second_result = (
        generate_budget_dimension_intelligence(
            dashboard
        )
    )

    first_codes = [
        item["code"]
        for item in first_result["donor"][
            "priority_items"
        ]
    ]

    second_codes = [
        item["code"]
        for item in second_result["donor"][
            "priority_items"
        ]
    ]

    assert first_codes == [
        "D2",
        "D3",
        "D1",
    ]

    assert second_codes == first_codes    