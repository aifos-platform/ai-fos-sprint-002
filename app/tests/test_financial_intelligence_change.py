from app.services.financial_intelligence_change import (
    generate_financial_intelligence_change,
)


def _snapshot(
    *,
    snapshot_id: str,
    health_score: float | None = None,
    runway: float | None = None,
    available_cash: float | None = None,
    funding_gap: float | None = None,
    coverage: float | None = None,
):
    return {
        "snapshot_id": snapshot_id,
        "captured_at": "2026-09-13T12:00:00+00:00",
        "financial_intelligence": {
            "financial_health": {
                "score": health_score,
                "categories": {},
            },
            "liquidity": {
                "available_cash": available_cash,
                "cash_runway_months": runway,
            },
            "funding_gap": {
                "summary": {
                    "funding_gap": funding_gap,
                    "applied_coverage_percentage": (
                        coverage
                    ),
                },
            },
        },
    }


def _metric(
    result,
    metric_id,
):
    return next(
        item
        for item in result["comparisons"]
        if item["metric_id"] == metric_id
    )


def test_financial_health_score_increase_is_improvement():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            health_score=54,
        ),
        _snapshot(
            snapshot_id="b",
            health_score=63,
        ),
    )

    metric = _metric(
        result,
        "financial_health_score",
    )

    assert metric["absolute_change"] == 9.0
    assert metric["signal"] == "improved"


def test_financial_health_score_decrease_is_deterioration():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            health_score=70,
        ),
        _snapshot(
            snapshot_id="b",
            health_score=50,
        ),
    )

    metric = _metric(
        result,
        "financial_health_score",
    )

    assert metric["signal"] == "deteriorated"


def test_cash_runway_increase_is_improvement():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            runway=5.0,
        ),
        _snapshot(
            snapshot_id="b",
            runway=8.0,
        ),
    )

    metric = _metric(
        result,
        "cash_runway_months",
    )

    assert metric["absolute_change"] == 3.0
    assert metric["signal"] == "improved"


def test_cash_runway_decrease_is_deterioration():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            runway=8.0,
        ),
        _snapshot(
            snapshot_id="b",
            runway=4.0,
        ),
    )

    metric = _metric(
        result,
        "cash_runway_months",
    )

    assert metric["signal"] == "deteriorated"


def test_funding_gap_reduction_is_improvement():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            funding_gap=1200000,
        ),
        _snapshot(
            snapshot_id="b",
            funding_gap=800000,
        ),
    )

    metric = _metric(
        result,
        "funding_gap",
    )

    assert metric["absolute_change"] == -400000.0
    assert metric["signal"] == "improved"


def test_funding_gap_increase_is_deterioration():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            funding_gap=800000,
        ),
        _snapshot(
            snapshot_id="b",
            funding_gap=1200000,
        ),
    )

    metric = _metric(
        result,
        "funding_gap",
    )

    assert metric["signal"] == "deteriorated"


def test_funding_coverage_increase_is_improvement():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            coverage=50,
        ),
        _snapshot(
            snapshot_id="b",
            coverage=75,
        ),
    )

    metric = _metric(
        result,
        "applied_coverage_percentage",
    )

    assert metric["absolute_change"] == 25.0
    assert metric["signal"] == "improved"


def test_available_cash_change_is_direction_only():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            available_cash=1000,
        ),
        _snapshot(
            snapshot_id="b",
            available_cash=1500,
        ),
    )

    metric = _metric(
        result,
        "available_cash",
    )

    assert metric["signal"] == "increased"
    assert metric["signal"] != "improved"


def test_missing_metric_is_not_invented():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
        ),
        _snapshot(
            snapshot_id="b",
            runway=6.0,
        ),
    )

    metric = _metric(
        result,
        "cash_runway_months",
    )

    assert metric["signal"] == "unavailable"
    assert metric["absolute_change"] is None


def test_unchanged_metric_is_reported_as_unchanged():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            health_score=60,
        ),
        _snapshot(
            snapshot_id="b",
            health_score=60,
        ),
    )

    metric = _metric(
        result,
        "financial_health_score",
    )

    assert metric["signal"] == "unchanged"


def test_mixed_improvements_and_deteriorations_return_mixed():
    result = generate_financial_intelligence_change(
        _snapshot(
            snapshot_id="a",
            health_score=50,
            runway=10,
        ),
        _snapshot(
            snapshot_id="b",
            health_score=60,
            runway=5,
        ),
    )

    assert result["overall_signal"] == "mixed"


def test_comparison_is_read_only_and_deterministic():
    snapshot_a = _snapshot(
        snapshot_id="a",
        health_score=50,
    )

    snapshot_b = _snapshot(
        snapshot_id="b",
        health_score=60,
    )

    original_a = repr(snapshot_a)
    original_b = repr(snapshot_b)

    result = generate_financial_intelligence_change(
        snapshot_a,
        snapshot_b,
    )

    assert repr(snapshot_a) == original_a
    assert repr(snapshot_b) == original_b

    controls = result["controls"]

    assert controls["deterministic"] is True
    assert controls["read_only"] is True
    assert (
        controls["financial_recalculation_performed"]
        is False
    )
    assert (
        controls["historical_snapshots_modified"]
        is False
    )
    assert (
        controls["missing_values_not_invented"]
        is True
    )
    assert (
        controls["hypothetical_scenarios_excluded"]
        is True
    )
def _risk_snapshot(
    snapshot_id,
    risks,
):
    return {
        "snapshot_id": snapshot_id,
        "financial_intelligence": {
            "risk_assessment": risks,
        },
    }


def test_new_risk_is_detected():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [],
        ),
        _risk_snapshot(
            "b",
            [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Operating deficit",
                    "evidence": "Deficit exists.",
                }
            ],
        ),
    )

    assert result["summary"]["new_count"] == 1
    assert result["movements"][0]["movement"] == "new"


def test_resolved_risk_is_detected():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Operating deficit",
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [],
        ),
    )

    assert result["summary"]["resolved_count"] == 1
    assert (
        result["movements"][0]["movement"]
        == "resolved"
    )


def test_same_risk_with_same_severity_is_unchanged():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Operating deficit",
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Operating deficit",
                }
            ],
        ),
    )

    assert result["summary"]["persistent_count"] == 1
    assert result["summary"]["unchanged_count"] == 1


def test_cash_runway_title_change_is_same_risk_family():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "High",
                    "category": "Liquidity",
                    "title": "Low cash runway",
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [
                {
                    "severity": "Medium",
                    "category": "Liquidity",
                    "title": (
                        "Cash runway requires monitoring"
                    ),
                }
            ],
        ),
    )

    assert len(result["movements"]) == 1

    assert (
        result["movements"][0]["risk_family"]
        == "cash_runway"
    )

    assert (
        result["movements"][0]["movement"]
        == "severity_decreased"
    )


def test_cash_runway_severity_increase_is_detected():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "Medium",
                    "category": "Liquidity",
                    "title": (
                        "Cash runway requires monitoring"
                    ),
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [
                {
                    "severity": "Critical",
                    "category": "Liquidity",
                    "title": "Critical cash runway",
                }
            ],
        ),
    )

    assert (
        result["summary"][
            "severity_increased_count"
        ]
        == 1
    )


def test_financial_health_title_change_is_same_family():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "Critical",
                    "category": "Financial Health",
                    "title": "Critical financial health",
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [
                {
                    "severity": "High",
                    "category": "Financial Health",
                    "title": "Weak financial health",
                }
            ],
        ),
    )

    assert len(result["movements"]) == 1

    assert (
        result["movements"][0]["risk_family"]
        == "financial_health"
    )

    assert (
        result["movements"][0]["movement"]
        == "severity_decreased"
    )


def test_no_major_risk_fallback_is_not_treated_as_real_risk():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "Low",
                    "category": "General",
                    "title": (
                        "No major financial risks detected"
                    ),
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [],
        ),
    )

    assert result["movements"] == []

    assert (
        result["summary"]["resolved_count"]
        == 0
    )


def test_risk_evidence_change_does_not_create_new_risk():
    from app.services.financial_intelligence_change import (
        compare_risk_movement,
    )

    result = compare_risk_movement(
        _risk_snapshot(
            "a",
            [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Operating deficit",
                    "evidence": "Old evidence.",
                }
            ],
        ),
        _risk_snapshot(
            "b",
            [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Operating deficit",
                    "evidence": "Updated evidence.",
                }
            ],
        ),
    )

    assert len(result["movements"]) == 1
    assert (
        result["movements"][0]["movement"]
        == "unchanged"
    )

    assert (
        result["controls"][
            "evidence_text_used_for_matching"
        ]
        is False
    )

def test_unified_change_positive_only_is_improved():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    result = (
        generate_unified_financial_intelligence_change(
            _snapshot(
                snapshot_id="a",
                health_score=50,
                runway=5,
            ),
            _snapshot(
                snapshot_id="b",
                health_score=60,
                runway=8,
            ),
        )
    )

    assert result["overall_direction"] == "improved"

    assert (
        result["evidence_summary"][
            "positive_evidence_count"
        ]
        == 2
    )

    assert (
        result["evidence_summary"][
            "negative_evidence_count"
        ]
        == 0
    )


def test_unified_change_negative_only_is_deteriorated():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    result = (
        generate_unified_financial_intelligence_change(
            _snapshot(
                snapshot_id="a",
                health_score=70,
                runway=10,
            ),
            _snapshot(
                snapshot_id="b",
                health_score=50,
                runway=4,
            ),
        )
    )

    assert (
        result["overall_direction"]
        == "deteriorated"
    )

    assert (
        result["evidence_summary"][
            "negative_evidence_count"
        ]
        == 2
    )


def test_unified_change_positive_and_negative_is_mixed():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    result = (
        generate_unified_financial_intelligence_change(
            _snapshot(
                snapshot_id="a",
                health_score=50,
                runway=10,
            ),
            _snapshot(
                snapshot_id="b",
                health_score=60,
                runway=5,
            ),
        )
    )

    assert result["overall_direction"] == "mixed"


def test_unified_change_new_high_risk_requires_priority_review():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    snapshot_a = _risk_snapshot(
        "a",
        [],
    )

    snapshot_b = _risk_snapshot(
        "b",
        [
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Operating deficit",
            }
        ],
    )

    result = (
        generate_unified_financial_intelligence_change(
            snapshot_a,
            snapshot_b,
        )
    )

    assert (
        result["overall_direction"]
        == "deteriorated"
    )

    assert (
        result["management_attention"]
        == "priority_review"
    )


def test_unified_change_resolved_risk_is_positive_evidence():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    snapshot_a = _risk_snapshot(
        "a",
        [
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Operating deficit",
            }
        ],
    )

    snapshot_b = _risk_snapshot(
        "b",
        [],
    )

    result = (
        generate_unified_financial_intelligence_change(
            snapshot_a,
            snapshot_b,
        )
    )

    assert result["overall_direction"] == "improved"

    assert (
        result["evidence_summary"][
            "resolved_risk_count"
        ]
        == 1
    )


def test_unified_change_neutral_cash_movement_does_not_vote_on_health():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    result = (
        generate_unified_financial_intelligence_change(
            _snapshot(
                snapshot_id="a",
                available_cash=1000,
            ),
            _snapshot(
                snapshot_id="b",
                available_cash=2000,
            ),
        )
    )

    assert (
        result["overall_direction"]
        == "stable_or_insufficient_evidence"
    )

    assert (
        result["evidence_summary"][
            "positive_evidence_count"
        ]
        == 0
    )

    assert (
        result["evidence_summary"][
            "negative_evidence_count"
        ]
        == 0
    )


def test_unified_change_preserves_component_outputs():
    from app.services.financial_intelligence_change import (
        generate_unified_financial_intelligence_change,
    )

    result = (
        generate_unified_financial_intelligence_change(
            _snapshot(
                snapshot_id="a",
                health_score=50,
            ),
            _snapshot(
                snapshot_id="b",
                health_score=60,
            ),
        )
    )

    assert result["metric_change"]["status"] == "available"
    assert result["risk_change"]["status"] == "available"

    controls = result["controls"]

    assert controls["deterministic"] is True
    assert controls["read_only"] is True

    assert (
        controls[
            "financial_recalculation_performed"
        ]
        is False
    )

    assert (
        controls[
            "historical_snapshots_modified"
        ]
        is False
    )

    assert (
        controls[
            "missing_evidence_not_invented"
        ]
        is True
    )        