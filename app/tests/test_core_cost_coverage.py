from app.services.core_cost_coverage import (
    generate_core_cost_coverage,
)


def test_core_cost_coverage_calculates_remaining_gap():
    needed_core_costs = [
        {
            "program_code": "CORE",
            "category_code": "PERSONNEL",
            "budget_line_code": "SAL-001",
            "budget_line_name": "Finance Manager",
            "employee_responsible": "Employee A",
            "fiscal_year": 2027,
            "needed_budget": 100000.0,
        }
    ]

    direct_grant_coverage = [
        {
            "budget_line_code": "SAL-001",
            "amount": 40000.0,
        }
    ]

    indirect_recovery_allocations = [
        {
            "budget_line_code": "SAL-001",
            "amount": 15000.0,
        }
    ]

    unrestricted_core_funding = [
        {
            "budget_line_code": "SAL-001",
            "amount": 10000.0,
        }
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=direct_grant_coverage,
        indirect_recovery_allocations=(
            indirect_recovery_allocations
        ),
        unrestricted_core_funding=(
            unrestricted_core_funding
        ),
    )

    assert result["status"] == "available"

    assert result["summary"]["needed_core_cost"] == 100000.0
    assert result["summary"]["direct_grant_coverage"] == 40000.0

    assert (
        result["summary"]["allocated_indirect_recovery"]
        == 15000.0
    )

    assert (
        result["summary"]["unrestricted_core_funding"]
        == 10000.0
    )

    assert result["summary"]["remaining_core_cost_gap"] == 35000.0

def test_available_indirect_recovery_is_not_automatically_allocated():
    needed_core_costs = [
        {
            "budget_line_code": "SAL-001",
            "needed_budget": 100000.0,
        }
    ]

    direct_grant_coverage = [
        {
            "budget_line_code": "SAL-001",
            "amount": 40000.0,
        }
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=direct_grant_coverage,
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
    )

    assert result["summary"]["needed_core_cost"] == 100000.0
    assert result["summary"]["direct_grant_coverage"] == 40000.0

    assert (
        result["summary"]["allocated_indirect_recovery"]
        == 0.0
    )

    assert result["summary"]["remaining_core_cost_gap"] == 60000.0 

def test_core_cost_gap_never_becomes_negative():
    needed_core_costs = [
        {
            "budget_line_code": "SAL-001",
            "needed_budget": 100000.0,
        }
    ]

    direct_grant_coverage = [
        {
            "budget_line_code": "SAL-001",
            "amount": 80000.0,
        }
    ]

    indirect_recovery_allocations = [
        {
            "budget_line_code": "SAL-001",
            "amount": 30000.0,
        }
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=direct_grant_coverage,
        indirect_recovery_allocations=(
            indirect_recovery_allocations
        ),
        unrestricted_core_funding=[],
    )

    assert result["summary"]["needed_core_cost"] == 100000.0

    assert (
        result["summary"]["direct_grant_coverage"]
        == 80000.0
    )

    assert (
        result["summary"]["allocated_indirect_recovery"]
        == 30000.0
    )

    assert result["summary"]["remaining_core_cost_gap"] == 0.0 

def test_core_cost_coverage_returns_line_level_results():
    needed_core_costs = [
        {
            "program_code": "CORE",
            "category_code": "PERSONNEL",
            "budget_line_code": "SAL-001",
            "budget_line_name": "Finance Manager",
            "employee_responsible": "Employee A",
            "fiscal_year": 2027,
            "needed_budget": 100000.0,
        },
        {
            "program_code": "CORE",
            "category_code": "PERSONNEL",
            "budget_line_code": "SAL-002",
            "budget_line_name": "Accountant",
            "employee_responsible": "Employee B",
            "fiscal_year": 2027,
            "needed_budget": 60000.0,
        },
    ]

    direct_grant_coverage = [
        {
            "budget_line_code": "SAL-001",
            "amount": 40000.0,
        },
        {
            "budget_line_code": "SAL-002",
            "amount": 30000.0,
        },
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=direct_grant_coverage,
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
    )

    lines = result["lines"]

    assert len(lines) == 2

    assert lines[0]["budget_line_code"] == "SAL-001"
    assert lines[0]["needed_core_cost"] == 100000.0
    assert lines[0]["direct_grant_coverage"] == 40000.0
    assert lines[0]["remaining_core_cost_gap"] == 60000.0

    assert lines[1]["budget_line_code"] == "SAL-002"
    assert lines[1]["needed_core_cost"] == 60000.0
    assert lines[1]["direct_grant_coverage"] == 30000.0
    assert lines[1]["remaining_core_cost_gap"] == 30000.0 

def test_coverage_is_not_applied_to_another_budget_line():
    needed_core_costs = [
        {
            "budget_line_code": "SAL-001",
            "needed_budget": 100000.0,
        },
        {
            "budget_line_code": "SAL-002",
            "needed_budget": 80000.0,
        },
    ]

    direct_grant_coverage = [
        {
            "budget_line_code": "SAL-001",
            "amount": 70000.0,
        }
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=direct_grant_coverage,
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
    )

    lines = result["lines"]

    assert lines[0]["direct_grant_coverage"] == 70000.0
    assert lines[0]["remaining_core_cost_gap"] == 30000.0

    assert lines[1]["direct_grant_coverage"] == 0.0
    assert lines[1]["remaining_core_cost_gap"] == 80000.0

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 110000.0
    )

def test_available_indirect_recovery_is_tracked_separately():
    needed_core_costs = [
        {
            "budget_line_code": "SAL-001",
            "needed_budget": 100000.0,
        }
    ]

    available_indirect_recovery = [
        {
            "fund_code": "GRANT-001",
            "amount": 30000.0,
        }
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=[],
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
        available_indirect_recovery=(
            available_indirect_recovery
        ),
    )

    assert (
        result["summary"]["available_indirect_recovery"]
        == 30000.0
    )

    assert (
        result["summary"]["allocated_indirect_recovery"]
        == 0.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 100000.0
    )     
def test_used_indirect_recovery_is_tracked_separately():
    needed_core_costs = [
        {
            "budget_line_code": "SAL-001",
            "needed_budget": 100000.0,
        }
    ]

    indirect_recovery_allocations = [
        {
            "budget_line_code": "SAL-001",
            "amount": 30000.0,
        }
    ]

    used_indirect_recovery = [
        {
            "budget_line_code": "SAL-001",
            "amount": 12000.0,
        }
    ]

    result = generate_core_cost_coverage(
        needed_core_costs=needed_core_costs,
        direct_grant_coverage=[],
        indirect_recovery_allocations=(
            indirect_recovery_allocations
        ),
        unrestricted_core_funding=[],
        available_indirect_recovery=[],
        used_indirect_recovery=used_indirect_recovery,
    )

    assert (
        result["summary"]["allocated_indirect_recovery"]
        == 30000.0
    )

    assert (
        result["summary"]["used_indirect_recovery"]
        == 12000.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 70000.0
    ) 
def test_used_indirect_recovery_above_allocation_is_flagged():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[],
        indirect_recovery_allocations=[
            {
                "budget_line_code": "SAL-001",
                "amount": 20000.0,
            }
        ],
        unrestricted_core_funding=[],
        available_indirect_recovery=[
            {
                "fund_code": "GRANT-001",
                "amount": 40000.0,
            }
        ],
        used_indirect_recovery=[
            {
                "budget_line_code": "SAL-001",
                "amount": 30000.0,
            }
        ],
    )

    assert (
        result["controls"][
            "used_indirect_recovery_exceeds_allocation"
        ]
        is True
    )

    assert (
        result["controls"][
            "used_indirect_recovery_over_allocation_amount"
        ]
        == 10000.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 80000.0
    )
def test_allocated_indirect_recovery_above_available_is_flagged():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[],
        indirect_recovery_allocations=[
            {
                "budget_line_code": "SAL-001",
                "amount": 40000.0,
            }
        ],
        unrestricted_core_funding=[],
        available_indirect_recovery=[
            {
                "fund_code": "GRANT-001",
                "amount": 30000.0,
            }
        ],
        used_indirect_recovery=[],
    )

    assert (
        result["controls"][
            "allocated_indirect_recovery_exceeds_available"
        ]
        is True
    )

    assert (
        result["controls"][
            "allocated_indirect_recovery_over_available_amount"
        ]
        == 10000.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 60000.0
    )
def test_valid_indirect_recovery_lifecycle_has_no_control_flags():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[],
        indirect_recovery_allocations=[
            {
                "budget_line_code": "SAL-001",
                "amount": 30000.0,
            }
        ],
        unrestricted_core_funding=[],
        available_indirect_recovery=[
            {
                "fund_code": "GRANT-001",
                "amount": 50000.0,
            }
        ],
        used_indirect_recovery=[
            {
                "budget_line_code": "SAL-001",
                "amount": 20000.0,
            }
        ],
    )

    assert (
        result["controls"][
            "allocated_indirect_recovery_exceeds_available"
        ]
        is False
    )

    assert (
        result["controls"][
            "allocated_indirect_recovery_over_available_amount"
        ]
        == 0.0
    )

    assert (
        result["controls"][
            "used_indirect_recovery_exceeds_allocation"
        ]
        is False
    )

    assert (
        result["controls"][
            "used_indirect_recovery_over_allocation_amount"
        ]
        == 0.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 70000.0
    )
def test_multiple_direct_grant_coverages_are_aggregated():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 25000.0,
            },
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-001",
                "amount": 15000.0,
            },
        ],
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
        available_indirect_recovery=[],
        used_indirect_recovery=[],
    )

    assert (
        result["lines"][0]["direct_grant_coverage"]
        == 40000.0
    )

    assert (
        result["summary"]["direct_grant_coverage"]
        == 40000.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 60000.0
    )
def test_direct_grant_coverage_preserves_source_detail():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 25000.0,
            },
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-001",
                "amount": 15000.0,
            },
        ],
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
        available_indirect_recovery=[],
        used_indirect_recovery=[],
    )

    sources = result["lines"][0][
        "direct_grant_coverage_sources"
    ]

    assert len(sources) == 2

    assert sources[0]["fund_code"] == "GRANT-001"
    assert sources[0]["amount"] == 25000.0

    assert sources[1]["fund_code"] == "GRANT-002"
    assert sources[1]["amount"] == 15000.0      
def test_indirect_recovery_allocation_preserves_source_detail():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[],
        indirect_recovery_allocations=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 20000.0,
            },
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-001",
                "amount": 10000.0,
            },
        ],
        unrestricted_core_funding=[],
        available_indirect_recovery=[],
        used_indirect_recovery=[],
    )

    sources = result["lines"][0][
        "indirect_recovery_allocation_sources"
    ]

    assert len(sources) == 2

    assert sources[0]["fund_code"] == "GRANT-001"
    assert sources[0]["amount"] == 20000.0

    assert sources[1]["fund_code"] == "GRANT-002"
    assert sources[1]["amount"] == 10000.0

    assert (
        result["lines"][0]["allocated_indirect_recovery"]
        == 30000.0
    ) 
def test_unrestricted_core_funding_preserves_source_detail():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[],
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[
            {
                "fund_code": "CORE-001",
                "budget_line_code": "SAL-001",
                "amount": 10000.0,
            },
            {
                "fund_code": "CORE-002",
                "budget_line_code": "SAL-001",
                "amount": 5000.0,
            },
        ],
        available_indirect_recovery=[],
        used_indirect_recovery=[],
    )

    sources = result["lines"][0][
        "unrestricted_core_funding_sources"
    ]

    assert len(sources) == 2

    assert sources[0]["fund_code"] == "CORE-001"
    assert sources[0]["amount"] == 10000.0

    assert sources[1]["fund_code"] == "CORE-002"
    assert sources[1]["amount"] == 5000.0

    assert (
        result["lines"][0]["unrestricted_core_funding"]
        == 15000.0
    )

    assert (
        result["lines"][0]["remaining_core_cost_gap"]
        == 85000.0
    )
def test_total_core_cost_coverage_exceeding_need_is_flagged():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 80000.0,
            }
        ],
        indirect_recovery_allocations=[
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-001",
                "amount": 30000.0,
            }
        ],
        unrestricted_core_funding=[],
        available_indirect_recovery=[
            {
                "fund_code": "GRANT-002",
                "amount": 30000.0,
            }
        ],
        used_indirect_recovery=[],
    )

    line = result["lines"][0]

    assert line["remaining_core_cost_gap"] == 0.0

    assert (
        result["controls"][
            "total_core_cost_coverage_exceeds_need"
        ]
        is True
    )

    assert (
        result["controls"][
            "total_core_cost_coverage_over_need_amount"
        ]
        == 10000.0
    )
def test_overcoverage_on_one_line_does_not_offset_gap_on_another():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            },
            {
                "budget_line_code": "SAL-002",
                "needed_budget": 100000.0,
            },
        ],
        direct_grant_coverage=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 120000.0,
            },
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-002",
                "amount": 50000.0,
            },
        ],
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
        available_indirect_recovery=[],
        used_indirect_recovery=[],
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 50000.0
    )

    assert (
        result["controls"][
            "total_core_cost_coverage_exceeds_need"
        ]
        is True
    )

    assert (
        result["controls"][
            "total_core_cost_coverage_over_need_amount"
        ]
        == 20000.0
    )
def test_core_cost_coverage_percentage_is_calculated():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 40000.0,
            }
        ],
        indirect_recovery_allocations=[
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-001",
                "amount": 15000.0,
            }
        ],
        unrestricted_core_funding=[
            {
                "fund_code": "CORE-001",
                "budget_line_code": "SAL-001",
                "amount": 10000.0,
            }
        ],
        available_indirect_recovery=[
            {
                "fund_code": "GRANT-002",
                "amount": 15000.0,
            }
        ],
        used_indirect_recovery=[],
    )

    assert (
        result["summary"]["core_cost_coverage_percentage"]
        == 65.0
    )
def test_core_cost_coverage_percentage_is_capped_at_100():
    result = generate_core_cost_coverage(
        needed_core_costs=[
            {
                "budget_line_code": "SAL-001",
                "needed_budget": 100000.0,
            }
        ],
        direct_grant_coverage=[
            {
                "fund_code": "GRANT-001",
                "budget_line_code": "SAL-001",
                "amount": 80000.0,
            }
        ],
        indirect_recovery_allocations=[
            {
                "fund_code": "GRANT-002",
                "budget_line_code": "SAL-001",
                "amount": 30000.0,
            }
        ],
        unrestricted_core_funding=[],
        available_indirect_recovery=[
            {
                "fund_code": "GRANT-002",
                "amount": 30000.0,
            }
        ],
        used_indirect_recovery=[],
    )

    assert (
        result["summary"]["core_cost_coverage_percentage"]
        == 100.0
    )

    assert (
        result["controls"][
            "total_core_cost_coverage_exceeds_need"
        ]
        is True
    )

    assert (
        result["controls"][
            "total_core_cost_coverage_over_need_amount"
        ]
        == 10000.0
    )                   
def test_core_cost_coverage_percentage_is_zero_when_no_need():
    result = generate_core_cost_coverage(
        needed_core_costs=[],
        direct_grant_coverage=[],
        indirect_recovery_allocations=[],
        unrestricted_core_funding=[],
        available_indirect_recovery=[],
        used_indirect_recovery=[],
    )

    assert result["summary"]["needed_core_cost"] == 0.0

    assert (
        result["summary"]["core_cost_coverage_percentage"]
        == 0.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 0.0
    )