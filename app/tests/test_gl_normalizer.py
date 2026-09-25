from app.services.gl_normalizer import GLNormalizer


def test_normalize_transaction_preserves_gl_dimensions():
    normalizer = GLNormalizer()

    transaction = {
        "fund_code": "FR0001-2026",
        "donor_code": "SIDA",
        "program_code": "RESEARCH",
        "category_code": "PERSONNEL",
        "budget_line_code": "BL-001",
        "donor_line_code": "SIDA-01",
    }

    result = normalizer.normalize_transaction(
        transaction=transaction,
        company_code="ACSS",
        source_system="business_central",
        transaction_index=0,
    )

    assert result["fund_code"] == "FR0001-2026"
    assert result["donor_code"] == "SIDA"
    assert result["program_code"] == "RESEARCH"
    assert result["category_code"] == "PERSONNEL"
    assert result["budget_line_code"] == "BL-001"
    assert result["donor_line_code"] == "SIDA-01"