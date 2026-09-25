from typing import Any


def generate_cfo_action_performance(
    history_events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """
    Build deterministic CFO Action Performance Intelligence
    from immutable CFO Action History events.

    This service interprets historical management execution
    patterns only.

    It does not:
    - modify CFO Action Plan state,
    - modify CFO Action History,
    - recalculate financial intelligence,
    - infer current action status from incomplete history,
    - invent actors, owners, due dates, or sources.
    """

    events = [
        event
        for event in (
            history_events
            or []
        )
        if isinstance(
            event,
            dict,
        )
    ]

    # ==================================================
    # EMPTY HISTORY
    # ==================================================

    if not events:
        return {
            "status": "available",
            "summary": {
                "total_events": 0,
                "action_count": 0,
                "completed_action_count": 0,
                "reopened_action_count": 0,
                "blocked_action_count": 0,
                "actions_with_repeated_blocks": 0,
                "actions_with_multiple_owner_changes": 0,
                "actions_with_multiple_due_date_changes": 0,
                "completion_reopen_rate_percentage": 0.0,
            },
            "event_counts": {},
            "source_activity": {
                "known_sources": {},
                "unknown_source_events": 0,
            },
            "actor_activity": {
                "known_actors": {},
                "unknown_actor_events": 0,
            },
            "action_performance": [],
            "management_patterns": [],
            "controls": {
                "deterministic": True,
                "read_only": True,
                "action_records_modified": False,
                "history_records_modified": False,
                "financial_recalculation_performed": False,
                "current_action_state_not_inferred": True,
                "missing_actor_not_invented": True,
                "missing_source_not_invented": True,
            },
        }

    # ==================================================
    # EVENT COUNTS
    # ==================================================

    event_counts: dict[str, int] = {}

    source_counts: dict[str, int] = {}
    actor_counts: dict[str, int] = {}

    unknown_source_events = 0
    unknown_actor_events = 0

    action_records: dict[
        str,
        dict[str, Any],
    ] = {}

    for event in events:

        action_id = str(
            event.get(
                "action_id",
                "",
            )
            or ""
        ).strip()

        if not action_id:
            # Invalid historical rows are ignored rather
            # than interpreted or repaired.
            continue

        event_type = str(
            event.get(
                "event_type",
                "",
            )
            or ""
        ).strip().lower()

        if event_type:
            event_counts[event_type] = (
                event_counts.get(
                    event_type,
                    0,
                )
                + 1
            )

        source = _optional_text(
            event.get(
                "source"
            )
        )

        if source is None:
            unknown_source_events += 1

        else:
            source_counts[source] = (
                source_counts.get(
                    source,
                    0,
                )
                + 1
            )

        actor = _optional_text(
            event.get(
                "actor"
            )
        )

        if actor is None:
            unknown_actor_events += 1

        else:
            actor_counts[actor] = (
                actor_counts.get(
                    actor,
                    0,
                )
                + 1
            )

        if action_id not in action_records:
            action_records[action_id] = {
                "action_id": action_id,
                "event_count": 0,
                "created_event_count": 0,
                "owner_change_count": 0,
                "due_date_change_count": 0,
                "progress_update_count": 0,
                "block_count": 0,
                "completion_count": 0,
                "reopen_count": 0,
                "cancellation_count": 0,
                "last_event_at": None,
            }

        record = action_records[
            action_id
        ]

        record["event_count"] += 1

        occurred_at = _optional_text(
            event.get(
                "occurred_at"
            )
        )

        if (
            occurred_at
            and (
                record["last_event_at"] is None
                or occurred_at
                > record["last_event_at"]
            )
        ):
            record["last_event_at"] = (
                occurred_at
            )

        if event_type == "action_created":
            record[
                "created_event_count"
            ] += 1

        elif event_type == "owner_changed":
            record[
                "owner_change_count"
            ] += 1

        elif event_type == "due_date_changed":
            record[
                "due_date_change_count"
            ] += 1

        elif event_type == "progress_changed":
            record[
                "progress_update_count"
            ] += 1

        elif event_type == "status_changed":

            previous_status = (
                _normalize_status(
                    event.get(
                        "previous_value"
                    )
                )
            )

            new_status = (
                _normalize_status(
                    event.get(
                        "new_value"
                    )
                )
            )

            if new_status == "blocked":
                record[
                    "block_count"
                ] += 1

            if new_status == "completed":
                record[
                    "completion_count"
                ] += 1

            if (
                previous_status
                == "completed"
                and new_status
                == "open"
            ):
                record[
                    "reopen_count"
                ] += 1

            if new_status == "cancelled":
                record[
                    "cancellation_count"
                ] += 1

    # ==================================================
    # ACTION-LEVEL PERFORMANCE
    # ==================================================

    action_performance = list(
        action_records.values()
    )

    action_performance.sort(
        key=lambda record: (
            -int(
                record.get(
                    "reopen_count",
                    0,
                )
            ),
            -int(
                record.get(
                    "block_count",
                    0,
                )
            ),
            -int(
                record.get(
                    "due_date_change_count",
                    0,
                )
            ),
            -int(
                record.get(
                    "owner_change_count",
                    0,
                )
            ),
            str(
                record.get(
                    "action_id",
                    "",
                )
            ),
        )
    )

    completed_action_ids = {
        record["action_id"]
        for record in action_performance
        if (
            record[
                "completion_count"
            ]
            > 0
        )
    }

    reopened_action_ids = {
        record["action_id"]
        for record in action_performance
        if (
            record[
                "reopen_count"
            ]
            > 0
        )
    }

    blocked_action_ids = {
        record["action_id"]
        for record in action_performance
        if (
            record[
                "block_count"
            ]
            > 0
        )
    }

    repeated_block_ids = {
        record["action_id"]
        for record in action_performance
        if (
            record[
                "block_count"
            ]
            > 1
        )
    }

    multiple_owner_change_ids = {
        record["action_id"]
        for record in action_performance
        if (
            record[
                "owner_change_count"
            ]
            > 1
        )
    }

    multiple_due_date_change_ids = {
        record["action_id"]
        for record in action_performance
        if (
            record[
                "due_date_change_count"
            ]
            > 1
        )
    }

    completion_reopen_rate = (
        (
            len(
                reopened_action_ids
            )
            / len(
                completed_action_ids
            )
        )
        * 100.0
        if completed_action_ids
        else 0.0
    )

    # ==================================================
    # MANAGEMENT PATTERNS
    # ==================================================

    management_patterns: list[
        dict[str, Any]
    ] = []

    for record in action_performance:

        action_id = record[
            "action_id"
        ]

        reopen_count = int(
            record[
                "reopen_count"
            ]
        )

        block_count = int(
            record[
                "block_count"
            ]
        )

        owner_change_count = int(
            record[
                "owner_change_count"
            ]
        )

        due_date_change_count = int(
            record[
                "due_date_change_count"
            ]
        )

        if reopen_count > 0:
            management_patterns.append(
                {
                    "action_id": action_id,
                    "pattern": (
                        "action_reopened"
                    ),
                    "severity": (
                        "High"
                        if reopen_count > 1
                        else "Medium"
                    ),
                    "count": reopen_count,
                    "interpretation": (
                        "This action was reopened after "
                        "a recorded completion."
                    ),
                }
            )

        if block_count > 1:
            management_patterns.append(
                {
                    "action_id": action_id,
                    "pattern": (
                        "repeated_blocking"
                    ),
                    "severity": "High",
                    "count": block_count,
                    "interpretation": (
                        "This action entered blocked "
                        "status more than once."
                    ),
                }
            )

        if due_date_change_count > 1:
            management_patterns.append(
                {
                    "action_id": action_id,
                    "pattern": (
                        "repeated_due_date_changes"
                    ),
                    "severity": "Medium",
                    "count": (
                        due_date_change_count
                    ),
                    "interpretation": (
                        "This action has multiple "
                        "recorded due-date changes."
                    ),
                }
            )

        if owner_change_count > 1:
            management_patterns.append(
                {
                    "action_id": action_id,
                    "pattern": (
                        "repeated_owner_changes"
                    ),
                    "severity": "Medium",
                    "count": (
                        owner_change_count
                    ),
                    "interpretation": (
                        "This action has multiple "
                        "recorded ownership changes."
                    ),
                }
            )

    severity_order = {
        "High": 2,
        "Medium": 1,
        "Low": 0,
    }

    management_patterns.sort(
        key=lambda item: (
            -severity_order.get(
                str(
                    item.get(
                        "severity",
                        "Low",
                    )
                ),
                0,
            ),
            -int(
                item.get(
                    "count",
                    0,
                )
            ),
            str(
                item.get(
                    "action_id",
                    "",
                )
            ),
            str(
                item.get(
                    "pattern",
                    "",
                )
            ),
        )
    )

    # ==================================================
    # RESULT
    # ==================================================

    return {
        "status": "available",
        "summary": {
            "total_events": len(
                events
            ),
            "action_count": len(
                action_records
            ),
            "completed_action_count": len(
                completed_action_ids
            ),
            "reopened_action_count": len(
                reopened_action_ids
            ),
            "blocked_action_count": len(
                blocked_action_ids
            ),
            "actions_with_repeated_blocks": len(
                repeated_block_ids
            ),
            "actions_with_multiple_owner_changes": len(
                multiple_owner_change_ids
            ),
            "actions_with_multiple_due_date_changes": len(
                multiple_due_date_change_ids
            ),
            "completion_reopen_rate_percentage": round(
                completion_reopen_rate,
                2,
            ),
        },
        "event_counts": dict(
            sorted(
                event_counts.items()
            )
        ),
        "source_activity": {
            "known_sources": dict(
                sorted(
                    source_counts.items()
                )
            ),
            "unknown_source_events": (
                unknown_source_events
            ),
        },
        "actor_activity": {
            "known_actors": dict(
                sorted(
                    actor_counts.items()
                )
            ),
            "unknown_actor_events": (
                unknown_actor_events
            ),
        },
        "action_performance": (
            action_performance
        ),
        "management_patterns": (
            management_patterns
        ),
        "controls": {
            "deterministic": True,
            "read_only": True,
            "action_records_modified": False,
            "history_records_modified": False,
            "financial_recalculation_performed": False,
            "current_action_state_not_inferred": True,
            "missing_actor_not_invented": True,
            "missing_source_not_invented": True,
        },
    }


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


def _normalize_status(
    value: Any,
) -> str | None:

    text = _optional_text(
        value
    )

    if text is None:
        return None

    return (
        text
        .lower()
        .replace(
            " ",
            "_",
        )
    )