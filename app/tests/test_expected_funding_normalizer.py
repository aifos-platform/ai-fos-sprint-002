import pytest

from app.services.expected_funding_normalizer import (
    ExpectedFundingNormalizer,
)


def test_normalizes_valid_expected_funding_record():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-001",
        funding_name="Core Support Proposal",
        donor_code="OSF",
        donor_name="Open Society Foundations",
        stage="Proposal Submitted",
        probability_percentage="75",
        minimum_amount="$400,000",
        most_likely_amount="$500,000",
        maximum_amount="$600,000",
        expected_decision_date="2026-11-15",
        expected_first_payment_date="2027-01-15",
        original_currency="USD",
        reporting_currency="USD",
        program_code="CORE",
        project_code="PRJ-001",
        budget_line_code="BL-001",
        notes="Management estimate",
    )

    assert result["expected_funding_code"] == "EF-001"
    assert result["funding_name"] == "Core Support Proposal"
    assert result["donor_code"] == "OSF"
    assert result["stage"] == "Proposal Submitted"

    assert result["probability_percentage"] == 75.0

    assert result["minimum_amount"] == 400000.0
    assert result["most_likely_amount"] == 500000.0
    assert result["maximum_amount"] == 600000.0

    assert result["expected_decision_date"] == "2026-11-15"
    assert result["expected_first_payment_date"] == "2027-01-15"

    assert result["requires_review"] is False
    assert result["review_reasons"] == []


def test_missing_probability_remains_none():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-002",
        funding_name="Expected Grant",
        donor_code="FORD",
        probability_percentage=None,
        most_likely_amount=250000,
    )

    assert result["probability_percentage"] is None
    assert result["requires_review"] is True

    assert (
        "Missing probability percentage."
        in result["review_reasons"]
    )


def test_missing_most_likely_amount_remains_none():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-003",
        funding_name="Expected Grant",
        donor_code="IDRC",
        probability_percentage=60,
        most_likely_amount=None,
    )

    assert result["most_likely_amount"] is None
    assert result["requires_review"] is True

    assert (
        "Missing most likely amount."
        in result["review_reasons"]
    )


@pytest.mark.parametrize(
    "probability",
    [
        -1,
        101,
    ],
)
def test_probability_outside_valid_range_requires_review(
    probability,
):
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-004",
        funding_name="Expected Grant",
        donor_code="SIDA",
        probability_percentage=probability,
        most_likely_amount=300000,
    )

    assert result["requires_review"] is True

    assert (
        "Probability percentage must be between 0 and 100."
        in result["review_reasons"]
    )


def test_zero_probability_is_preserved_as_explicit_zero():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-005",
        funding_name="Low Probability Proposal",
        donor_code="MELLON",
        probability_percentage=0,
        most_likely_amount=100000,
    )

    assert result["probability_percentage"] == 0.0


def test_missing_code_requires_review():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code=None,
        funding_name="Expected Grant",
        donor_code="FORD",
        probability_percentage=50,
        most_likely_amount=200000,
    )

    assert result["requires_review"] is True

    assert (
        "Missing expected funding code."
        in result["review_reasons"]
    )


def test_negative_expected_amount_requires_review():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-006",
        funding_name="Expected Grant",
        donor_code="FORD",
        probability_percentage=50,
        most_likely_amount=-100000,
    )

    assert result["requires_review"] is True

    assert (
        "Expected funding amount cannot be negative."
        in result["review_reasons"]
    )


def test_blank_optional_fields_remain_none():
    normalizer = ExpectedFundingNormalizer()

    result = normalizer.normalize_line(
        expected_funding_code="EF-007",
        funding_name="Expected Grant",
        donor_code="FORD",
        probability_percentage=50,
        most_likely_amount=100000,
        project_code="",
        budget_line_code="",
        notes="",
    )

    assert result["project_code"] is None
    assert result["budget_line_code"] is None
    assert result["notes"] is None