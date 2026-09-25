from app.services.core_cost_coverage_normalizer import (
    CoreCostCoverageNormalizer,
)


def test_normalizes_direct_grant_coverage_record():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="direct_grant_coverage",
        fund_code="GRANT-001",
        budget_line_code="SAL-001",
        amount="25000",
    )

    assert result["coverage_type"] == "direct_grant_coverage"
    assert result["fund_code"] == "GRANT-001"
    assert result["budget_line_code"] == "SAL-001"
    assert result["amount"] == 25000.0
    assert result["requires_review"] is False
    assert result["review_reasons"] == []

def test_normalizes_indirect_recovery_allocation_record():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="indirect_recovery_allocation",
        fund_code="GRANT-002",
        budget_line_code="SAL-001",
        amount="15000.50",
    )

    assert (
        result["coverage_type"]
        == "indirect_recovery_allocation"
    )
    assert result["fund_code"] == "GRANT-002"
    assert result["budget_line_code"] == "SAL-001"
    assert result["amount"] == 15000.50
    assert result["requires_review"] is False
    assert result["review_reasons"] == []

def test_normalizes_unrestricted_core_funding_record():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="unrestricted_core_funding",
        fund_code="CORE-001",
        budget_line_code="SAL-002",
        amount="10000",
    )

    assert (
        result["coverage_type"]
        == "unrestricted_core_funding"
    )
    assert result["fund_code"] == "CORE-001"
    assert result["budget_line_code"] == "SAL-002"
    assert result["amount"] == 10000.0
    assert result["requires_review"] is False
    assert result["review_reasons"] == []

def test_normalizes_available_indirect_recovery_record():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="available_indirect_recovery",
        fund_code="GRANT-003",
        amount="30000",
    )

    assert (
        result["coverage_type"]
        == "available_indirect_recovery"
    )
    assert result["fund_code"] == "GRANT-003"
    assert result["budget_line_code"] is None
    assert result["amount"] == 30000.0
    assert result["requires_review"] is False
    assert result["review_reasons"] == []

def test_normalizes_used_indirect_recovery_record():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="used_indirect_recovery",
        budget_line_code="SAL-001",
        amount="12000",
    )

    assert (
        result["coverage_type"]
        == "used_indirect_recovery"
    )
    assert result["fund_code"] is None
    assert result["budget_line_code"] == "SAL-001"
    assert result["amount"] == 12000.0
    assert result["requires_review"] is False
    assert result["review_reasons"] == []

def test_unknown_coverage_type_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="something_unknown",
        fund_code="GRANT-001",
        budget_line_code="SAL-001",
        amount="10000",
    )

    assert result["coverage_type"] == "something_unknown"
    assert result["requires_review"] is True
    assert "Unknown coverage type." in result["review_reasons"]

def test_missing_coverage_type_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type=None,
        fund_code="GRANT-001",
        budget_line_code="SAL-001",
        amount="10000",
    )

    assert result["coverage_type"] is None
    assert result["requires_review"] is True
    assert (
        "Missing coverage type."
        in result["review_reasons"]
    )

def test_missing_amount_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="direct_grant_coverage",
        fund_code="GRANT-001",
        budget_line_code="SAL-001",
        amount=None,
    )

    assert result["amount"] == 0.0
    assert result["requires_review"] is True
    assert (
        "Missing amount."
        in result["review_reasons"]
    )

def test_negative_amount_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="direct_grant_coverage",
        fund_code="GRANT-001",
        budget_line_code="SAL-001",
        amount="-5000",
    )

    assert result["amount"] == -5000.0
    assert result["requires_review"] is True
    assert (
        "Core cost coverage amount cannot be negative."
        in result["review_reasons"]
    )   

def test_direct_grant_coverage_missing_budget_line_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="direct_grant_coverage",
        fund_code="GRANT-001",
        budget_line_code=None,
        amount="25000",
    )

    assert result["budget_line_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing budget line code."
        in result["review_reasons"]
    )

def test_indirect_recovery_allocation_missing_budget_line_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="indirect_recovery_allocation",
        fund_code="GRANT-001",
        budget_line_code=None,
        amount="15000",
    )

    assert result["budget_line_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing budget line code."
        in result["review_reasons"]
    ) 

def test_unrestricted_core_funding_missing_budget_line_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="unrestricted_core_funding",
        fund_code="CORE-001",
        budget_line_code=None,
        amount="10000",
    )

    assert result["budget_line_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing budget line code."
        in result["review_reasons"]
    ) 

def test_direct_grant_coverage_missing_fund_code_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="direct_grant_coverage",
        fund_code=None,
        budget_line_code="SAL-001",
        amount="25000",
    )

    assert result["fund_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing fund code."
        in result["review_reasons"]
    ) 

def test_indirect_recovery_allocation_missing_fund_code_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="indirect_recovery_allocation",
        fund_code=None,
        budget_line_code="SAL-001",
        amount="15000",
    )

    assert result["fund_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing fund code."
        in result["review_reasons"]
    )

def test_available_indirect_recovery_missing_fund_code_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="available_indirect_recovery",
        fund_code=None,
        amount="30000",
    )

    assert result["fund_code"] is None
    assert result["budget_line_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing fund code."
        in result["review_reasons"]
    )

def test_used_indirect_recovery_missing_budget_line_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="used_indirect_recovery",
        budget_line_code=None,
        amount="12000",
    )

    assert result["budget_line_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing budget line code."
        in result["review_reasons"]
    )

def test_invalid_amount_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="direct_grant_coverage",
        fund_code="GRANT-001",
        budget_line_code="SAL-001",
        amount="not-a-number",
    )

    assert result["amount"] == 0.0
    assert result["requires_review"] is True
    assert (
        "Invalid amount."
        in result["review_reasons"]
    )

def test_unrestricted_core_funding_missing_fund_code_requires_review():
    normalizer = CoreCostCoverageNormalizer()

    result = normalizer.normalize_line(
        coverage_type="unrestricted_core_funding",
        fund_code=None,
        budget_line_code="SAL-001",
        amount="10000",
    )

    assert result["fund_code"] is None
    assert result["requires_review"] is True
    assert (
        "Missing fund code."
        in result["review_reasons"]
    )                             
                         
        