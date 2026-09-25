from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.financial_model_service import (
    FinancialModelService,
)


class CFOActionHistoryService:
    """
    Append-only audit trail for CFO Action Plan activity.

    The Action Plan remains the source of current management state.

    This history service preserves immutable events describing
    how management-controlled action state changed over time.

    It does not:
    - modify CFO Action Plan records,
    - modify financial outputs,
    - recalculate financial intelligence,
    - invent owners, dates, progress, statuses, or actors.
    """

    FILENAME = "cfo_action_history.json"

    VALID_EVENT_TYPES = {
        "action_created",
        "title_changed",
        "description_changed",
        "priority_changed",
        "category_changed",
        "owner_changed",
        "due_date_changed",
        "status_changed",
        "progress_changed",
        "management_notes_changed",
    }

    # ==================================================
    # READ
    # ==================================================

    @staticmethod
    def list_events(
        financial_model_folder: Path,
    ) -> list[dict[str, Any]]:
        """
        Return all persisted CFO Action history events.

        Missing or invalid files are treated as an empty history.
        """

        events = FinancialModelService.load_json(
            financial_model_folder,
            CFOActionHistoryService.FILENAME,
        )

        if not isinstance(
            events,
            list,
        ):
            return []

        return [
            event
            for event in events
            if isinstance(
                event,
                dict,
            )
        ]

    @staticmethod
    def list_action_events(
        *,
        financial_model_folder: Path,
        action_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return history for one CFO action in chronological order.
        """

        normalized_action_id = str(
            action_id
            or ""
        ).strip()

        if not normalized_action_id:
            raise ValueError(
                "Action ID is required."
            )

        events = CFOActionHistoryService.list_events(
            financial_model_folder
        )

        action_events = [
            event
            for event in events
            if str(
                event.get(
                    "action_id",
                    "",
                )
                or ""
            ).strip()
            == normalized_action_id
        ]

        return sorted(
            action_events,
            key=lambda event: (
                str(
                    event.get(
                        "occurred_at",
                        "",
                    )
                    or ""
                ),
                str(
                    event.get(
                        "event_id",
                        "",
                    )
                    or ""
                ),
            ),
        )

    # ==================================================
    # APPEND
    # ==================================================

    @staticmethod
    def record_event(
        *,
        financial_model_folder: Path,
        action_id: str,
        event_type: str,
        field: str | None = None,
        previous_value: Any = None,
        new_value: Any = None,
        actor: str | None = None,
        source: str | None = None,
        metadata: dict[str, Any] | None = None,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        """
        Append one immutable CFO Action audit event.

        Existing events are never updated by this service.
        """

        normalized_action_id = str(
            action_id
            or ""
        ).strip()

        if not normalized_action_id:
            raise ValueError(
                "Action ID is required."
            )

        normalized_event_type = str(
            event_type
            or ""
        ).strip().lower()

        if (
            normalized_event_type
            not in CFOActionHistoryService.VALID_EVENT_TYPES
        ):
            raise ValueError(
                "Invalid CFO action history event type."
            )

        normalized_field = (
            CFOActionHistoryService._optional_text(
                field
            )
        )

        normalized_actor = (
            CFOActionHistoryService._optional_text(
                actor
            )
        )

        normalized_source = (
            CFOActionHistoryService._optional_text(
                source
            )
        )        

        normalized_metadata = (
            dict(metadata)
            if isinstance(
                metadata,
                dict,
            )
            else {}
        )

        event_time = (
            CFOActionHistoryService._normalize_timestamp(
                occurred_at
            )
            if occurred_at is not None
            else CFOActionHistoryService._utc_now()
        )

        event = {
            "event_id": str(
                uuid4()
            ),
            "action_id": normalized_action_id,
            "event_type": normalized_event_type,
            "field": normalized_field,
            "previous_value": previous_value,
            "new_value": new_value,
            "actor": normalized_actor,
            "source": normalized_source,
            "metadata": normalized_metadata,
            "occurred_at": event_time,
        }

        events = CFOActionHistoryService.list_events(
            financial_model_folder
        )

        events.append(
            event
        )

        CFOActionHistoryService._save_events(
            financial_model_folder=financial_model_folder,
            events=events,
        )

        return event

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    @staticmethod
    def _save_events(
        *,
        financial_model_folder: Path,
        events: list[dict[str, Any]],
    ) -> None:

        FinancialModelService.save_json(
            financial_model_folder,
            CFOActionHistoryService.FILENAME,
            events,
        )

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
    def _normalize_timestamp(
        value: Any,
    ) -> str:

        text = str(
            value
            or ""
        ).strip()

        if not text:
            raise ValueError(
                "History event timestamp is required."
            )

        try:
            parsed = datetime.fromisoformat(
                text
            )

        except ValueError as exc:
            raise ValueError(
                "History event timestamp must be ISO format."
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