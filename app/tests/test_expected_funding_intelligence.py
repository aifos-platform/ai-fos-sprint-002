from app.services.expected_funding_intelligence import (
    generate_expected_funding_intelligence,
)


def _record(
    *,
    code="EF-001",
    donor_code="FORD",
    donor_name="Ford Foundation",
    stage="Proposal Submitted",
    probability=50.0,
    minimum=80000.0,
    most_likely=100000.0,
    maximum=120000.0,
    requires_review=False,
):
    return {
        "expected_funding_code": code,
        "funding_name": "Expected Grant",
        "donor_code": donor_code,
        "donor_name": donor_name,
        "stage": stage,
        "probability_percentage": probability,
        "minimum_amount": minimum,
        "most_likely_amount": most_likely,
        "maximum_amount": maximum,
        "expected_decision_date": None,
        "expected_first_payment_date": None,
        "original_currency": "USD",
        "reporting_currency": "USD",
        "program_code": None,
        "project_code": None,
        "budget_line_code": None,
        "notes": None,
        "requires_review": requires_review,
        "review_reasons": [],
    }


def test_empty_expected_funding_is_not_available():
    result = generate_expected_funding_intelligence(
        []
    )

    assert result["status"] == "not_available"
    assert result["summary"]["record_count"] == 0


def test_calculates_pipeline_totals():
    result = generate_expected_funding_intelligence(
        [
            _record(
                minimum=80000,
                most_likely=100000,
                maximum=120000,
            ),
            _record(
                code="EF-002",
                minimum=150000,
                most_likely=200000,
                maximum=250000,
            ),
        ]
    )

    summary = result["summary"]

    assert summary["record_count"] == 2
    assert summary["minimum_pipeline_value"] == 230000.0
    assert summary["most_likely_pipeline_value"] == 300000.0
    assert summary["maximum_pipeline_value"] == 370000.0


def test_calculates_probability_weighted_expected_funding():
    result = generate_expected_funding_intelligence(
        [
            _record(
                probability=50,
                most_likely=100000,
            ),
            _record(
                code="EF-002",
                probability=75,
                most_likely=200000,
            ),
        ]
    )

    assert (
        result["summary"][
            "probability_weighted_expected_funding"
        ]
        == 200000.0
    )


def test_missing_probability_is_not_treated_as_zero():
    result = generate_expected_funding_intelligence(
        [
            _record(
                probability=None,
                most_likely=100000,
                requires_review=True,
            ),
        ]
    )

    summary = result["summary"]

    assert (
        summary[
            "probability_weighted_expected_funding"
        ]
        is None
    )

    assert (
        summary[
            "weighted_record_count"
        ]
        == 0
    )


def test_review_records_are_reported():
    result = generate_expected_funding_intelligence(
        [
            _record(),
            _record(
                code="EF-002",
                requires_review=True,
            ),
        ]
    )

    assert (
        result["summary"][
            "record_count_requiring_review"
        ]
        == 1
    )


def test_expected_funding_is_never_classified_as_secured():
    result = generate_expected_funding_intelligence(
        [
            _record(),
        ]
    )

    assert (
        result["controls"][
            "prospective_funding_only"
        ]
        is True
    )

    assert (
        result["controls"][
            "treated_as_secured_funding"
        ]
        is False
    )

    assert (
        result["controls"][
            "financial_recalculation_performed"
        ]
        is False
    )