from typing import Any


def generate_scenario_decision_intelligence(
    scenario: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Interpret an existing deterministic financial scenario
    without recalculating any financial values.

    This layer converts validated scenario outputs into
    structured management decision signals.

    It must not:
    - modify the scenario;
    - recalculate financial results;
    - infer missing cash impacts;
    - infer missing runway impacts.
    """

    scenario = scenario or {}

    if scenario.get("status") != "available":
        return {
            "status": "not_available",
            "scenario_name": scenario.get(
                "scenario_name"
            ),
            "scenario_type": scenario.get(
                "scenario_type"
            ),
            "forecast_horizon_months": scenario.get(
                "forecast_horizon_months"
            ),
            "reason": (
                scenario.get("reason")
                or (
                    "A validated deterministic financial "
                    "scenario is required before AI-FOS can "
                    "generate scenario decision intelligence."
                )
            ),
            "controls": {
                "source_is_deterministic_scenario": True,
                "financial_recalculation_performed": False,
                "missing_impacts_not_invented": True,
                "recommendations_are_rule_based": True,
            },
        }

    impact = (
        scenario.get(
            "impact",
            {},
        )
        or {}
    )

    cash = (
        scenario.get(
            "cash",
            {},
        )
        or {}
    )

    runway = (
        scenario.get(
            "runway",
            {},
        )
        or {}
    )

    # --------------------------------------------------
    # Net-result direction
    # --------------------------------------------------

    overall_direction = _normalize_direction(
        impact.get(
            "net_result_direction"
        )
    )

    # --------------------------------------------------
    # Cash impact
    # --------------------------------------------------

    cash_variance = _optional_float(
        cash.get(
            "available_cash_variance"
        )
    )

    if cash_variance is None:
        cash_available = False
        cash_direction = None

    else:
        cash_available = True
        cash_direction = _direction_from_variance(
            cash_variance
        )

    # --------------------------------------------------
    # Runway impact
    # --------------------------------------------------

    runway_change = _optional_float(
        runway.get(
            "cash_runway_change_months"
        )
    )

    if runway_change is None:
        runway_available = False
        runway_direction = None

    else:
        runway_available = True
        runway_direction = _direction_from_variance(
            runway_change
        )

    scenario_runway = _optional_float(
        runway.get(
            "scenario_cash_runway_months"
        )
    )

    # --------------------------------------------------
    # Decision factors
    # --------------------------------------------------

    decision_factors: list[str] = []

    if overall_direction == "deteriorated":
        decision_factors.append(
            "net_result"
        )

    if cash_direction == "deteriorated":
        decision_factors.append(
            "cash"
        )

    if runway_direction == "deteriorated":
        decision_factors.append(
            "runway"
        )

    deterioration_count = len(
        decision_factors
    )

    # --------------------------------------------------
    # Decision signal
    # --------------------------------------------------

    positive_factors = 0
    negative_factors = 0

    if overall_direction == "improved":
        positive_factors += 1

    elif overall_direction == "deteriorated":
        negative_factors += 1

    if cash_direction == "improved":
        positive_factors += 1

    elif cash_direction == "deteriorated":
        negative_factors += 1

    if runway_direction == "improved":
        positive_factors += 1

    elif runway_direction == "deteriorated":
        negative_factors += 1

    if (
        positive_factors > 0
        and negative_factors > 0
    ):
        decision_signal = "mixed"

    elif negative_factors > 0:
        decision_signal = "negative"

    elif positive_factors > 0:
        decision_signal = "positive"

    else:
        decision_signal = "neutral"

    # --------------------------------------------------
    # Management severity
    # --------------------------------------------------

    if (
        scenario_runway is not None
        and scenario_runway <= 3.0
    ):
        severity = "critical"
        management_attention = "immediate"

    elif deterioration_count >= 2:
        severity = "high"
        management_attention = "priority_review"

    elif deterioration_count == 1:
        severity = "medium"
        management_attention = "review"

    else:
        severity = "low"
        management_attention = "monitor"

    # --------------------------------------------------
    # Deterministic recommended actions
    # --------------------------------------------------

    recommended_actions = _build_recommended_actions(
        overall_direction=overall_direction,
        cash_direction=cash_direction,
        runway_direction=runway_direction,
        severity=severity,
    )

    return {
        "status": "available",
        "scenario_name": scenario.get(
            "scenario_name"
        ),
        "scenario_type": scenario.get(
            "scenario_type"
        ),
        "forecast_horizon_months": scenario.get(
            "forecast_horizon_months"
        ),
        "overall_direction": overall_direction,
        "decision_signal": decision_signal,
        "severity": severity,
        "management_attention": management_attention,
        "decision_factors": decision_factors,
        "net_result_impact": {
            "direction": overall_direction,
            "variance": _optional_float(
                impact.get(
                    "net_result_variance"
                )
            ),
        },
        "cash_impact": {
            "available": cash_available,
            "direction": cash_direction,
            "variance": cash_variance,
        },
        "runway_impact": {
            "available": runway_available,
            "direction": runway_direction,
            "change_months": runway_change,
        },
        "recommended_actions": recommended_actions,
        "controls": {
            "source_is_deterministic_scenario": True,
            "financial_recalculation_performed": False,
            "missing_impacts_not_invented": True,
            "recommendations_are_rule_based": True,
        },
    }


def _build_recommended_actions(
    *,
    overall_direction: str,
    cash_direction: str | None,
    runway_direction: str | None,
    severity: str,
) -> list[dict[str, str]]:
    """
    Build deterministic management actions only from
    verified scenario directions.

    No financial amounts are calculated here.
    """

    actions: list[dict[str, str]] = []

    if overall_direction == "deteriorated":
        actions.append(
            {
                "area": "financial_performance",
                "priority": (
                    "high"
                    if severity in {
                        "high",
                        "critical",
                    }
                    else "medium"
                ),
                "action": (
                    "Review the drivers of the projected "
                    "net-result deterioration and identify "
                    "management responses."
                ),
            }
        )

    if cash_direction == "deteriorated":
        actions.append(
            {
                "area": "liquidity",
                "priority": (
                    "critical"
                    if severity == "critical"
                    else "high"
                ),
                "action": (
                    "Review expected cash inflows, committed "
                    "outflows, and discretionary spending to "
                    "protect available liquidity."
                ),
            }
        )

    if runway_direction == "deteriorated":
        actions.append(
            {
                "area": "cash_runway",
                "priority": (
                    "critical"
                    if severity == "critical"
                    else "high"
                ),
                "action": (
                    "Review the causes of the reduced cash "
                    "runway and assess funding, timing, or "
                    "cost-control responses."
                ),
            }
        )

    if not actions:
        actions.append(
            {
                "area": "monitoring",
                "priority": "low",
                "action": (
                    "Continue monitoring the scenario against "
                    "the validated baseline and update the "
                    "assessment when assumptions change."
                ),
            }
        )

    return actions


def _normalize_direction(
    value: Any,
) -> str:
    cleaned = (
        str(
            value or ""
        )
        .strip()
        .lower()
    )

    if cleaned in {
        "improved",
        "deteriorated",
        "unchanged",
    }:
        return cleaned

    return "unchanged"


def _direction_from_variance(
    value: float,
) -> str:
    if value > 0:
        return "improved"

    if value < 0:
        return "deteriorated"

    return "unchanged"


def _optional_float(
    value: Any,
) -> float | None:
    if value in {
        None,
        "",
    }:
        return None

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return None