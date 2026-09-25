from app.services.cfo_report_pdf import generate_cfo_report_pdf


def test_generate_cfo_report_pdf_returns_pdf_bytes():
    report = {
        "report_type": "cfo_report",
        "version": "1.0",
        "executive_summary": {
            "financial_health": {
                "score": 75,
                "rating": "Moderate",
            },
            "high_current_risk_count": 1,
            "high_forward_risk_count": 1,
            "high_opportunity_count": 1,
            "priority_action_count": 1,
        },
        "financial_health": {
            "score": 75,
            "rating": "Moderate",
        },
        "liquidity": {
            "cash_runway_months": 10.5,
        },
        "budget": {
            "status": "available",
        },
        "funding": {
            "funding_gap": {
                "summary": {
                    "funding_gap": 500000.0,
                }
            }
        },
        "core_cost_coverage": {
            "status": "available",
            "summary": {
                "needed_core_cost": 100000.0,
                "direct_grant_coverage": 50000.0,
                "allocated_indirect_recovery": 15000.0,
                "unrestricted_core_funding": 10000.0,
                "remaining_core_cost_gap": 25000.0,
                "core_cost_coverage_percentage": 75.0,
                "available_indirect_recovery": 30000.0,
                "used_indirect_recovery": 5000.0,
            },
            "lines": [],
            "controls": {},
        },
        "risks": {
            "current": [
                {
                    "severity": "High",
                    "category": "Budget",
                    "title": "Budget pressure",
                    "evidence": "Validated evidence.",
                }
            ],
            "forward": [
                {
                    "severity": "High",
                    "category": "Funding",
                    "title": "Forward Funding Gap exposure",
                    "evidence": "Validated forward evidence.",
                }
            ],
        },
        "opportunities": {
            "all": [
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Funding opportunity",
                    "evidence": "Validated opportunity evidence.",
                    "recommended_action": "Protect the opportunity.",
                }
            ]
        },
        "recommendations": {
            "all": [
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Close funding gap",
                    "reason": "Validated funding gap remains.",
                }
            ]
        },
        "trends": {
            "status": "available",
        },
        "forecast": {
            "status": "available",
        },
        "methodology": {
            "calculation_policy": (
                "The report consumes validated AI-FOS outputs."
            )
        },
    }

    pdf_bytes = generate_cfo_report_pdf(report)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_generate_cfo_report_pdf_handles_empty_report():
    pdf_bytes = generate_cfo_report_pdf({})

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500