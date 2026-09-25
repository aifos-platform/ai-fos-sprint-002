from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.financial_model_service import (
    FinancialModelService,
)
from app.services.cfo_action_monitoring import (
    generate_cfo_action_monitoring,
)
from app.services.cfo_action_escalation import (
    generate_cfo_action_escalation,
)
from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_performance import (
    generate_cfo_action_performance,
)

_UNSET = object()


class CFOActionPlanService:
    """
    Persist and manage CFO management actions.

    CFO Action Plan records are operational management state.
    They remain separate from validated financial outputs,
    deterministic intelligence, and hypothetical scenarios.

    AI-FOS may propose an action, but owner, due date,
    progress, completion, and management notes are explicit
    management-controlled fields.
    """

    FILENAME = "cfo_action_plan.json"

    VALID_STATUSES = {
        "open",
        "in_progress",
        "blocked",
        "completed",
        "cancelled",
    }

    VALID_PRIORITIES = {
        "Critical",
        "High",
        "Medium",
        "Low",
    }

    # ==================================================
    # READ
    # ==================================================

    @staticmethod
    def list_actions(
        financial_model_folder: Path,
    ) -> list[dict[str, Any]]:
        """
        Return all persisted CFO Action Plan records.

        Missing or invalid files are treated as an empty
        action plan.
        """

        actions = FinancialModelService.load_json(
            financial_model_folder,
            CFOActionPlanService.FILENAME,
        )

        if not isinstance(
            actions,
            list,
        ):
            return []

        return [
            action
            for action in actions
            if isinstance(
                action,
                dict,
            )
        ]

    @staticmethod
    def get_action(
        *,
        financial_model_folder: Path,
        action_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve one CFO Action Plan record by ID.
        """

        actions = CFOActionPlanService.list_actions(
            financial_model_folder
        )

        for action in actions:
            if (
                action.get(
                    "action_id"
                )
                == action_id
            ):
                return action

        return None

    # ==================================================
    # CREATE
    # ==================================================

    @staticmethod
    def create_action(
        *,
        financial_model_folder: Path,
        title: str,
        description: str,
        priority: str = "Medium",
        category: str = "Financial Management",
        source_type: str | None = None,
        source_title: str | None = None,
        source_priority: str | None = None,
        owner: str | None = None,
        due_date: str | None = None,
        status: str = "open",
        progress_percentage: int | float = 0,
        management_notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Create and persist one CFO management action.

        Owner and due date are never invented by this service.
        """

        actions = CFOActionPlanService.list_actions(
            financial_model_folder
        )

        normalized_title = (
            str(title or "")
            .strip()
        )

        normalized_description = (
            str(description or "")
            .strip()
        )

        if not normalized_title:
            raise ValueError(
                "CFO action title is required."
            )

        if not normalized_description:
            raise ValueError(
                "CFO action description is required."
            )

        normalized_priority = (
            CFOActionPlanService._validate_priority(
                priority
            )
        )

        normalized_status = (
            CFOActionPlanService._validate_status(
                status
            )
        )

        normalized_progress = (
            CFOActionPlanService._validate_progress(
                progress_percentage
            )
        )

        normalized_due_date = (
            CFOActionPlanService._normalize_due_date(
                due_date
            )
        )

        now = CFOActionPlanService._utc_now()

        completed_at = None

        if normalized_status == "completed":
            normalized_progress = 100
            completed_at = now

        record = {
            "action_id": str(
                uuid4()
            ),
            "title": normalized_title,
            "description": normalized_description,
            "priority": normalized_priority,
            "category": (
                str(
                    category
                    or "Financial Management"
                ).strip()
                or "Financial Management"
            ),
            "source_type": (
                CFOActionPlanService._optional_text(
                    source_type
                )
            ),
            "source_title": (
                CFOActionPlanService._optional_text(
                    source_title
                )
            ),
            "source_priority": (
                CFOActionPlanService._optional_text(
                    source_priority
                )
            ),
            "owner": (
                CFOActionPlanService._optional_text(
                    owner
                )
            ),
            "due_date": normalized_due_date,
            "status": normalized_status,
            "progress_percentage": (
                normalized_progress
            ),
            "management_notes": (
                CFOActionPlanService._optional_text(
                    management_notes
                )
            ),
            "created_at": now,
            "updated_at": now,
            "completed_at": completed_at,
        }

        actions.append(
            record
        )

        CFOActionPlanService._save_actions(
            financial_model_folder=(
                financial_model_folder
            ),
            actions=actions,
        )

        CFOActionHistoryService.record_event(
            financial_model_folder=(
                financial_model_folder
            ),
            action_id=record["action_id"],
            event_type="action_created",
            new_value={
                "title": record.get("title"),
                "description": record.get(
                    "description"
                ),
                "priority": record.get(
                    "priority"
                ),
                "category": record.get(
                    "category"
                ),
                "source_type": record.get(
                    "source_type"
                ),
                "source_title": record.get(
                    "source_title"
                ),
                "source_priority": record.get(
                    "source_priority"
                ),
                "owner": record.get("owner"),
                "due_date": record.get(
                    "due_date"
                ),
                "status": record.get(
                    "status"
                ),
                "progress_percentage": (
                    record.get(
                        "progress_percentage"
                    )
                ),
                "management_notes": (
                    record.get(
                        "management_notes"
                    )
                ),
            },
            occurred_at=record["created_at"],
        )

        return record

    @staticmethod
    def create_from_executive_priority(
        *,
        financial_model_folder: Path,
        executive_priority: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert one verified Executive Decision Intelligence
        priority into a CFO Action Plan record.

        This operation preserves the verified priority and
        proposed management action but does not invent an owner,
        due date, progress, or management notes.
        """

        if not isinstance(
            executive_priority,
            dict,
        ):
            raise ValueError(
                "Executive priority must be a dictionary."
            )

        title = str(
            executive_priority.get(
                "title",
                "",
            )
            or ""
        ).strip()

        management_action = str(
            executive_priority.get(
                "management_action",
                "",
            )
            or ""
        ).strip()

        priority = str(
            executive_priority.get(
                "priority",
                "",
            )
            or ""
        ).strip()

        if not title:
            raise ValueError(
                "Executive priority title is required."
            )

        if not management_action:
            raise ValueError(
                "Executive priority management action is required."
            )

        if not priority:
            raise ValueError(
                "Executive priority level is required."
            )

        return CFOActionPlanService.create_action(
            financial_model_folder=(
                financial_model_folder
            ),
            title=title,
            description=management_action,
            priority=priority,
            category=str(
                executive_priority.get(
                    "category",
                    "Financial Management",
                )
                or "Financial Management"
            ),
            source_type=(
                "executive_decision_intelligence"
            ),
            source_title=title,
            source_priority=priority,
            owner=None,
            due_date=None,
            status="open",
            progress_percentage=0,
            management_notes=None,
        )

    # ==================================================
    # UPDATE
    # ==================================================

    @staticmethod
    def update_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        title: Any = _UNSET,
        description: Any = _UNSET,
        priority: Any = _UNSET,
        category: Any = _UNSET,
        owner: Any = _UNSET,
        due_date: Any = _UNSET,
        status: Any = _UNSET,
        progress_percentage: Any = _UNSET,
        management_notes: Any = _UNSET,
        history_actor: str | None = None,
        history_source: str | None = None,        
    ) -> dict[str, Any] | None:
        """
        Update management-controlled fields on one action.

        Source provenance and creation metadata remain immutable.

        All supplied values are validated before mutation.
        History events are appended only after the Action Plan
        update has been successfully persisted.
        """

        actions = CFOActionPlanService.list_actions(
            financial_model_folder
        )

        target = None

        for action in actions:
            if (
                action.get(
                    "action_id"
                )
                == action_id
            ):
                target = action
                break

        if target is None:
            return None

        # --------------------------------------------------
        # VALIDATE FIRST — DO NOT MUTATE YET
        # --------------------------------------------------

        proposed: dict[str, Any] = {}

        if title is not _UNSET:
            normalized_title = (
                str(title or "")
                .strip()
            )

            if not normalized_title:
                raise ValueError(
                    "CFO action title is required."
                )

            proposed["title"] = normalized_title

        if description is not _UNSET:
            normalized_description = (
                str(description or "")
                .strip()
            )

            if not normalized_description:
                raise ValueError(
                    "CFO action description is required."
                )

            proposed[
                "description"
            ] = normalized_description

        if priority is not _UNSET:
            proposed["priority"] = (
                CFOActionPlanService._validate_priority(
                    priority
                )
            )

        if category is not _UNSET:
            proposed["category"] = (
                str(
                    category
                    or "Financial Management"
                ).strip()
                or "Financial Management"
            )

        if owner is not _UNSET:
            proposed["owner"] = (
                CFOActionPlanService._optional_text(
                    owner
                )
            )

        if due_date is not _UNSET:
            proposed["due_date"] = (
                CFOActionPlanService._normalize_due_date(
                    due_date
                )
            )

        if management_notes is not _UNSET:
            proposed[
                "management_notes"
            ] = (
                CFOActionPlanService._optional_text(
                    management_notes
                )
            )

        if progress_percentage is not _UNSET:
            proposed[
                "progress_percentage"
            ] = (
                CFOActionPlanService._validate_progress(
                    progress_percentage
                )
            )

        if status is not _UNSET:
            proposed["status"] = (
                CFOActionPlanService._validate_status(
                    status
                )
            )

        # --------------------------------------------------
        # DETERMINE ACTUAL CHANGES
        # --------------------------------------------------

        previous_status = str(
            target.get(
                "status",
                "open",
            )
            or "open"
        )

        changes: list[
            tuple[
                str,
                Any,
                Any,
            ]
        ] = []

        for field, new_value in proposed.items():
            old_value = target.get(
                field
            )

            if old_value != new_value:
                changes.append(
                    (
                        field,
                        old_value,
                        new_value,
                    )
                )

        # --------------------------------------------------
        # APPLY VALIDATED CHANGES
        # --------------------------------------------------

        for (
            field,
            _old_value,
            new_value,
        ) in changes:
            target[field] = new_value

        normalized_status = (
            proposed.get(
                "status"
            )
            if "status" in proposed
            else None
        )

        if normalized_status == "completed":

            old_progress = target.get(
                "progress_percentage",
                0,
            )

            if old_progress != 100:
                changes.append(
                    (
                        "progress_percentage",
                        old_progress,
                        100,
                    )
                )

                target[
                    "progress_percentage"
                ] = 100

            if (
                previous_status
                != "completed"
                or not target.get(
                    "completed_at"
                )
            ):
                target[
                    "completed_at"
                ] = (
                    CFOActionPlanService._utc_now()
                )

        elif (
            normalized_status is not None
            and previous_status == "completed"
            and normalized_status != "completed"
        ):
            target[
                "completed_at"
            ] = None

        # --------------------------------------------------
        # NO-OP UPDATE
        # --------------------------------------------------

        if not changes:
            return target

        target[
            "updated_at"
        ] = CFOActionPlanService._utc_now()

        CFOActionPlanService._save_actions(
            financial_model_folder=(
                financial_model_folder
            ),
            actions=actions,
        )

        # --------------------------------------------------
        # APPEND HISTORY AFTER SUCCESSFUL PERSISTENCE
        # --------------------------------------------------

        event_type_by_field = {
            "title": "title_changed",
            "description": "description_changed",
            "priority": "priority_changed",
            "category": "category_changed",
            "owner": "owner_changed",
            "due_date": "due_date_changed",
            "status": "status_changed",
            "progress_percentage": "progress_changed",
            "management_notes": "management_notes_changed",
        }

        event_time = target[
            "updated_at"
        ]

        for (
            field,
            old_value,
            new_value,
        ) in changes:

            event_type = (
                event_type_by_field.get(
                    field
                )
            )

            if event_type is None:
                continue

            CFOActionHistoryService.record_event(
                financial_model_folder=(
                    financial_model_folder
                ),
                action_id=action_id,
                event_type=event_type,
                field=field,
                previous_value=old_value,
                new_value=new_value,
                actor=history_actor,
                source=history_source,
                occurred_at=event_time,
            )

        return target



    # ==================================================
    # MONITORING
    # ==================================================

    @staticmethod
    def build_monitoring(
        *,
        financial_model_folder: Path,
        reference_date: date | None = None,
        due_soon_days: int = 7,
    ) -> dict[str, Any]:
        """
        Build deterministic monitoring intelligence from the
        currently persisted CFO Action Plan.

        The persisted action records are read but not modified.
        """

        actions = CFOActionPlanService.list_actions(
            financial_model_folder
        )

        return generate_cfo_action_monitoring(
            actions,
            reference_date=reference_date,
            due_soon_days=due_soon_days,
        )

    @staticmethod
    def build_performance(
        *,
        financial_model_folder: Path,
    ) -> dict[str, Any]:
        """
        Build deterministic CFO Action Performance Intelligence
        from persisted immutable CFO Action History.

        This method is read-only. It does not modify Action Plan
        state or history records.
        """

        history_events = (
            CFOActionHistoryService.list_events(
                financial_model_folder
            )
        )

        return generate_cfo_action_performance(
            history_events
        )    

    @staticmethod
    def build_escalation(
        *,
        financial_model_folder: Path,
        reference_date: date | None = None,
        due_soon_days: int = 7,
    ) -> dict[str, Any]:
        """
        Build deterministic Management Follow-Up &
        Escalation Intelligence from persisted CFO actions.

        Monitoring owns overdue, due-soon, blocked, and
        unassigned classifications. Escalation interprets those
        monitoring signals without recalculating them.
        """

        monitoring = CFOActionPlanService.build_monitoring(
            financial_model_folder=financial_model_folder,
            reference_date=reference_date,
            due_soon_days=due_soon_days,
        )

        return generate_cfo_action_escalation(
            monitoring
        )    

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    @staticmethod
    def _save_actions(
        *,
        financial_model_folder: Path,
        actions: list[dict[str, Any]],
    ) -> None:

        FinancialModelService.save_json(
            financial_model_folder,
            CFOActionPlanService.FILENAME,
            actions,
        )

    @staticmethod
    def _validate_status(
        status: Any,
    ) -> str:

        normalized = (
            str(
                status
                or ""
            )
            .strip()
            .lower()
        )

        if (
            normalized
            not in CFOActionPlanService.VALID_STATUSES
        ):
            raise ValueError(
                "Invalid CFO action status. "
                "Expected one of: "
                + ", ".join(
                    sorted(
                        CFOActionPlanService.VALID_STATUSES
                    )
                )
                + "."
            )

        return normalized

    @staticmethod
    def _validate_priority(
        priority: Any,
    ) -> str:

        normalized = (
            str(
                priority
                or ""
            )
            .strip()
            .title()
        )

        if (
            normalized
            not in CFOActionPlanService.VALID_PRIORITIES
        ):
            raise ValueError(
                "Invalid CFO action priority. "
                "Expected Critical, High, Medium, or Low."
            )

        return normalized

    @staticmethod
    def _validate_progress(
        progress_percentage: Any,
    ) -> float:

        try:
            progress = float(
                progress_percentage
            )

        except (
            TypeError,
            ValueError,
        ):
            raise ValueError(
                "Progress percentage must be numeric."
            )

        if (
            progress < 0
            or progress > 100
        ):
            raise ValueError(
                "Progress percentage must be between 0 and 100."
            )

        return progress

    @staticmethod
    def _normalize_due_date(
        due_date: Any,
    ) -> str | None:

        if due_date is None:
            return None

        text = str(
            due_date
        ).strip()

        if not text:
            return None

        try:
            parsed = date.fromisoformat(
                text
            )

        except ValueError:
            raise ValueError(
                "Due date must use YYYY-MM-DD format."
            )

        return parsed.isoformat()

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
    def _utc_now() -> str:

        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )