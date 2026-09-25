from pathlib import Path
from typing import Any

from app.services.cfo_action_lifecycle import (
    CFOActionLifecycleService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


class CFOActionCommandService:
    """
    Deterministic command and action-resolution layer for
    CFO management actions.

    This service sits between user/Ask CFO commands and the
    CFO Action Lifecycle.

    Safety principles:
    - Never guess which action the user means.
    - Exactly one action must resolve before mutation.
    - Zero matches means zero mutation.
    - Multiple matches means zero mutation.
    - All mutations pass through CFOActionLifecycleService.
    - No owner, date, progress, status, or notes are invented.
    """

    # ==================================================
    # NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str:
        return " ".join(
            str(value or "")
            .strip()
            .lower()
            .split()
        )

    # ==================================================
    # ACTION RESOLUTION
    # ==================================================

    @staticmethod
    def resolve_action(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
    ) -> dict[str, Any]:
        """
        Resolve exactly one persisted CFO action.

        Resolution order:
        1. Explicit action_id.
        2. Exact normalized title match.
        3. Unique partial normalized title match.

        If resolution is not unique, no mutation is allowed.
        """

        actions = CFOActionPlanService.list_actions(
            financial_model_folder
        )

        # ----------------------------------------------
        # Explicit ID
        # ----------------------------------------------

        if action_id is not None:
            normalized_id = str(
                action_id
            ).strip()

            if not normalized_id:
                raise ValueError(
                    "Action ID cannot be empty."
                )

            matches = [
                action
                for action in actions
                if str(
                    action.get(
                        "action_id",
                        "",
                    )
                ).strip()
                == normalized_id
            ]

            if len(matches) == 1:
                return matches[0]

            raise ValueError(
                f"CFO action not found: {normalized_id}"
            )

        # ----------------------------------------------
        # Human-readable reference
        # ----------------------------------------------

        reference = (
            CFOActionCommandService._normalize_text(
                action_reference
            )
        )

        if not reference:
            raise ValueError(
                "Action reference is required."
            )

        exact_matches = [
            action
            for action in actions
            if (
                CFOActionCommandService._normalize_text(
                    action.get("title")
                )
                == reference
            )
        ]

        if len(exact_matches) == 1:
            return exact_matches[0]

        if len(exact_matches) > 1:
            raise ValueError(
                "Action reference is ambiguous. "
                "Multiple CFO actions have the same title."
            )

        partial_matches = [
            action
            for action in actions
            if (
                reference
                in CFOActionCommandService._normalize_text(
                    action.get("title")
                )
            )
        ]

        if len(partial_matches) == 1:
            return partial_matches[0]

        if len(partial_matches) > 1:
            raise ValueError(
                "Action reference is ambiguous. "
                "Multiple CFO actions match the reference."
            )

        raise ValueError(
            "No CFO action matches the reference."
        )

    # ==================================================
    # COMMAND TARGET
    # ==================================================

    @staticmethod
    def _resolve_action_id(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
    ) -> str:
        action = CFOActionCommandService.resolve_action(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            action_reference=action_reference,
        )

        resolved_id = str(
            action.get(
                "action_id",
                "",
            )
        ).strip()

        if not resolved_id:
            raise ValueError(
                "Resolved CFO action has no action ID."
            )

        return resolved_id

    # ==================================================
    # ASSIGNMENT
    # ==================================================

    @staticmethod
    def assign(
        *,
        financial_model_folder: Path,
        owner: Any,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.assign_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            owner=owner,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    def unassign(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.unassign_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            history_actor=history_actor,
            history_source=history_source,
        )

    # ==================================================
    # DUE DATE
    # ==================================================

    @staticmethod
    def set_due_date(
        *,
        financial_model_folder: Path,
        due_date: Any,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.set_due_date(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            due_date=due_date,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    def clear_due_date(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.clear_due_date(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            history_actor=history_actor,
            history_source=history_source,
        )

    # ==================================================
    # EXECUTION STATUS
    # ==================================================

    @staticmethod
    def start(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.start_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    def update_progress(
        *,
        financial_model_folder: Path,
        progress_percentage: Any,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.update_progress(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            progress_percentage=progress_percentage,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    @staticmethod
    def block(
        *,
        financial_model_folder: Path,
        management_notes: Any = None,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.block_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            management_notes=management_notes,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    def unblock(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.unblock_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            history_actor=history_actor,
            history_source=history_source,
        )

    # ==================================================
    # COMPLETE / REOPEN / CANCEL
    # ==================================================

    @staticmethod
    def complete(
        *,
        financial_model_folder: Path,
        management_notes: Any = None,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.complete_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            management_notes=management_notes,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    def reopen(
        *,
        financial_model_folder: Path,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.reopen_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            history_actor=history_actor,
            history_source=history_source,
        )

    @staticmethod
    def cancel(
        *,
        financial_model_folder: Path,
        management_notes: Any = None,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return CFOActionLifecycleService.cancel_action(
            financial_model_folder=financial_model_folder,
            action_id=resolved_id,
            management_notes=management_notes,
            history_actor=history_actor,
            history_source=history_source,
        )

    # ==================================================
    # NOTES
    # ==================================================

    @staticmethod
    def update_notes(
        *,
        financial_model_folder: Path,
        management_notes: Any,
        action_id: str | None = None,
        action_reference: str | None = None,
        history_actor: str | None = None,
        history_source: str | None = None,
    ) -> dict[str, Any]:
        resolved_id = (
            CFOActionCommandService._resolve_action_id(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                action_reference=action_reference,
            )
        )

        return (
            CFOActionLifecycleService.update_management_notes(
                financial_model_folder=financial_model_folder,
                action_id=resolved_id,
                management_notes=management_notes,
                history_actor=history_actor,
                history_source=history_source,
            )
        )