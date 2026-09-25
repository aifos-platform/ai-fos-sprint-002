from app.organization import Organization


def _coverage_line(
    coverage_type,
    amount,
    fund_code=None,
    budget_line_code=None,
):
    return {
        "coverage_type": coverage_type,
        "fund_code": fund_code,
        "budget_line_code": budget_line_code,
        "amount": amount,
        "requires_review": False,
        "review_reasons": [],
    }


def test_load_core_cost_coverage_stores_separate_records():
    organization = Organization()

    lines = [
        _coverage_line(
            "direct_grant_coverage",
            25000.0,
            fund_code="GRANT-001",
            budget_line_code="SAL-001",
        ),
        _coverage_line(
            "available_indirect_recovery",
            10000.0,
            fund_code="GRANT-001",
        ),
    ]

    organization.load_core_cost_coverage(lines)

    assert len(
        organization.core_cost_coverage_inputs
    ) == 2

    assert (
        organization.core_cost_coverage_inputs[0][
            "coverage_type"
        ]
        == "direct_grant_coverage"
    )

    assert organization.funding_gap is None


def test_generate_core_cost_coverage_analysis():
    organization = Organization()

    organization.needed_budget.load_budget(
        [
            {
                "program_code": "PROGRAM-001",
                "category_code": "PERSONNEL",
                "budget_line_code": "SAL-001",
                "budget_line_name": "Salary",
                "employee_responsible": "Employee A",
                "fiscal_year": 2026,
                "needed_budget": 100000.0,
                "requires_review": False,
                "review_reasons": [],
            }
        ]
    )

    organization.load_core_cost_coverage(
        [
            _coverage_line(
                "direct_grant_coverage",
                40000.0,
                fund_code="GRANT-001",
                budget_line_code="SAL-001",
            ),
            _coverage_line(
                "indirect_recovery_allocation",
                15000.0,
                fund_code="GRANT-001",
                budget_line_code="SAL-001",
            ),
            _coverage_line(
                "unrestricted_core_funding",
                10000.0,
                fund_code="CORE-001",
                budget_line_code="SAL-001",
            ),
            _coverage_line(
                "available_indirect_recovery",
                20000.0,
                fund_code="GRANT-001",
            ),
            _coverage_line(
                "used_indirect_recovery",
                12000.0,
                budget_line_code="SAL-001",
            ),
        ]
    )

    organization.generate_core_cost_coverage_analysis()

    result = organization.core_cost_coverage

    assert (
        result["summary"]["needed_core_cost"]
        == 100000.0
    )

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 35000.0
    )

    assert (
        result["summary"]["available_indirect_recovery"]
        == 20000.0
    )

    assert (
        result["summary"]["used_indirect_recovery"]
        == 12000.0
    )


def test_unknown_core_cost_coverage_type_is_not_applied():
    organization = Organization()

    organization.needed_budget.load_budget(
        [
            {
                "budget_line_code": "SAL-001",
                "budget_line_name": "Salary",
                "fiscal_year": 2026,
                "needed_budget": 100000.0,
            }
        ]
    )

    organization.load_core_cost_coverage(
        [
            _coverage_line(
                "unknown_type",
                50000.0,
                fund_code="GRANT-001",
                budget_line_code="SAL-001",
            )
        ]
    )

    organization.generate_core_cost_coverage_analysis()

    result = organization.core_cost_coverage

    assert (
        result["summary"]["remaining_core_cost_gap"]
        == 100000.0
    )
