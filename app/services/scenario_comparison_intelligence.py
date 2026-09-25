from typing import Any


SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

ATTENTION_RANK = {
    "monitor": 1,
    "review": 2,
    "priority_review": 3,
    "immediate": 4,
}


def generate_scenario_comparison_intelligence(
    scenario_a: dict[str, Any] | None,
    scenario_b: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Compare two existing deterministic scenario decision
    intelligence outputs without recalculating any financial
    values.

    This service must not:
    - modify either input;
    - rerun financial scenarios;
    - recalculate financial results;
    - infer missing cash impacts;
    - infer missing runway impacts.
    """

    scenario_a = scenario_a or {}
    scenario_b = scenario_b or {}

    if (
        scenario_a.get("status") != "available"
        or scenario_b.get("status") != "available"
    ):
        return {
            "status": "not_available",
            "scenario_a": scenario_a.get("scenario_name"),
            "scenario_b": scenario_b.get("scenario_name"),
            "preferred_scenario": None,
            "comparison_signal": "not_comparable",
            "reason": (
                "Two available deterministic scenario decision "
                "intelligence outputs are required for comparison."
            ),
            "controls": {
                "source_is_scenario_decision_intelligence": True,
                "financial_recalculation_performed": False,
                "missing_impacts_not_invented": True,
                "inputs_preserved": True,
            },
        }

    name_a = scenario_a.get("scenario_name")
    name_b = scenario_b.get("scenario_name")

    net_a = _optional_float(
        (
            scenario_a.get("net_result_impact", {})
            or {}
        ).get("variance")
    )

    net_b = _optional_float(
        (
            scenario_b.get("net_result_impact", {})
            or {}
        ).get("variance")
    )

    cash_a = _optional_float(
        (
            scenario_a.get("cash_impact", {})
            or {}
        ).get("variance")
    )

    cash_b = _optional_float(
        (
            scenario_b.get("cash_impact", {})
            or {}
        ).get("variance")
    )

    runway_a = _optional_float(
        (
            scenario_a.get("runway_impact", {})
            or {}
        ).get("change_months")
    )

    runway_b = _optional_float(
        (
            scenario_b.get("runway_impact", {})
            or {}
        ).get("change_months")
    )

    severity_a = _normalize_text(
        scenario_a.get("severity")
    )

    severity_b = _normalize_text(
        scenario_b.get("severity")
    )

    attention_a = _normalize_text(
        scenario_a.get("management_attention")
    )

    attention_b = _normalize_text(
        scenario_b.get("management_attention")
    )

    net_result_preference = _compare_numeric(
        value_a=net_a,
        value_b=net_b,
        name_a=name_a,
        name_b=name_b,
    )

    cash_available = (
        cash_a is not None
        and cash_b is not None
    )

    if cash_available:
        cash_preference = _compare_numeric(
            value_a=cash_a,
            value_b=cash_b,
            name_a=name_a,
            name_b=name_b,
        )
    else:
        cash_preference = None

    runway_available = (
        runway_a is not None
        and runway_b is not None
    )

    if runway_available:
        runway_preference = _compare_numeric(
            value_a=runway_a,
            value_b=runway_b,
            name_a=name_a,
            name_b=name_b,
        )
    else:
        runway_preference = None

    severity_preference = _compare_ranked(
        value_a=severity_a,
        value_b=severity_b,
        ranking=SEVERITY_RANK,
        name_a=name_a,
        name_b=name_b,
    )

    attention_preference = _compare_ranked(
        value_a=attention_a,
        value_b=attention_b,
        ranking=ATTENTION_RANK,
        name_a=name_a,
        name_b=name_b,
    )

    preferences = [
        preference
        for preference in [
            net_result_preference,
            cash_preference,
            runway_preference,
            severity_preference,
            attention_preference,
        ]
        if preference is not None
    ]

    distinct_preferences = {
        preference
        for preference in preferences
        if preference not in {
            "equal",
        }
    }

    if len(distinct_preferences) == 1:
        preferred_scenario = next(
            iter(distinct_preferences)
        )
        comparison_signal = "clear_preference"

    elif len(distinct_preferences) > 1:
        preferred_scenario = None
        comparison_signal = "mixed"

    else:
        preferred_scenario = None
        comparison_signal = "not_comparable"

    return {
        "status": "available",
        "scenario_a": {
            "scenario_name": name_a,
            "severity": severity_a,
            "management_attention": attention_a,
        },
        "scenario_b": {
            "scenario_name": name_b,
            "severity": severity_b,
            "management_attention": attention_b,
        },
        "preferred_scenario": preferred_scenario,
        "comparison_signal": comparison_signal,
        "net_result_comparison": {
            "available": (
                net_a is not None
                and net_b is not None
            ),
            "scenario_a_variance": net_a,
            "scenario_b_variance": net_b,
            "preferred_scenario": net_result_preference,
        },
        "cash_comparison": {
            "available": cash_available,
            "scenario_a_variance": cash_a,
            "scenario_b_variance": cash_b,
            "preferred_scenario": cash_preference,
        },
        "runway_comparison": {
            "available": runway_available,
            "scenario_a_change_months": runway_a,
            "scenario_b_change_months": runway_b,
            "preferred_scenario": runway_preference,
        },
        "severity_comparison": {
            "scenario_a": severity_a,
            "scenario_b": severity_b,
            "preferred_scenario": severity_preference,
        },
        "management_attention_comparison": {
            "scenario_a": attention_a,
            "scenario_b": attention_b,
            "preferred_scenario": attention_preference,
        },
        "controls": {
            "source_is_scenario_decision_intelligence": True,
            "financial_recalculation_performed": False,
            "missing_impacts_not_invented": True,
            "inputs_preserved": True,
        },
    }


def _compare_numeric(
    *,
    value_a: float | None,
    value_b: float | None,
    name_a: Any,
    name_b: Any,
) -> str | None:
    if (
        value_a is None
        or value_b is None
    ):
        return None

    if value_a > value_b:
        return str(name_a)

    if value_b > value_a:
        return str(name_b)

    return "equal"


def _compare_ranked(
    *,
    value_a: str,
    value_b: str,
    ranking: dict[str, int],
    name_a: Any,
    name_b: Any,
) -> str | None:
    rank_a = ranking.get(value_a)
    rank_b = ranking.get(value_b)

    if (
        rank_a is None
        or rank_b is None
    ):
        return None

    if rank_a < rank_b:
        return str(name_a)

    if rank_b < rank_a:
        return str(name_b)

    return "equal"


def _normalize_text(
    value: Any,
) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
    )


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