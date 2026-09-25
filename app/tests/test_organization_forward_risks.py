from app.organization import Organization


def test_organization_initializes_forward_risks_empty():
    organization = Organization()

    assert organization.forward_risks == []


def test_build_forward_risks_stores_result(
    monkeypatch,
):
    organization = Organization()

    organization.risk_assessment = [
        {
            "severity": "High",
            "category": "Operating Performance",
            "title": "Operating deficit",
            "evidence": "Current deficit.",
            "recommendation": "Review deficit drivers.",
        },
    ]

    organization.financial_trends = {
        "latest_month_comparison": {},
    }

    organization.financial_forecast = {
        "status": "available",
    }

    organization.liquidity = {
        "cash_runway_months": 5.0,
    }

    organization.funding_gap = {
        "summary": {},
    }

    organization.grant_diagnostics = {
        "matched_grants": [],
    }

    expected_result = [
        {
            "severity": "Medium",
            "category": "Liquidity",
            "title": "Limited forward cash runway",
            "evidence": "Forward risk evidence.",
            "recommendation": "Review liquidity.",
        },
    ]

    def fake_generate_forward_risks(**kwargs):
        assert kwargs["risk_assessment"] == (
            organization.risk_assessment
        )
        assert kwargs["financial_trends"] == (
            organization.financial_trends
        )
        assert kwargs["financial_forecast"] == (
            organization.financial_forecast
        )
        assert kwargs["liquidity"] == (
            organization.liquidity
        )
        assert kwargs["funding_gap"] == (
            organization.funding_gap
        )
        assert kwargs["grant_diagnostics"] == (
            organization.grant_diagnostics
        )

        return expected_result

    monkeypatch.setattr(
        "app.organization.generate_forward_risks",
        fake_generate_forward_risks,
    )

    organization.build_forward_risks()

    assert organization.forward_risks == expected_result


def test_build_forward_risks_does_not_modify_current_risk_register(
    monkeypatch,
):
    organization = Organization()

    current_risks = [
        {
            "severity": "High",
            "category": "Operating Performance",
            "title": "Operating deficit",
            "evidence": "Current risk.",
            "recommendation": "Current recommendation.",
        },
    ]

    organization.risk_assessment = [
        risk.copy()
        for risk in current_risks
    ]

    monkeypatch.setattr(
        "app.organization.generate_forward_risks",
        lambda **kwargs: [
            {
                "severity": "High",
                "category": "Funding",
                "title": "Forward Funding Gap exposure",
                "evidence": "Forward risk.",
                "recommendation": "Forward recommendation.",
            },
        ],
    )

    organization.build_forward_risks()

    assert organization.risk_assessment == current_risks
    assert len(organization.forward_risks) == 1