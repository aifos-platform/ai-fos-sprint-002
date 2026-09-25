from app.organization import Organization


def _expected_record(
    *,
    code="EF-001",
    probability=50.0,
    most_likely=100000.0,
):
    return {
        "expected_funding_code": code,
        "funding_name": "Expected Grant",
        "donor_code": "FORD",
        "donor_name": "Ford Foundation",
        "stage": "Proposal Submitted",
        "probability_percentage": probability,
        "minimum_amount": 80000.0,
        "most_likely_amount": most_likely,
        "maximum_amount": 120000.0,
        "expected_decision_date": None,
        "expected_first_payment_date": None,
        "original_currency": "USD",
        "reporting_currency": "USD",
        "program_code": None,
        "project_code": None,
        "budget_line_code": None,
        "notes": None,
        "requires_review": False,
        "review_reasons": [],
    }


def test_load_expected_funding_stores_separate_records():
    organization = Organization()

    organization.load_expected_funding(
        [
            _expected_record(),
        ]
    )

    assert len(
        organization.expected_funding
    ) == 1

    assert (
        organization.expected_funding[0][
            "expected_funding_code"
        ]
        == "EF-001"
    )

    assert organization.funding_gap is None


def test_generate_expected_funding_analysis():
    organization = Organization()

    organization.load_expected_funding(
        [
            _expected_record(
                probability=50.0,
                most_likely=100000.0,
            ),
            _expected_record(
                code="EF-002",
                probability=75.0,
                most_likely=200000.0,
            ),
        ]
    )

    organization.generate_expected_funding_analysis()

    result = (
        organization.expected_funding_intelligence
    )

    assert result["status"] == "available"

    assert (
        result["summary"][
            "record_count"
        ]
        == 2
    )

    assert (
        result["summary"][
            "probability_weighted_expected_funding"
        ]
        == 200000.0
    )

    assert (
        result["controls"][
            "treated_as_secured_funding"
        ]
        is False
    )


def test_empty_expected_funding_generates_not_available():
    organization = Organization()

    organization.generate_expected_funding_analysis()

    result = (
        organization.expected_funding_intelligence
    )

    assert result["status"] == "not_available"

    assert (
        result["summary"][
            "record_count"
        ]
        == 0
    )