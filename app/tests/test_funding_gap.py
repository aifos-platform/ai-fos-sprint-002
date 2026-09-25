from app.services.funding_gap import (
    _get_funding_period_status,
    generate_funding_gap,
)


def test_grant_period_status_eligible():
    grant_periods = {
        "G1": {
            "start_date": "2026-07-01",
            "end_date": "2027-06-30",
        }
    }

    result = _get_funding_period_status(
        ledger_entry={
            "fund_code": "G1",
        },
        fiscal_year=2026,
        grant_periods=grant_periods,
    )

    assert result == "eligible"


def test_grant_period_status_ineligible():
    grant_periods = {
        "G2": {
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
        }
    }

    result = _get_funding_period_status(
        ledger_entry={
            "fund_code": "G2",
        },
        fiscal_year=2026,
        grant_periods=grant_periods,
    )

    assert result == "ineligible"


def test_grant_period_status_unknown_when_dates_missing():
    grant_periods = {
        "G3": {
            "start_date": None,
            "end_date": None,
        }
    }

    result = _get_funding_period_status(
        ledger_entry={
            "fund_code": "G3",
        },
        fiscal_year=2026,
        grant_periods=grant_periods,
    )

    assert result == "unknown"


def test_period_ineligible_funding_is_not_applied():
    needed_budget_vs_actual = {
        "detailed": {
            "lines": [
                {
                    "code": "BL1",
                    "budget_line_code": "BL1",
                    "fiscal_year": 2026,
                    "needed_budget": 1000.0,
                    "actual": 0.0,
                    "remaining_requirement": 1000.0,
                }
            ]
        }
    }

    available_budget_lines = [
        {
            "fund_code": "TEST-OLD",
            "budget_line_code": "BL1",
            "remaining_secured_budget": 600.0,
        }
    ]

    budget_vs_actual = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "TEST-OLD",
                    "budget": 600.0,
                    "actual": 0.0,
                }
            ]
        }
    }

    grant_periods = {
        "TEST-OLD": {
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
        }
    }

    result = generate_funding_gap(
        needed_budget_vs_actual=needed_budget_vs_actual,
        available_budget_lines=available_budget_lines,
        budget_vs_actual=budget_vs_actual,
        grant_periods=grant_periods,
    )

    line = result["lines"][0]

    assert line["eligible_secured_funding"] == 0.0
    assert line["applied_secured_funding"] == 0.0
    assert line["period_ineligible_funding"] == 600.0
    assert line["funding_gap"] == 1000.0
    assert line["status"] == "No Eligible Secured Funding"

def test_period_unknown_funding_is_not_applied():
    needed_budget_vs_actual = {
        "lines": [
            {
                "fiscal_year": 2026,
                "budget_line_code": "UNPL008",
                "program_code": "",
                "category_code": "",
                "project_code": "",
                "needed_budget": 1000.0,
                "actual": 0.0,
                "remaining_needed_budget": 1000.0,
            }
        ]
    }

    available_budget_lines = [
        {
            "fund_code": "TEST-UNKNOWN",
            "budget_line_code": "UNPL008",
            "program_code": "",
            "category_code": "",
            "project_code": "",
            "remaining_secured_budget": 600.0,
        }
    ]

    budget_vs_actual = {
        "lines": [
            {
                "fund_code": "TEST-UNKNOWN",
                "budget_line_code": "UNPL008",
                "program_code": "",
                "category_code": "",
                "project_code": "",
                "budget": 600.0,
                "actual": 0.0,
                "remaining_budget": 600.0,
            }
        ]
    }

    grant_periods = {
        "TEST-UNKNOWN": {
            "start_date": None,
            "end_date": None,
        }
    }

    result = generate_funding_gap(
        needed_budget_vs_actual=needed_budget_vs_actual,
        available_budget_lines=available_budget_lines,
        budget_vs_actual=budget_vs_actual,
        grant_periods=grant_periods,
    )

    line = result["lines"][0]

    assert line["eligible_secured_funding"] == 0.0
    assert line["applied_secured_funding"] == 0.0
    assert line["period_unknown_funding"] == 600.0
    assert line["funding_gap"] == 1000.0
    assert line["status"] == "No Eligible Secured Funding"    

def test_summary_includes_period_ineligible_exposure():
    needed_budget_vs_actual = {
        "detailed": {
            "lines": [
                {
                    "code": "BL1",
                    "budget_line_code": "BL1",
                    "fiscal_year": 2026,
                    "needed_budget": 1000.0,
                    "actual": 0.0,
                    "remaining_requirement": 1000.0,
                }
            ]
        }
    }

    available_budget_lines = [
        {
            "fund_code": "TEST-OLD",
            "budget_line_code": "BL1",
            "remaining_secured_budget": 600.0,
        }
    ]

    budget_vs_actual = {
        "by_fund": {
            "lines": [
                {
                    "fund_code": "TEST-OLD",
                    "budget": 600.0,
                    "actual": 0.0,
                }
            ]
        }
    }

    grant_periods = {
        "TEST-OLD": {
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
        }
    }

    result = generate_funding_gap(
        needed_budget_vs_actual=needed_budget_vs_actual,
        available_budget_lines=available_budget_lines,
        budget_vs_actual=budget_vs_actual,
        grant_periods=grant_periods,
    )

    summary = result["summary"]

    assert summary["period_ineligible_funding_exposure"] == 600.0
    assert summary["period_unknown_funding_exposure"] == 0.0
    assert summary["dimension_incompatible_funding_exposure"] == 0.0

    assert (
        summary["requirements_with_period_ineligible_funding"]
        == 1
    )

    assert (
        summary["requirements_with_period_unknown_funding"]
        == 0
    )

    assert (
        summary["requirements_with_dimension_incompatible_funding"]
        == 0
    )

    assert "diagnostic_exposure_note" in result