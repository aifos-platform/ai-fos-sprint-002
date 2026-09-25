from typing import Any

from app.services.digital_cfo_orchestrator import (
    DigitalCFOOrchestrator,
)


# ==================================================
# STUBS
# ==================================================


class _AIQuestionEngine:
    def __init__(
        self,
        result: dict[str, Any],
    ) -> None:
        self.result = result
        self.calls = 0

    def answer(
        self,
        *,
        question: str,
        organisation_id: str,
    ) -> dict[str, Any]:
        self.calls += 1
        return dict(self.result)


class _ScopeGuard:
    def evaluate(
        self,
        *,
        question: str,
    ) -> dict[str, Any]:
        return {
            "allowed": True,
            "reason": "in_scope",
        }


class _Provider:
    pass


class _UsageControl:
    def __init__(
        self,
    ) -> None:
        self.calls: list[dict[str, Any]] = []

    def authorize(
        self,
        *,
        organisation_id: str,
        request_type: str,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "organisation_id": organisation_id,
                "request_type": request_type,
            }
        )

        return {
            "allowed": True,
            "reason": "allowed",
            "max_output_tokens": None,
        }


class _ContextBuilder:
    def __init__(
        self,
    ) -> None:
        self.calls = 0

    def build(
        self,
        *,
        organisation_id: str,
    ) -> dict[str, Any]:
        self.calls += 1

        return {
            "status": "available",
            "context": {
                "financial_health": {
                    "score": 80,
                }
            },
            "available_sections": [
                "financial_health",
            ],
            "missing_sections": [],
            "source_files": {
                "financial_health": (
                    "financial_health.json"
                ),
            },
            "trust": {
                "verified": True,
            },
        }


def _build_orchestrator(
    *,
    verified_result: dict[str, Any],
) -> tuple[
    DigitalCFOOrchestrator,
    _AIQuestionEngine,
    _UsageControl,
    _ContextBuilder,
]:
    ai_question_engine = _AIQuestionEngine(
        verified_result
    )

    usage_control = _UsageControl()
    context_builder = _ContextBuilder()

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=ai_question_engine,
        provider=_Provider(),
        context_builder=context_builder,
        scope_guard=_ScopeGuard(),
        usage_control=usage_control,
    )

    return (
        orchestrator,
        ai_question_engine,
        usage_control,
        context_builder,
    )


# ==================================================
# SUCCESSFUL MUTATION
# ==================================================


def test_successful_cfo_action_mutation_returns_immediately(
    monkeypatch,
) -> None:
    verified_result = {
        "status": "success",
        "question": (
            "Assign the funding gap action to Elie."
        ),
        "organisation_id": "org-1",
        "intent": "cfo_action_command",
        "domain": "management",
        "answer": (
            "CFO management action updated."
        ),
        "knowledge_used": True,
        "financial_data_used": False,
        "management_state_changed": True,
    }

    (
        orchestrator,
        ai_question_engine,
        usage_control,
        context_builder,
    ) = _build_orchestrator(
        verified_result=verified_result,
    )

    openai_calls = {
        "count": 0,
    }

    def _fail_openai(*args, **kwargs):
        openai_calls["count"] += 1
        raise AssertionError(
            "OpenAI must not be called for "
            "a successful CFO action mutation."
        )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_openai",
        _fail_openai,
    )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_verified_context",
        _fail_openai,
    )

    result = orchestrator.answer(
        question=(
            "Assign the funding gap action to Elie."
        ),
        organisation_id="org-1",
    )

    assert result == verified_result
    assert ai_question_engine.calls == 1
    assert usage_control.calls == []
    assert context_builder.calls == 0
    assert openai_calls["count"] == 0


# ==================================================
# REJECTED / AMBIGUOUS MUTATION
# ==================================================


def test_rejected_cfo_action_mutation_returns_immediately(
    monkeypatch,
) -> None:
    verified_result = {
        "status": "not_executed",
        "question": (
            "Assign the funding gap action to Elie."
        ),
        "organisation_id": "org-1",
        "intent": "cfo_action_command",
        "domain": "management",
        "answer": (
            "Action reference is ambiguous. "
            "Multiple CFO actions match the reference."
        ),
        "knowledge_used": True,
        "financial_data_used": False,
        "management_state_changed": False,
    }

    (
        orchestrator,
        ai_question_engine,
        usage_control,
        context_builder,
    ) = _build_orchestrator(
        verified_result=verified_result,
    )

    openai_calls = {
        "count": 0,
    }

    def _fail_openai(*args, **kwargs):
        openai_calls["count"] += 1
        raise AssertionError(
            "OpenAI must not be called for "
            "a rejected CFO action mutation."
        )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_openai",
        _fail_openai,
    )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_verified_context",
        _fail_openai,
    )

    result = orchestrator.answer(
        question=(
            "Assign the funding gap action to Elie."
        ),
        organisation_id="org-1",
    )

    assert result == verified_result
    assert ai_question_engine.calls == 1
    assert usage_control.calls == []
    assert context_builder.calls == 0
    assert openai_calls["count"] == 0


# ==================================================
# OTHER NON-SUCCESS CFO ACTION STATUS
# ==================================================


def test_any_cfo_action_command_status_is_terminal(
    monkeypatch,
) -> None:
    verified_result = {
        "status": "not_available",
        "question": (
            "Start the funding gap action."
        ),
        "organisation_id": "org-1",
        "intent": "cfo_action_command",
        "domain": "management",
        "answer": (
            "CFO action not found."
        ),
        "knowledge_used": True,
        "financial_data_used": False,
        "management_state_changed": False,
    }

    (
        orchestrator,
        _,
        usage_control,
        context_builder,
    ) = _build_orchestrator(
        verified_result=verified_result,
    )

    def _fail_openai(*args, **kwargs):
        raise AssertionError(
            "CFO action commands must never "
            "fall through to OpenAI."
        )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_openai",
        _fail_openai,
    )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_verified_context",
        _fail_openai,
    )

    result = orchestrator.answer(
        question=(
            "Start the funding gap action."
        ),
        organisation_id="org-1",
    )

    assert result == verified_result
    assert usage_control.calls == []
    assert context_builder.calls == 0


# ==================================================
# NORMAL DETERMINISTIC QUESTION
# ==================================================


def test_normal_successful_deterministic_answer_still_returns_immediately(
    monkeypatch,
) -> None:
    verified_result = {
        "status": "success",
        "question": (
            "What actions are overdue?"
        ),
        "organisation_id": "org-1",
        "intent": "overdue_actions",
        "domain": "management",
        "answer": (
            "There are no overdue actions."
        ),
        "knowledge_used": True,
        "financial_data_used": False,
    }

    (
        orchestrator,
        _,
        usage_control,
        context_builder,
    ) = _build_orchestrator(
        verified_result=verified_result,
    )

    def _fail_openai(*args, **kwargs):
        raise AssertionError(
            "Successful deterministic answers "
            "must still bypass OpenAI."
        )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_openai",
        _fail_openai,
    )

    monkeypatch.setattr(
        orchestrator,
        "_answer_with_verified_context",
        _fail_openai,
    )

    result = orchestrator.answer(
        question=(
            "What actions are overdue?"
        ),
        organisation_id="org-1",
    )

    assert result == verified_result
    assert usage_control.calls == []
    assert context_builder.calls == 0