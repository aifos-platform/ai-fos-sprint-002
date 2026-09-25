from typing import Any

from app.services.digital_cfo_orchestrator import (
    DigitalCFOOrchestrator,
)


class StubQuestionEngine:
    def __init__(
        self,
        result: dict[str, Any],
    ) -> None:
        self.result = result
        self.calls: list[dict[str, str]] = []

    def answer(
        self,
        question: str,
        organisation_id: str,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "question": question,
                "organisation_id": organisation_id,
            }
        )

        return dict(self.result)


class StubProvider:
    def __init__(
        self,
        response: str = "General CFO guidance.",
        should_fail: bool = False,
        usage_aware: bool = False,
        model: str = "test-model",
        input_tokens: int = 100,
        output_tokens: int = 50,
        total_tokens: int = 150,
    ) -> None:
        self.response = response
        self.should_fail = should_fail
        self.usage_aware = usage_aware
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens

        self.calls: list[
            dict[str, Any]
        ] = []

    def generate_text(
        self,
        instructions: str,
        user_input: str,
    ) -> str:
        self.calls.append(
            {
                "method": "generate_text",
                "instructions": instructions,
                "user_input": user_input,
            }
        )

        if self.should_fail:
            raise RuntimeError(
                "OpenAI unavailable"
            )

        return self.response

    def generate_text_with_usage(
        self,
        instructions: str,
        user_input: str,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not self.usage_aware:
            return self.generate_text(
                instructions=instructions,
                user_input=user_input,
            )

        self.calls.append(
            {
                "method": "generate_text_with_usage",
                "instructions": instructions,
                "user_input": user_input,
                "max_output_tokens": max_output_tokens,
            }
        )

        if self.should_fail:
            raise RuntimeError(
                "OpenAI unavailable"
            )

        return {
            "text": self.response,
            "model": self.model,
            "usage": {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
            },
        }


class StubContextBuilder:
    def __init__(
        self,
        result: dict[str, Any],
    ) -> None:
        self.result = result
        self.calls: list[str] = []

    def build(
        self,
        organisation_id: str,
    ) -> dict[str, Any]:
        self.calls.append(
            organisation_id
        )

        return dict(self.result)


def _unsupported_result(
    question: str,
) -> dict[str, Any]:
    return {
        "status": "unsupported",
        "question": question,
        "organisation_id": "acss",
        "intent": "unknown",
        "domain": "unknown",
        "answer": "Unsupported.",
        "knowledge_used": True,
        "financial_data_used": False,
    }


def test_verified_ai_fos_answer_is_returned_unchanged():
    verified_result = {
        "status": "success",
        "question": "What is our cash runway?",
        "organisation_id": "acss",
        "intent": "cash_runway",
        "domain": "liquidity",
        "answer": "Validated runway answer.",
        "knowledge_used": True,
        "financial_data_used": True,
    }

    engine = StubQuestionEngine(
        result=verified_result,
    )

    provider = StubProvider()

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                }
            },
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
    )

    result = orchestrator.answer(
        question="What is our cash runway?",
        organisation_id="acss",
    )

    assert result == verified_result
    assert len(engine.calls) == 1
    assert provider.calls == []
    assert context_builder.calls == []


def test_unknown_question_uses_openai_general_cfo_fallback():
    question = "What does EBITDA mean?"

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response=(
            "EBITDA is a general financial "
            "performance measure."
        )
    )

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                }
            },
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert (
        result["answer_source"]
        == "openai_general_cfo"
    )

    assert (
        result["verified_financial_answer"]
        is False
    )

    assert (
        result["financial_data_used"]
        is False
    )

    assert "EBITDA" in result["answer"]

    assert len(provider.calls) == 1

    # General knowledge questions should not
    # load organization-specific CFO context.
    assert context_builder.calls == []


def test_openai_general_fallback_receives_no_financial_figures():
    question = (
        "What should a CFO monitor monthly?"
    )

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider()

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "context": {
                "financial_facts": {
                    "revenue": 987654321,
                }
            },
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
    )

    orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    call = provider.calls[0]

    instructions = call[
        "instructions"
    ]

    user_input = call[
        "user_input"
    ]

    assert (
        "Do not invent, estimate, assume, or fabricate "
        "organization-specific financial figures."
        in instructions
    )

    assert (
        "No organization-specific financial figures are "
        "being supplied"
        in user_input
    )

    assert "987654321" not in user_input

    assert context_builder.calls == []


def test_organization_specific_question_uses_verified_cfo_context():
    question = (
        "Based on ACSS's financial situation, "
        "what should management focus on during "
        "the next six months?"
    )

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response=(
            "Management should prioritize "
            "liquidity and funding stability."
        )
    )

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "organisation_id": "acss",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                    "expenses": 1200,
                    "net_profit": -200,
                },
                "liquidity": {
                    "available_cash": 500,
                    "cash_runway_months": 3.5,
                },
                "financial_health": {
                    "score": 54,
                    "rating": "Weak",
                },
            },
            "available_sections": [
                "financial_facts",
                "liquidity",
                "financial_health",
            ],
            "missing_sections": [],
            "source_files": {
                "financial_facts": (
                    "financial_facts.json"
                ),
                "liquidity": "liquidity.json",
                "financial_health": (
                    "financial_health.json"
                ),
            },
            "trust": {
                "financial_source": (
                    "validated_ai_fos_outputs"
                ),
                "raw_general_ledger_included": False,
                "financial_recalculation_performed": False,
                "max_items_per_list": 5,
            },
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert (
        result["answer_source"]
        == "openai_verified_cfo_context"
    )

    assert (
        result["financial_data_used"]
        is True
    )

    assert (
        result["verified_financial_answer"]
        is False
    )

    assert (
        result["verified_context_used"]
        is True
    )

    assert (
        result["domain"]
        == "digital_cfo"
    )

    assert (
        context_builder.calls
        == ["acss"]
    )

    assert len(provider.calls) == 1


def test_verified_context_is_explicitly_identified_to_openai():
    question = (
        "What should we focus on based on "
        "our current financial position?"
    )

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response=(
            "Prioritize the most material "
            "verified financial issues."
        )
    )

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "organisation_id": "acss",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                    "expenses": 1200,
                },
                "liquidity": {
                    "cash_runway_months": 3.5,
                },
            },
            "available_sections": [
                "financial_facts",
                "liquidity",
            ],
            "missing_sections": [
                "financial_forecast",
            ],
            "source_files": {
                "financial_facts": (
                    "financial_facts.json"
                ),
                "liquidity": (
                    "liquidity.json"
                ),
            },
            "trust": {
                "financial_source": (
                    "validated_ai_fos_outputs"
                ),
                "raw_general_ledger_included": False,
                "financial_recalculation_performed": False,
            },
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
    )

    orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    call = provider.calls[0]

    instructions = call[
        "instructions"
    ]

    user_input = call[
        "user_input"
    ]

    assert (
        "VERIFIED AI-FOS CFO CONTEXT"
        in user_input
    )

    assert (
        '"cash_runway_months": 3.5'
        in user_input
    )

    assert (
        '"revenue": 1000'
        in user_input
    )

    assert (
        "validated AI-FOS outputs"
        in instructions
    )

    assert (
        "Do not recalculate"
        in instructions
    )

    assert (
        "Do not invent"
        in instructions
    )


def test_organization_specific_question_without_context_does_not_fake_financial_data():
    question = (
        "Based on our financial situation, "
        "what should management focus on?"
    )

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response=(
            "Verified organization-specific "
            "financial information is required."
        )
    )

    context_builder = StubContextBuilder(
        result={
            "status": "not_available",
            "organisation_id": "acss",
            "context": {},
            "available_sections": [],
            "missing_sections": [],
            "source_files": {},
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert (
        result["financial_data_used"]
        is False
    )

    assert (
        result["verified_context_used"]
        is False
    )

    assert (
        result["answer_source"]
        == "openai_general_cfo"
    )

    assert (
        context_builder.calls
        == ["acss"]
    )


def test_openai_failure_returns_original_verified_result():
    question = (
        "Explain working capital."
    )

    original_result = (
        _unsupported_result(
            question
        )
    )

    original_result["answer"] = (
        "Original unsupported response."
    )

    engine = StubQuestionEngine(
        result=original_result,
    )

    provider = StubProvider(
        should_fail=True,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result == original_result


def test_empty_openai_response_returns_original_result():
    question = (
        "Explain liquidity."
    )

    original_result = (
        _unsupported_result(
            question
        )
    )

    original_result["answer"] = (
        "Original unsupported response."
    )

    engine = StubQuestionEngine(
        result=original_result,
    )

    provider = StubProvider(
        response="   ",
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result == original_result

class StubScopeGuard:
    def __init__(
        self,
        result: dict[str, Any],
    ) -> None:
        self.result = result
        self.calls: list[str] = []

    def evaluate(
        self,
        question: str,
    ) -> dict[str, Any]:
        self.calls.append(question)
        return dict(self.result)


def test_out_of_scope_question_is_blocked_before_question_engine():
    engine = StubQuestionEngine(
        result={
            "status": "unsupported",
            "question": "Write me a birthday song.",
            "organisation_id": "acss",
            "intent": "unknown",
            "domain": "unknown",
            "answer": "Unsupported.",
        }
    )

    provider = StubProvider()

    scope_guard = StubScopeGuard(
        {
            "allowed": False,
            "scope": "out_of_scope",
            "reason": "non_cfo_request",
            "classifier_domain": "unknown",
            "classifier_intent": "unknown",
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        scope_guard=scope_guard,
    )

    result = orchestrator.answer(
        question="Write me a birthday song.",
        organisation_id="acss",
    )

    assert result["status"] == "blocked"
    assert result["domain"] == "scope_control"
    assert result["intent"] == "out_of_scope"
    assert result["answer_source"] == "scope_guard"
    assert result["financial_data_used"] is False
    assert result["openai_used"] is False

    assert len(scope_guard.calls) == 1

    # Critical cost-control requirement:
    # blocked questions never reach either the deterministic
    # engine or the OpenAI provider.
    assert engine.calls == []
    assert provider.calls == []


def test_allowed_question_continues_to_ai_fos_engine():
    verified_result = {
        "status": "success",
        "question": "What is our cash runway?",
        "organisation_id": "acss",
        "intent": "cash_runway",
        "domain": "liquidity",
        "answer": "Validated runway answer.",
        "knowledge_used": True,
        "financial_data_used": True,
    }

    engine = StubQuestionEngine(
        result=verified_result
    )

    provider = StubProvider()

    scope_guard = StubScopeGuard(
        {
            "allowed": True,
            "scope": "cfo",
            "reason": "ai_fos_classified",
            "classifier_domain": "liquidity",
            "classifier_intent": "cash_runway",
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        scope_guard=scope_guard,
    )

    result = orchestrator.answer(
        question="What is our cash runway?",
        organisation_id="acss",
    )

    assert result == verified_result
    assert len(scope_guard.calls) == 1
    assert len(engine.calls) == 1
    assert provider.calls == []


def test_blocked_response_does_not_expose_internal_classifier_details():
    engine = StubQuestionEngine(
        result={}
    )

    provider = StubProvider()

    scope_guard = StubScopeGuard(
        {
            "allowed": False,
            "scope": "out_of_scope",
            "reason": "scope_not_established",
            "classifier_domain": "unknown",
            "classifier_intent": "unknown",
        }
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        scope_guard=scope_guard,
    )

    result = orchestrator.answer(
        question="Tell me something interesting.",
        organisation_id="acss",
    )

    assert result["status"] == "blocked"
    assert result["scope_reason"] == "scope_not_established"

    assert "classifier_domain" not in result
    assert "classifier_intent" not in result

    assert engine.calls == []
    assert provider.calls == []

class StubUsageControl:
    def __init__(
        self,
        allowed: bool = True,
        reason: str = "allowed",
        max_output_tokens: int = 2000,
    ) -> None:
        self.allowed = allowed
        self.reason = reason
        self.max_output_tokens = max_output_tokens

        self.authorize_calls: list[
            dict[str, str]
        ] = []

        self.record_usage_calls: list[
            dict[str, Any]
        ] = []

    def authorize(
        self,
        organisation_id: str,
        request_type: str,
    ) -> dict[str, Any]:
        self.authorize_calls.append(
            {
                "organisation_id": organisation_id,
                "request_type": request_type,
            }
        )

        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "max_output_tokens": (
                self.max_output_tokens
            ),
        }

    def record_usage(
        self,
        organisation_id: str,
        request_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        status: str = "success",
    ) -> dict[str, Any]:
        call = {
            "organisation_id": organisation_id,
            "request_type": request_type,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "status": status,
        }

        self.record_usage_calls.append(
            call
        )

        return call


def test_deterministic_answer_does_not_consume_ai_allowance():
    verified_result = {
        "status": "success",
        "question": "What is our cash runway?",
        "organisation_id": "acss",
        "intent": "cash_runway",
        "domain": "liquidity",
        "answer": "Validated runway answer.",
        "knowledge_used": True,
        "financial_data_used": True,
    }

    engine = StubQuestionEngine(
        result=verified_result,
    )

    provider = StubProvider()

    usage_control = StubUsageControl(
        allowed=False,
        reason="monthly_token_limit_reached",
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question="What is our cash runway?",
        organisation_id="acss",
    )

    assert result == verified_result

    assert provider.calls == []

    assert (
        usage_control.authorize_calls
        == []
    )


def test_general_cfo_openai_request_requires_usage_authorization():
    engine = StubQuestionEngine(
        result={
            "status": "unsupported",
            "question": "Explain EBITDA.",
            "organisation_id": "acss",
            "intent": "unknown",
            "domain": "unknown",
            "answer": "Unsupported.",
            "knowledge_used": True,
            "financial_data_used": False,
        }
    )

    provider = StubProvider(
        response="EBITDA explanation.",
    )

    usage_control = StubUsageControl(
        allowed=True,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question="Explain EBITDA.",
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert (
        result["answer_source"]
        == "openai_general_cfo"
    )

    assert (
        usage_control.authorize_calls
        == [
            {
                "organisation_id": "acss",
                "request_type": "general_cfo",
            }
        ]
    )

    assert len(provider.calls) == 1


def test_general_cfo_request_is_blocked_when_allowance_is_exhausted():
    engine = StubQuestionEngine(
        result={
            "status": "unsupported",
            "question": "Explain EBITDA.",
            "organisation_id": "acss",
            "intent": "unknown",
            "domain": "unknown",
            "answer": "Unsupported.",
            "knowledge_used": True,
            "financial_data_used": False,
        }
    )

    provider = StubProvider()

    usage_control = StubUsageControl(
        allowed=False,
        reason="monthly_token_limit_reached",
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question="Explain EBITDA.",
        organisation_id="acss",
    )

    assert result["status"] == "blocked"

    assert (
        result["domain"]
        == "ai_usage_control"
    )

    assert (
        result["intent"]
        == "ai_usage_limit"
    )

    assert (
        result["usage_reason"]
        == "monthly_token_limit_reached"
    )

    assert (
        result["answer_source"]
        == "ai_usage_control"
    )

    assert result["openai_used"] is False

    assert provider.calls == []


def test_verified_cfo_reasoning_has_separate_usage_authorization():
    engine = StubQuestionEngine(
        result={
            "status": "unsupported",
            "question": (
                "Based on ACSS's financial situation, "
                "what should management focus on?"
            ),
            "organisation_id": "acss",
            "intent": "unknown",
            "domain": "unknown",
            "answer": "Unsupported.",
            "knowledge_used": True,
            "financial_data_used": False,
        }
    )

    provider = StubProvider(
        response="Verified-context CFO analysis.",
    )

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                    "expenses": 900,
                }
            },
            "available_sections": [
                "financial_facts",
            ],
            "missing_sections": [],
            "trust": {
                "financial_recalculation_performed": False,
            },
        }
    )

    usage_control = StubUsageControl(
        allowed=True,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question=(
            "Based on ACSS's financial situation, "
            "what should management focus on?"
        ),
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert (
        result["answer_source"]
        == "openai_verified_cfo_context"
    )

    assert (
        usage_control.authorize_calls
        == [
            {
                "organisation_id": "acss",
                "request_type": (
                    "verified_cfo_reasoning"
                ),
            }
        ]
    )

    assert len(provider.calls) == 1


def test_verified_cfo_reasoning_is_blocked_before_openai_when_limit_reached():
    engine = StubQuestionEngine(
        result={
            "status": "unsupported",
            "question": (
                "Based on ACSS's financial situation, "
                "what should management focus on?"
            ),
            "organisation_id": "acss",
            "intent": "unknown",
            "domain": "unknown",
            "answer": "Unsupported.",
            "knowledge_used": True,
            "financial_data_used": False,
        }
    )

    provider = StubProvider()

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                    "expenses": 900,
                }
            },
            "available_sections": [
                "financial_facts",
            ],
            "missing_sections": [],
            "trust": {
                "financial_recalculation_performed": False,
            },
        }
    )

    usage_control = StubUsageControl(
        allowed=False,
        reason="daily_token_limit_reached",
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question=(
            "Based on ACSS's financial situation, "
            "what should management focus on?"
        ),
        organisation_id="acss",
    )

    assert result["status"] == "blocked"

    assert (
        result["usage_reason"]
        == "daily_token_limit_reached"
    )

    assert (
        result["answer_source"]
        == "ai_usage_control"
    )

    assert result["openai_used"] is False

    assert provider.calls == []  

def test_general_cfo_passes_authorized_output_cap_to_provider():
    question = "Explain EBITDA."

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response="EBITDA explanation.",
        usage_aware=True,
    )

    usage_control = StubUsageControl(
        allowed=True,
        max_output_tokens=1750,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert len(provider.calls) == 1

    call = provider.calls[0]

    assert (
        call["method"]
        == "generate_text_with_usage"
    )

    assert (
        call["max_output_tokens"]
        == 1750
    )


def test_general_cfo_records_actual_openai_usage():
    question = "Explain EBITDA."

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response="EBITDA explanation.",
        usage_aware=True,
        model="test-model-1",
        input_tokens=120,
        output_tokens=80,
        total_tokens=200,
    )

    usage_control = StubUsageControl(
        allowed=True,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert (
        usage_control.record_usage_calls
        == [
            {
                "organisation_id": "acss",
                "request_type": "general_cfo",
                "model": "test-model-1",
                "input_tokens": 120,
                "output_tokens": 80,
                "total_tokens": 200,
                "status": "success",
            }
        ]
    )


def test_verified_cfo_reasoning_records_actual_openai_usage():
    question = (
        "Based on ACSS's financial situation, "
        "what should management focus on?"
    )

    engine = StubQuestionEngine(
        result=_unsupported_result(
            question
        )
    )

    provider = StubProvider(
        response="Verified CFO analysis.",
        usage_aware=True,
        model="test-model-2",
        input_tokens=450,
        output_tokens=150,
        total_tokens=600,
    )

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "organisation_id": "acss",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                    "expenses": 900,
                }
            },
            "available_sections": [
                "financial_facts",
            ],
            "missing_sections": [],
            "source_files": {
                "financial_facts": (
                    "financial_facts.json"
                ),
            },
            "trust": {
                "financial_recalculation_performed": False,
            },
        }
    )

    usage_control = StubUsageControl(
        allowed=True,
        max_output_tokens=2200,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question=question,
        organisation_id="acss",
    )

    assert result["status"] == "success"

    assert len(provider.calls) == 1

    call = provider.calls[0]

    assert (
        call["method"]
        == "generate_text_with_usage"
    )

    assert (
        call["max_output_tokens"]
        == 2200
    )

    assert (
        usage_control.record_usage_calls
        == [
            {
                "organisation_id": "acss",
                "request_type": (
                    "verified_cfo_reasoning"
                ),
                "model": "test-model-2",
                "input_tokens": 450,
                "output_tokens": 150,
                "total_tokens": 600,
                "status": "success",
            }
        ]
    )


def test_deterministic_answer_records_no_openai_usage():
    verified_result = {
        "status": "success",
        "question": "What is our cash runway?",
        "organisation_id": "acss",
        "intent": "cash_runway",
        "domain": "liquidity",
        "answer": "Validated runway answer.",
        "knowledge_used": True,
        "financial_data_used": True,
    }

    engine = StubQuestionEngine(
        result=verified_result,
    )

    provider = StubProvider(
        usage_aware=True,
    )

    usage_control = StubUsageControl(
        allowed=True,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question="What is our cash runway?",
        organisation_id="acss",
    )

    assert result == verified_result

    assert provider.calls == []

    assert (
        usage_control.authorize_calls
        == []
    )

    assert (
        usage_control.record_usage_calls
        == []
    )  

def test_financial_scenario_decision_intelligence_is_returned_without_openai():
    scenario_result = {
        "status": "success",
        "question": (
            "What if revenue decreases by 10%?"
        ),
        "organisation_id": "acss",
        "intent": "revenue_scenario",
        "domain": "financial_scenario",
        "answer": (
            "Scenario analysis with deterministic "
            "decision intelligence."
        ),
        "knowledge_used": True,
        "financial_data_used": True,
    }

    engine = StubQuestionEngine(
        result=scenario_result,
    )

    provider = StubProvider(
        usage_aware=True,
    )

    context_builder = StubContextBuilder(
        result={
            "status": "available",
            "context": {
                "financial_facts": {
                    "revenue": 1000,
                }
            },
        }
    )

    usage_control = StubUsageControl(
        allowed=True,
    )

    orchestrator = DigitalCFOOrchestrator(
        ai_question_engine=engine,
        provider=provider,
        context_builder=context_builder,
        usage_control=usage_control,
    )

    result = orchestrator.answer(
        question=(
            "What if revenue decreases by 10%?"
        ),
        organisation_id="acss",
    )

    assert result == scenario_result

    assert len(engine.calls) == 1

    assert provider.calls == []

    assert context_builder.calls == []

    assert (
        usage_control.authorize_calls
        == []
    )

    assert (
        usage_control.record_usage_calls
        == []
    )            