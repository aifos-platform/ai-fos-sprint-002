from typing import Any

from app.services.question_catalog import get_question_catalog


class SuggestedQuestionService:
    """
    Select the most relevant AI-FOS questions for an
    organization using persisted verified financial
    intelligence.

    The master question wording remains in
    question_catalog.py. This service only decides which
    questions should be promoted.
    """

    def __init__(self) -> None:
        self._question_lookup = self._build_question_lookup()

    @staticmethod
    def _build_question_lookup() -> dict[str, dict[str, Any]]:
        lookup: dict[str, dict[str, Any]] = {}

        for category in get_question_catalog():

            category_name = category.get("category")
            description = category.get("description")

            for question in category.get("questions", []):

                question_id = question.get("id")

                if not question_id:
                    continue

                lookup[question_id] = {
                    **question,
                    "category": category_name,
                    "category_description": description,
                }

        return lookup

    def get_suggested_questions(
        self,
        intelligence_hub: dict[str, Any] | None,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        """
        Return organization-specific suggested questions
        based only on persisted verified AI-FOS
        intelligence.
        """

        intelligence_hub = intelligence_hub or {}

        intelligence = (
            intelligence_hub.get(
                "intelligence",
                {},
            )
            or {}
        )

        facts = (
            intelligence_hub.get(
                "facts",
                {},
            )
            or {}
        )

        financial_health = (
            intelligence.get(
                "financial_health",
                {},
            )
            or {}
        )

        risks = (
            intelligence.get(
                "risk_assessment",
                [],
            )
            or []
        )

        recommendations = (
            intelligence.get(
                "cfo_recommendations",
                [],
            )
            or []
        )

        executive_dashboard = (
            intelligence.get(
                "executive_dashboard",
                {},
            )
            or {}
        )

        kpi_dashboard = (
            intelligence.get(
                "kpi_dashboard",
                {},
            )
            or {}
        )

        budget_dashboard = (
            facts.get(
                "budget_dashboard",
                {},
            )
            or {}
        )

        grant_diagnostics = (
            facts.get(
                "grant_diagnostics",
                {},
            )
            or {}
        )

        #
        # Funding intelligence is currently available
        # inside Financial Health and Executive Dashboard.
        #

        funding_summary = {}

        executive_funding_summary = (
            executive_dashboard.get(
                "funding_summary",
                {},
            )
            or {}
        )

        if executive_funding_summary:

            funding_summary = executive_funding_summary

        else:

            funding_health = (
                financial_health
                .get(
                    "categories",
                    {},
                )
                .get(
                    "funding_and_grant_health",
                    {},
                )
                or {}
            )

            funding_summary = (
                funding_health.get(
                    "metrics",
                    {},
                )
                or {}
            )

        candidates: list[dict[str, Any]] = []

        # =================================================
        # MANAGEMENT PRIORITIES
        # =================================================

        high_recommendations = [
            recommendation
            for recommendation in recommendations
            if str(
                recommendation.get(
                    "priority",
                    "",
                )
            ).lower()
            in {
                "critical",
                "high",
            }
        ]

        if high_recommendations:

            self._add(
                candidates=candidates,
                question_id="recommendation_001",
                priority=100,
                reason=(
                    "High-priority CFO recommendations "
                    "are available."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="recommendation_007",
                priority=94,
                reason=(
                    "Management has high-priority "
                    "financial actions to review."
                ),
            )

        # =================================================
        # FUNDING GAP
        # =================================================

        funding_gap_amount = self._to_float(
            funding_summary.get(
                "funding_gap"
            )
        )

        coverage_percentage = self._to_float(
            funding_summary.get(
                "applied_coverage_percentage"
            )
        )

        unmatched_count = self._to_int(
            funding_summary.get(
                "unmatched_requirement_count"
            )
        )

        if funding_gap_amount > 0:

            self._add(
                candidates=candidates,
                question_id="funding_001",
                priority=99,
                reason=(
                    "A material Funding Gap has been "
                    "identified."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="funding_008",
                priority=97,
                reason=(
                    "Management action is required on "
                    "the identified Funding Gap."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="funding_002",
                priority=95,
                reason=(
                    "Current validated funding does not "
                    "fully cover remaining requirements."
                ),
            )

        if (
            coverage_percentage > 0
            and coverage_percentage < 100
        ):

            self._add(
                candidates=candidates,
                question_id="funding_003",
                priority=93,
                reason=(
                    "Remaining requirements are only "
                    "partially covered by validated "
                    "secured funding."
                ),
            )

        if unmatched_count > 0:

            self._add(
                candidates=candidates,
                question_id="funding_007",
                priority=91,
                reason=(
                    "Some requirements do not currently "
                    "have validated eligible secured "
                    "funding."
                ),
            )

        # =================================================
        # FINANCIAL HEALTH
        # =================================================

        health_score = self._extract_health_score(
            financial_health
        )

        if (
            health_score is not None
            and health_score < 70
        ):

            self._add(
                candidates=candidates,
                question_id="financial_health_002",
                priority=98,
                reason=(
                    "The Financial Health Score requires "
                    "management attention."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="financial_health_003",
                priority=92,
                reason=(
                    "Financial-health weaknesses have "
                    "been identified."
                ),
            )

        # =================================================
        # RISKS
        # =================================================

        critical_or_high_risks = [
            risk
            for risk in risks
            if str(
                risk.get(
                    "severity",
                    "",
                )
            ).lower()
            in {
                "critical",
                "high",
            }
        ]

        if critical_or_high_risks:

            self._add(
                candidates=candidates,
                question_id="risk_002",
                priority=96,
                reason=(
                    "Critical or High-severity financial "
                    "risks are currently present."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="risk_003",
                priority=90,
                reason=(
                    "Management should identify which "
                    "financial risk requires the most "
                    "urgent attention."
                ),
            )

        # =================================================
        # OPERATING PERFORMANCE
        # =================================================

        net_result = self._to_float(
            kpi_dashboard.get(
                "net_result"
            )
        )

        if net_result < 0:

            self._add(
                candidates=candidates,
                question_id="performance_001",
                priority=89,
                reason=(
                    "The organization is currently "
                    "reporting a deficit."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="recommendation_003",
                priority=88,
                reason=(
                    "Management action may be required "
                    "to address the operating deficit."
                ),
            )

        # =================================================
        # BUDGET CONTROL
        # =================================================

        budget_utilization = self._to_float(
            kpi_dashboard.get(
                "budget_utilization"
            )
        )

        over_budget_lines = self._to_int(
            kpi_dashboard.get(
                "over_budget_lines"
            )
        )

        actuals_without_budget = self._to_int(
            kpi_dashboard.get(
                "actuals_without_budget_lines"
            )
        )

        if (
            over_budget_lines > 0
            or actuals_without_budget > 0
        ):

            self._add(
                candidates=candidates,
                question_id="budget_008",
                priority=87,
                reason=(
                    "Budget-control exceptions have "
                    "been identified."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="budget_006",
                priority=85,
                reason=(
                    "Some budget lines require "
                    "management attention."
                ),
            )

        elif budget_utilization > 90:

            self._add(
                candidates=candidates,
                question_id="budget_001",
                priority=80,
                reason=(
                    "Portfolio budget utilization is "
                    "relatively high."
                ),
            )

        # =================================================
        # LIQUIDITY
        # =================================================

        runway_months = self._to_float(
            kpi_dashboard.get(
                "cash_runway_months"
            )
        )

        if (
            runway_months > 0
            and runway_months < 9
        ):

            self._add(
                candidates=candidates,
                question_id="liquidity_003",
                priority=86,
                reason=(
                    "Cash runway requires closer "
                    "management attention."
                ),
            )

            self._add(
                candidates=candidates,
                question_id="liquidity_006",
                priority=83,
                reason=(
                    "Liquidity risk should be reviewed."
                ),
            )

        # =================================================
        # GRANT DIAGNOSTICS
        # =================================================

        actual_only = (
            grant_diagnostics.get(
                "actual_only_grants",
                [],
            )
            or []
        )

        if actual_only:

            self._add(
                candidates=candidates,
                question_id="grant_005",
                priority=84,
                reason=(
                    "Some grants have actual activity "
                    "without corresponding budget data."
                ),
            )

        budget_only = (
            grant_diagnostics.get(
                "budget_only_grants",
                [],
            )
            or []
        )

        if budget_only:

            self._add(
                candidates=candidates,
                question_id="grant_006",
                priority=82,
                reason=(
                    "Some grants have budget data "
                    "without actual activity."
                ),
            )

        # =================================================
        # FALLBACK
        # =================================================

        fallback_ids = [
            "financial_health_001",
            "liquidity_003",
            "budget_001",
            "performance_001",
            "risk_001",
            "recommendation_001",
            "funding_001",
            "grant_008",
        ]

        for index, question_id in enumerate(
            fallback_ids
        ):

            self._add(
                candidates=candidates,
                question_id=question_id,
                priority=50 - index,
                reason=(
                    "General financial-management "
                    "question."
                ),
            )

        candidates.sort(
            key=lambda item: item[
                "priority"
            ],
            reverse=True,
        )

        unique: list[
            dict[str, Any]
        ] = []

        seen: set[str] = set()

        for candidate in candidates:

            question_id = candidate[
                "id"
            ]

            if question_id in seen:
                continue

            seen.add(
                question_id
            )

            unique.append(
                candidate
            )

            if len(unique) >= limit:
                break

        return unique

    def _add(
        self,
        candidates: list[dict[str, Any]],
        question_id: str,
        priority: int,
        reason: str,
    ) -> None:

        question = self._question_lookup.get(
            question_id
        )

        if not question:
            return

        candidates.append(
            {
                "id": question[
                    "id"
                ],
                "question": question[
                    "question"
                ],
                "category": question[
                    "category"
                ],
                "priority": priority,
                "reason": reason,
            }
        )

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float:

        if value is None:
            return 0.0

        if isinstance(
            value,
            (int, float),
        ):
            return float(
                value
            )

        text = (
            str(
                value
            )
            .replace(
                ",",
                "",
            )
            .replace(
                "$",
                "",
            )
            .strip()
        )

        if not text:
            return 0.0

        if (
            text.startswith("(")
            and text.endswith(")")
        ):
            text = (
                "-"
                + text[
                    1:-1
                ]
            )

        try:
            return float(
                text
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int:

        try:
            return int(
                value or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _extract_health_score(
        financial_health: dict[str, Any],
    ) -> float | None:

        possible_keys = (
            "overall_score",
            "score",
            "financial_health_score",
        )

        for key in possible_keys:

            if key not in financial_health:
                continue

            try:
                return float(
                    financial_health[
                        key
                    ]
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

        return None