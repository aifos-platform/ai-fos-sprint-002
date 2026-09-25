from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.financial_model_service import (
    FinancialModelService,
)
from app.services.financial_intelligence_change import (
    generate_unified_financial_intelligence_change,
)
from app.services.historical_decision_intelligence import (
    generate_historical_decision_intelligence,
)


class FinancialIntelligenceHistoryService:
    """
    Immutable history of completed verified AI-FOS
    financial intelligence states.

    This service stores point-in-time snapshots of already
    calculated and validated AI-FOS outputs.

    It does not:
    - recalculate financial intelligence,
    - modify current financial outputs,
    - modify historical snapshots,
    - include hypothetical scenario outputs,
    - include mutable CFO Action Plan state,
    - invent missing financial evidence.
    """

    FILENAME = "financial_intelligence_history.json"

    # ==================================================
    # READ
    # ==================================================

    @staticmethod
    def list_snapshots(
        financial_model_folder: Path,
    ) -> list[dict[str, Any]]:
        """
        Return all persisted financial intelligence snapshots.

        Missing or invalid persistence is treated as empty history.
        """

        snapshots = FinancialModelService.load_json(
            financial_model_folder,
            FinancialIntelligenceHistoryService.FILENAME,
        )

        if not isinstance(
            snapshots,
            list,
        ):
            return []

        return [
            snapshot
            for snapshot in snapshots
            if isinstance(
                snapshot,
                dict,
            )
        ]

    @staticmethod
    def get_snapshot(
        *,
        financial_model_folder: Path,
        snapshot_id: str,
    ) -> dict[str, Any] | None:
        """
        Return one immutable snapshot by ID.
        """

        normalized_snapshot_id = str(
            snapshot_id
            or ""
        ).strip()

        if not normalized_snapshot_id:
            raise ValueError(
                "Snapshot ID is required."
            )

        for snapshot in (
            FinancialIntelligenceHistoryService.list_snapshots(
                financial_model_folder
            )
        ):
            if (
                str(
                    snapshot.get(
                        "snapshot_id",
                        "",
                    )
                    or ""
                ).strip()
                == normalized_snapshot_id
            ):
                return snapshot

        return None

    @staticmethod
    def compare_snapshots(
        *,
        financial_model_folder: Path,
        snapshot_a_id: str,
        snapshot_b_id: str,
    ) -> dict[str, Any]:
        """
        Compare two persisted immutable Financial Intelligence
        History snapshots.

        snapshot_a is treated as the earlier/base state.
        snapshot_b is treated as the later/comparison state.

        This method retrieves persisted snapshots and delegates
        deterministic interpretation to Change Analysis.
        """

        normalized_snapshot_a_id = str(
            snapshot_a_id
            or ""
        ).strip()

        normalized_snapshot_b_id = str(
            snapshot_b_id
            or ""
        ).strip()

        if not normalized_snapshot_a_id:
            raise ValueError(
                "Snapshot A ID is required."
            )

        if not normalized_snapshot_b_id:
            raise ValueError(
                "Snapshot B ID is required."
            )

        if (
            normalized_snapshot_a_id
            == normalized_snapshot_b_id
        ):
            raise ValueError(
                "Two different snapshot IDs are required."
            )

        snapshot_a = (
            FinancialIntelligenceHistoryService.get_snapshot(
                financial_model_folder=financial_model_folder,
                snapshot_id=normalized_snapshot_a_id,
            )
        )

        if snapshot_a is None:
            raise ValueError(
                "Snapshot A was not found."
            )

        snapshot_b = (
            FinancialIntelligenceHistoryService.get_snapshot(
                financial_model_folder=financial_model_folder,
                snapshot_id=normalized_snapshot_b_id,
            )
        )

        if snapshot_b is None:
            raise ValueError(
                "Snapshot B was not found."
            )

        return (
            generate_unified_financial_intelligence_change(
                snapshot_a,
                snapshot_b,
            )
        )

    @staticmethod
    def compare_latest(
        financial_model_folder: Path,
    ) -> dict[str, Any]:
        """
        Compare the two most recently persisted Financial
        Intelligence History snapshots.

        Persisted append order is preserved:
        - second-last snapshot = earlier/base state;
        - last snapshot = latest/comparison state.
        """

        snapshots = (
            FinancialIntelligenceHistoryService.list_snapshots(
                financial_model_folder
            )
        )

        if len(snapshots) < 2:
            return {
                "status": "insufficient_history",
                "snapshot_count": len(
                    snapshots
                ),
                "reason": (
                    "At least two Financial Intelligence "
                    "History snapshots are required for "
                    "historical comparison."
                ),
                "controls": {
                    "deterministic": True,
                    "read_only": True,
                    "financial_recalculation_performed": False,
                    "historical_snapshots_modified": False,
                    "missing_history_not_invented": True,
                },
            }

        snapshot_a = snapshots[-2]
        snapshot_b = snapshots[-1]

        return (
            generate_unified_financial_intelligence_change(
                snapshot_a,
                snapshot_b,
            )
        )

    @staticmethod
    def build_latest_historical_decision(
        financial_model_folder: Path,
    ) -> dict[str, Any]:

        historical_change = (
            FinancialIntelligenceHistoryService.compare_latest(
                financial_model_folder
            )
        )

        return (
            generate_historical_decision_intelligence(
                historical_change
            )
        )

    # ==================================================
    # RECORD
    # ==================================================

    @staticmethod
    def record_snapshot(
        *,
        financial_model_folder: Path,
        financial_health: Any = None,
        liquidity: Any = None,
        financial_facts: Any = None,
        budget_dashboard: Any = None,
        funding_gap: Any = None,
        grant_diagnostics: Any = None,
        expected_funding_intelligence: Any = None,
        financial_trends: Any = None,
        financial_forecast: Any = None,
        risk_assessment: Any = None,
        forward_risks: Any = None,
        financial_opportunities: Any = None,
        cfo_recommendations: Any = None,
        executive_decision_intelligence: Any = None,
        analysis_start_date: Any = None,
        analysis_end_date: Any = None,
        source: str | None = "financial_processing",
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        """
        Append one immutable snapshot of verified AI-FOS intelligence.

        Inputs are copied exactly from already-generated verified
        outputs. No financial calculation is performed here.
        """

        event_time = (
            FinancialIntelligenceHistoryService._normalize_timestamp(
                captured_at
            )
            if captured_at is not None
            else FinancialIntelligenceHistoryService._utc_now()
        )

        snapshot = {
            "snapshot_id": str(
                uuid4()
            ),
            "captured_at": event_time,
            "source": (
                FinancialIntelligenceHistoryService._optional_text(
                    source
                )
            ),
            "analysis_period": {
                "start_date": (
                    FinancialIntelligenceHistoryService._optional_date_text(
                        analysis_start_date
                    )
                ),
                "end_date": (
                    FinancialIntelligenceHistoryService._optional_date_text(
                        analysis_end_date
                    )
                ),
            },
            "financial_intelligence": {
                "financial_health": deepcopy(
                    financial_health
                ),
                "liquidity": deepcopy(
                    liquidity
                ),
                "financial_facts": deepcopy(
                    financial_facts
                ),
                "budget_dashboard": deepcopy(
                    budget_dashboard
                ),
                "funding_gap": deepcopy(
                    funding_gap
                ),
                "grant_diagnostics": deepcopy(
                    grant_diagnostics
                ),
                "expected_funding_intelligence": deepcopy(
                    expected_funding_intelligence
                ),
                "financial_trends": deepcopy(
                    financial_trends
                ),
                "financial_forecast": deepcopy(
                    financial_forecast
                ),
                "risk_assessment": deepcopy(
                    risk_assessment
                ),
                "forward_risks": deepcopy(
                    forward_risks
                ),
                "financial_opportunities": deepcopy(
                    financial_opportunities
                ),
                "cfo_recommendations": deepcopy(
                    cfo_recommendations
                ),
                "executive_decision_intelligence": deepcopy(
                    executive_decision_intelligence
                ),
            },
            "controls": {
                "deterministic": True,
                "read_only_history": True,
                "financial_recalculation_performed": False,
                "validated_outputs_preserved": True,
                "hypothetical_scenarios_excluded": True,
                "action_plan_state_excluded": True,
                "missing_evidence_not_invented": True,
                "historical_snapshot_mutation_supported": False,
            },
        }

        snapshots = (
            FinancialIntelligenceHistoryService.list_snapshots(
                financial_model_folder
            )
        )

        snapshots.append(
            snapshot
        )

        FinancialModelService.save_json(
            financial_model_folder,
            FinancialIntelligenceHistoryService.FILENAME,
            snapshots,
        )

        return snapshot

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _optional_text(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        text = str(
            value
        ).strip()

        return (
            text
            if text
            else None
        )

    @staticmethod
    def _optional_date_text(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value.date().isoformat()

        text = str(
            value
        ).strip()

        return (
            text
            if text
            else None
        )

    @staticmethod
    def _normalize_timestamp(
        value: Any,
    ) -> str:

        text = str(
            value
            or ""
        ).strip()

        if not text:
            raise ValueError(
                "Snapshot timestamp is required."
            )

        try:
            parsed = datetime.fromisoformat(
                text
            )

        except ValueError as exc:
            raise ValueError(
                "Snapshot timestamp must be ISO format."
            ) from exc

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.isoformat()

    @staticmethod
    def _utc_now() -> str:

        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )