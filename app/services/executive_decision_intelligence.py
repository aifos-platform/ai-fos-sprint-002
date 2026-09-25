from typing import Any


PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


EXECUTIVE_SIGNAL_BY_PRIORITY = {
    "Critical": "immediate_action",
    "High": "priority_attention",
    "Medium": "management_review",
    "Low": "monitor",
}


def generate_executive_decision_intelligence(
    risk_assessment: list[dict[str, Any]] | None,
    forward_risks: list[dict[str, Any]] | None,
    cfo_recommendations: list[dict[str, Any]] | None,
    financial_opportunities: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """
    Build deterministic Executive Decision Intelligence.

    This service prioritizes existing verified AI-FOS intelligence
    for management attention.

    It does not recalculate financial statements, liquidity,
    forecasts, budgets, grants, Funding Gap, financial health,
    risks, opportunities, or recommendations.

    Responsibilities:

    1. Convert verified current risks into management priorities.
    2. Convert verified forward-looking risks into priorities.
    3. Use existing CFO recommendations as the preferred action
       source when they correspond to an identified risk.
    4. Remove duplicate or substantially overlapping priorities.
    5. Rank priorities deterministically by severity.
    6. Preserve verified financial opportunities separately.
    """

    risk_assessment = risk_assessment or []
    forward_risks = forward_risks or []
    cfo_recommendations = cfo_recommendations or []
    financial_opportunities = financial_opportunities or []

    candidates: list[dict[str, Any]] = []

    # --------------------------------------------------
    # 1. Current verified risks
    # --------------------------------------------------

    for risk in risk_assessment:
        if not isinstance(risk, dict):
            continue

        if _is_no_major_risk_fallback(risk):
            continue

        severity = _normalize_priority(
            risk.get("severity")
        )

        category = _clean_text(
            risk.get("category")
        ) or "Financial Management"

        title = _clean_text(
            risk.get("title")
        ) or "Financial risk"

        evidence = _clean_text(
            risk.get("evidence")
        )

        recommendation = _find_matching_recommendation(
            title=title,
            category=category,
            recommendations=cfo_recommendations,
        )

        management_action = (
            _clean_text(
                recommendation.get("action")
            )
            if recommendation
            else ""
        )

        expected_impact = (
            _clean_text(
                recommendation.get("expected_impact")
            )
            if recommendation
            else ""
        )

        if not management_action:
            management_action = _clean_text(
                risk.get("recommendation")
            )

        candidates.append(
            {
                "priority": severity,
                "category": category,
                "title": title,
                "evidence": evidence,
                "management_action": management_action,
                "expected_impact": expected_impact,
                "source": "risk_assessment",
                "source_type": "current_risk",
            }
        )

    # --------------------------------------------------
    # 2. Forward-looking verified risks
    # --------------------------------------------------

    for risk in forward_risks:
        if not isinstance(risk, dict):
            continue

        severity = _normalize_priority(
            risk.get("severity")
        )

        category = _clean_text(
            risk.get("category")
        ) or "Forward-Looking Risk"

        title = _clean_text(
            risk.get("title")
        ) or "Emerging financial risk"

        evidence = _clean_text(
            risk.get("evidence")
        )

        recommendation = _find_matching_recommendation(
            title=title,
            category=category,
            recommendations=cfo_recommendations,
        )

        management_action = (
            _clean_text(
                recommendation.get("action")
            )
            if recommendation
            else ""
        )

        expected_impact = (
            _clean_text(
                recommendation.get("expected_impact")
            )
            if recommendation
            else ""
        )

        if not management_action:
            management_action = _clean_text(
                risk.get("recommendation")
            )

        candidates.append(
            {
                "priority": severity,
                "category": category,
                "title": title,
                "evidence": evidence,
                "management_action": management_action,
                "expected_impact": expected_impact,
                "source": "forward_risk",
                "source_type": "forward_risk",
            }
        )

    # --------------------------------------------------
    # 3. CFO recommendations not already represented
    # --------------------------------------------------
    #
    # Some recommendations are created from validated outputs
    # directly rather than through the Risk Register.
    #
    # Examples:
    # - cash-flow recommendations
    # - grant diagnostics
    # - Funding Gap evidence issues
    #
    # These should remain eligible for executive prioritization.
    # --------------------------------------------------

    for recommendation in cfo_recommendations:
        if not isinstance(recommendation, dict):
            continue

        if _is_monitoring_fallback(recommendation):
            continue

        priority = _normalize_priority(
            recommendation.get("priority")
        )

        category = _clean_text(
            recommendation.get("category")
        ) or "Financial Management"

        title = _clean_text(
            recommendation.get("title")
        ) or "Management action"

        evidence = (
            _clean_text(
                recommendation.get("evidence")
            )
            or _clean_text(
                recommendation.get("reason")
            )
        )

        action = _clean_text(
            recommendation.get("action")
        )

        if not action:
            action = title

        expected_impact = _clean_text(
            recommendation.get("expected_impact")
        )

        linked_risk = _clean_text(
            recommendation.get("linked_risk")
        )

        candidate_title = (
            linked_risk
            if linked_risk
            else title
        )

        candidates.append(
            {
                "priority": priority,
                "category": category,
                "title": candidate_title,
                "evidence": evidence,
                "management_action": action,
                "expected_impact": expected_impact,
                "source": _clean_text(
                    recommendation.get("source")
                )
                or "cfo_recommendation",
                "source_type": "recommendation",
            }
        )

    # --------------------------------------------------
    # 4. Remove duplicates / overlapping priorities
    # --------------------------------------------------

    priorities = _deduplicate_priorities(
        candidates
    )

    # --------------------------------------------------
    # 5. Deterministic ranking
    # --------------------------------------------------

    priorities.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(
                str(
                    item.get("priority")
                ),
                0,
            ),
            _source_rank(
                item.get("source_type")
            ),
            str(
                item.get("category")
                or ""
            ).lower(),
            str(
                item.get("title")
                or ""
            ).lower(),
        ),
        reverse=True,
    )

    for index, priority in enumerate(
        priorities,
        start=1,
    ):
        priority["rank"] = index

    # --------------------------------------------------
    # 6. Opportunities remain separate
    # --------------------------------------------------

    opportunities = _prepare_opportunities(
        financial_opportunities
    )

    # --------------------------------------------------
    # 7. Executive summary signal
    # --------------------------------------------------

    if priorities:
        highest_priority = str(
            priorities[0].get("priority")
            or "Low"
        )

        executive_signal = (
            EXECUTIVE_SIGNAL_BY_PRIORITY.get(
                highest_priority,
                "monitor",
            )
        )

    else:
        highest_priority = "Low"
        executive_signal = "monitor"

    # --------------------------------------------------
    # 8. Management focus summary
    # --------------------------------------------------

    management_focus = []

    for priority in priorities[:5]:
        management_focus.append(
            {
                "rank": priority.get("rank"),
                "priority": priority.get("priority"),
                "category": priority.get("category"),
                "title": priority.get("title"),
                "management_action": priority.get(
                    "management_action"
                ),
            }
        )

    # --------------------------------------------------
    # 9. Deterministic result
    # --------------------------------------------------

    return {
        "status": "available",
        "executive_signal": executive_signal,
        "highest_priority": highest_priority,
        "priority_count": len(priorities),
        "opportunity_count": len(opportunities),
        "management_focus": management_focus,
        "priorities": priorities,
        "opportunities": opportunities,
        "controls": {
            "deterministic": True,
            "financial_recalculation_performed": False,
            "validated_outputs_preserved": True,
            "missing_evidence_not_invented": True,
            "opportunities_do_not_cancel_risks": True,
        },
    }


def _deduplicate_priorities(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Remove overlapping priorities conservatively.

    Matching is based on normalized title/category and linked
    risk meaning. When duplicates exist, the highest severity
    version is preserved and missing descriptive fields may be
    filled only from already verified candidate outputs.
    """

    deduplicated: list[dict[str, Any]] = []

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue

        duplicate_index = _find_duplicate_index(
            candidate=candidate,
            existing=deduplicated,
        )

        if duplicate_index is None:
            deduplicated.append(
                dict(candidate)
            )
            continue

        existing = deduplicated[
            duplicate_index
        ]

        candidate_priority = (
            PRIORITY_ORDER.get(
                str(
                    candidate.get("priority")
                ),
                0,
            )
        )

        existing_priority = (
            PRIORITY_ORDER.get(
                str(
                    existing.get("priority")
                ),
                0,
            )
        )

        if candidate_priority > existing_priority:
            stronger = dict(candidate)
            weaker = existing
        else:
            stronger = existing
            weaker = candidate

        for field in (
            "evidence",
            "management_action",
            "expected_impact",
        ):
            if not _clean_text(
                stronger.get(field)
            ):
                stronger[field] = (
                    _clean_text(
                        weaker.get(field)
                    )
                )

        if (
            _source_rank(
                weaker.get("source_type")
            )
            > _source_rank(
                stronger.get("source_type")
            )
            and candidate_priority
            == existing_priority
        ):
            stronger["source"] = (
                weaker.get("source")
            )
            stronger["source_type"] = (
                weaker.get("source_type")
            )

        deduplicated[
            duplicate_index
        ] = stronger

    return deduplicated


def _find_duplicate_index(
    candidate: dict[str, Any],
    existing: list[dict[str, Any]],
) -> int | None:

    candidate_title = _normalize_match_text(
        candidate.get("title")
    )

    candidate_category = _normalize_match_text(
        candidate.get("category")
    )

    for index, item in enumerate(
        existing
    ):
        existing_title = _normalize_match_text(
            item.get("title")
        )

        existing_category = _normalize_match_text(
            item.get("category")
        )

        # Exact normalized title match.
        if (
            candidate_title
            and existing_title
            and candidate_title
            == existing_title
        ):
            return index

        # Same category and strongly overlapping title meaning.
        if (
            candidate_category
            and candidate_category
            == existing_category
            and _titles_overlap(
                candidate_title,
                existing_title,
            )
        ):
            return index

    return None


def _titles_overlap(
    title_a: str,
    title_b: str,
) -> bool:

    if not title_a or not title_b:
        return False

    if title_a in title_b or title_b in title_a:
        return True

    words_a = {
        word
        for word in title_a.split()
        if len(word) >= 4
    }

    words_b = {
        word
        for word in title_b.split()
        if len(word) >= 4
    }

    if not words_a or not words_b:
        return False

    overlap = words_a.intersection(
        words_b
    )

    minimum_size = min(
        len(words_a),
        len(words_b),
    )

    if minimum_size == 0:
        return False

    return (
        len(overlap)
        / minimum_size
        >= 0.6
    )


def _find_matching_recommendation(
    title: str,
    category: str,
    recommendations: list[dict[str, Any]],
) -> dict[str, Any] | None:

    normalized_title = (
        _normalize_match_text(title)
    )

    normalized_category = (
        _normalize_match_text(category)
    )

    for recommendation in recommendations:
        if not isinstance(
            recommendation,
            dict,
        ):
            continue

        linked_risk = (
            _normalize_match_text(
                recommendation.get(
                    "linked_risk"
                )
            )
        )

        recommendation_category = (
            _normalize_match_text(
                recommendation.get(
                    "category"
                )
            )
        )

        recommendation_title = (
            _normalize_match_text(
                recommendation.get(
                    "title"
                )
            )
        )

        if (
            linked_risk
            and linked_risk
            == normalized_title
        ):
            return recommendation

        if (
            normalized_category
            and normalized_category
            == recommendation_category
            and _titles_overlap(
                normalized_title,
                recommendation_title,
            )
        ):
            return recommendation

    return None


def _prepare_opportunities(
    financial_opportunities: list[
        dict[str, Any]
    ],
) -> list[dict[str, Any]]:

    opportunities: list[
        dict[str, Any]
    ] = []

    for opportunity in financial_opportunities:
        if not isinstance(
            opportunity,
            dict,
        ):
            continue

        title = _clean_text(
            opportunity.get("title")
        )

        if not title:
            continue

        opportunities.append(
            {
                "priority": _normalize_priority(
                    opportunity.get("priority")
                ),
                "category": (
                    _clean_text(
                        opportunity.get("category")
                    )
                    or "Financial Opportunity"
                ),
                "title": title,
                "evidence": _clean_text(
                    opportunity.get("evidence")
                ),
                "recommended_action": (
                    _clean_text(
                        opportunity.get(
                            "recommended_action"
                        )
                    )
                ),
                "source": "financial_opportunity",
            }
        )

    opportunities.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(
                str(
                    item.get("priority")
                ),
                0,
            ),
            str(
                item.get("category")
                or ""
            ).lower(),
            str(
                item.get("title")
                or ""
            ).lower(),
        ),
        reverse=True,
    )

    return opportunities


def _normalize_priority(
    value: Any,
) -> str:

    text = _clean_text(value).lower()

    mapping = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    return mapping.get(
        text,
        "Medium",
    )


def _clean_text(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip()


def _normalize_match_text(
    value: Any,
) -> str:

    text = _clean_text(
        value
    ).lower()

    replacements = (
        "address ",
        "prepare for ",
        "resolve ",
        "review ",
        "implement ",
        "close the ",
        "close ",
        "improve ",
        "protect ",
    )

    for prefix in replacements:
        if text.startswith(prefix):
            text = text[
                len(prefix):
            ]

    cleaned = []

    for char in text:
        if (
            char.isalnum()
            or char.isspace()
        ):
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return " ".join(
        "".join(cleaned).split()
    )


def _source_rank(
    source_type: Any,
) -> int:

    source = _clean_text(
        source_type
    ).lower()

    ranking = {
        "current_risk": 3,
        "forward_risk": 2,
        "recommendation": 1,
    }

    return ranking.get(
        source,
        0,
    )


def _is_no_major_risk_fallback(
    risk: dict[str, Any],
) -> bool:

    title = _normalize_match_text(
        risk.get("title")
    )

    return title == (
        "no major financial risks detected"
    )


def _is_monitoring_fallback(
    recommendation: dict[str, Any],
) -> bool:

    source = _clean_text(
        recommendation.get("source")
    ).lower()

    title = _normalize_match_text(
        recommendation.get("title")
    )

    return (
        source == "general_monitoring"
        or title == "maintain financial monitoring"
    )