from pathlib import Path
from typing import Any

from app.services.cfo_action_plan import CFOActionPlanService


class CFOActionLifecycleService:
    """
    Deterministic management-action lifecycle for AI-FOS.

    This service provides controlled lifecycle operations over
    CFO Action Plan records.

    It does not persist action data directly. All mutations pass
    through CFOActionPlanService.update_action(), preserving the
    Action Plan as the single mutation boundary.

    Owners, due dates, progress, statuses, and management notes
    are explicit management-controlled information and must never
    be invented.
    """

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    @staticmethod
    def _require_action(
        *,
        financial_model_folder: Path,
        action_id: str,
    ) -> dict[str, Any]:
        action = CFOActionPlanService.get_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        if action is None:
            raise ValueError(
                f"CFO action not found: {action_id}"
            )

        return action

    @staticmethod
    def _update(
        *,
        financial_model_folder: Path,
        action_id: str,
        history_actor: str | None = None,
        history_source: str | None = None,
        **changes: Any,
    ) -> dict[str, Any]:
        updated = CFOActionPlanService.update_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            **changes,
        )

        if updated is None:
            raise ValueError(
                f"CFO action not found: {action_id}"
            )

        return updated

    @staticmethod
    def _status(
        action: dict[str, Any],
    ) -> str:
        return str(
            action.get("status", "open")
            or "open"
        ).strip().lower()

    # ==================================================
    # OWNER
    # ==================================================

    @staticmethod
    def assign_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        owner: Any,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Assign an explicit owner to an action.
        """

        CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        normalized_owner = (
            str(owner or "").strip()
        )

        if not normalized_owner:
            raise ValueError(
                "Action owner is required."
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            owner=normalized_owner,
        )

    @staticmethod
    def unassign_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Remove the current owner.
        """

        CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            owner=None,
        )

    # ==================================================
    # DUE DATE
    # ==================================================

    @staticmethod
    def set_due_date(
        *,
        financial_model_folder: Path,
        action_id: str,
        due_date: Any,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Set an explicit due date.
        """

        CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        if (
            due_date is None
            or not str(due_date).strip()
        ):
            raise ValueError(
                "Due date is required."
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            due_date=due_date,
        )

    @staticmethod
    def clear_due_date(
        *,
        financial_model_folder: Path,
        action_id: str,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Remove the current due date.
        """

        CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            due_date=None,
        )

    # ==================================================
    # START / PROGRESS
    # ==================================================

    @staticmethod
    def start_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Move an open action into progress.

        Cancelled or completed actions must be explicitly reopened
        before they can be started again.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status == "cancelled":
            raise ValueError(
                "Cancelled action must be reopened before it can be started."
            )

        if status == "completed":
            raise ValueError(
                "Completed action must be reopened before it can be started."
            )

        if status == "blocked":
            raise ValueError(
                "Blocked action must be unblocked before it can be started."
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            status="in_progress",
        )

    @staticmethod
    def update_progress(
        *,
        financial_model_folder: Path,
        action_id: str,
        progress_percentage: Any,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Update explicit management progress.

        Progress below 100 does not automatically change status.
        Progress of 100 does not automatically complete the action;
        completion must remain an explicit management decision.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status == "completed":
            raise ValueError(
                "Completed action must be reopened before progress can be changed."
            )

        if status == "cancelled":
            raise ValueError(
                "Cancelled action must be reopened before progress can be changed."
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            progress_percentage=progress_percentage,
        )

    # ==================================================
    # BLOCK / UNBLOCK
    # ==================================================

    @staticmethod
    def block_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        management_notes: Any = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Mark an active action as blocked.

        A blocking explanation is optional because the lifecycle
        must not invent a reason that management did not provide.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status == "completed":
            raise ValueError(
                "Completed action must be reopened before it can be blocked."
            )

        if status == "cancelled":
            raise ValueError(
                "Cancelled action must be reopened before it can be blocked."
            )

        changes: dict[str, Any] = {
            "status": "blocked",
        }

        if management_notes is not None:
            changes["management_notes"] = (
                management_notes
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            **changes,
        )

    @staticmethod
    def unblock_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Return a blocked action to in-progress status.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status != "blocked":
            raise ValueError(
                "Only a blocked action can be unblocked."
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            status="in_progress",
        )

    # ==================================================
    # COMPLETE / REOPEN / CANCEL
    # ==================================================

    @staticmethod
    def complete_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        management_notes: Any = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Explicitly complete an action.

        CFOActionPlanService owns the completion timestamp and
        automatically sets progress to 100.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status == "cancelled":
            raise ValueError(
                "Cancelled action must be reopened before it can be completed."
            )

        changes: dict[str, Any] = {
            "status": "completed",
        }

        if management_notes is not None:
            changes["management_notes"] = (
                management_notes
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            **changes,
        )

    @staticmethod
    def reopen_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Reopen a completed or cancelled action.

        Reopening returns the action to open status. The underlying
        Action Plan service clears completed_at when reopening a
        completed action.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status not in {
            "completed",
            "cancelled",
        }:
            raise ValueError(
                "Only a completed or cancelled action can be reopened."
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            status="open",
        )

    @staticmethod
    def cancel_action(
        *,
        financial_model_folder: Path,
        action_id: str,
        management_notes: Any = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Explicitly cancel an action.

        Completed actions must first be reopened so cancellation is
        an intentional management transition.
        """

        action = CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        status = CFOActionLifecycleService._status(
            action
        )

        if status == "completed":
            raise ValueError(
                "Completed action must be reopened before it can be cancelled."
            )

        changes: dict[str, Any] = {
            "status": "cancelled",
        }

        if management_notes is not None:
            changes["management_notes"] = (
                management_notes
            )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            **changes,
        )

    # ==================================================
    # NOTES
    # ==================================================

    @staticmethod
    def update_management_notes(
        *,
        financial_model_folder: Path,
        action_id: str,
        management_notes: Any,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        """
        Update management-controlled notes without changing
        financial or source-provenance information.
        """

        CFOActionLifecycleService._require_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
        )

        return CFOActionLifecycleService._update(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=history_actor,
            history_source=history_source,
            management_notes=management_notes,
        )