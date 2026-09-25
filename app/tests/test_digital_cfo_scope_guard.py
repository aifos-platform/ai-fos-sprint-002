from typing import Any

from app.services.digital_cfo_scope_guard import (
    DigitalCFOScopeGuard,
)


class StubClassifier:
    def __init__(
        self,
        result: dict[str, Any],
    ) -> None:
        self.result = result
        self.calls: list[str] = []

    def classify(
        self,
        question: str,
    ) -> dict[str, Any]:
        self.calls.append(question)
        return dict(self.result)


def _unknown_classifier():
    return StubClassifier(
        {
            "domain": "unknown",
            "intent": "unknown",
            "target": None,
        }
    )


def test_empty_question_is_blocked():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate("   ")

    assert result["allowed"] is False
    assert result["scope"] == "out_of_scope"
    assert result["reason"] == "empty_question"


def test_recognized_ai_fos_question_is_allowed():
    classifier = StubClassifier(
        {
            "domain": "liquidity",
            "intent": "cash_runway",
            "target": "cash_runway",
        }
    )

    guard = DigitalCFOScopeGuard(
        question_classifier=classifier
    )

    result = guard.evaluate(
        "What is our cash runway?"
    )

    assert result["allowed"] is True
    assert result["scope"] == "cfo"
    assert result["reason"] == "ai_fos_classified"
    assert result["classifier_domain"] == "liquidity"
    assert result["classifier_intent"] == "cash_runway"


def test_general_finance_question_is_allowed():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "What does EBITDA mean?"
    )

    assert result["allowed"] is True
    assert result["scope"] == "cfo"
    assert result["reason"] == "general_cfo_scope"


def test_nonprofit_grant_question_is_allowed():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "How should a nonprofit manage restricted grants?"
    )

    assert result["allowed"] is True
    assert result["scope"] == "cfo"


def test_finance_related_email_request_is_allowed():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Write an email to our donor explaining "
        "the budget variance."
    )

    assert result["allowed"] is True
    assert result["scope"] == "cfo"


def test_song_request_is_blocked():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Write me a birthday song."
    )

    assert result["allowed"] is False
    assert result["scope"] == "out_of_scope"
    assert result["reason"] == "non_cfo_request"


def test_travel_request_is_blocked():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Plan my vacation to Italy."
    )

    assert result["allowed"] is False
    assert result["scope"] == "out_of_scope"


def test_sports_request_is_blocked():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Who won the match yesterday?"
    )

    assert result["allowed"] is False
    assert result["scope"] == "out_of_scope"


def test_programming_request_is_blocked():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Write Python code for my website."
    )

    assert result["allowed"] is False
    assert result["scope"] == "out_of_scope"


def test_ambiguous_non_finance_request_is_blocked():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Tell me something interesting."
    )

    assert result["allowed"] is False
    assert result["scope"] == "out_of_scope"
    assert result["reason"] == "scope_not_established"


def test_out_of_scope_request_is_blocked_before_classifier():
    classifier = StubClassifier(
        {
            "domain": "unknown",
            "intent": "unknown",
            "target": None,
        }
    )

    guard = DigitalCFOScopeGuard(
        question_classifier=classifier
    )

    result = guard.evaluate(
        "Write me a poem."
    )

    assert result["allowed"] is False

    # Clear non-CFO requests should be rejected
    # before classifier work is needed.
    assert classifier.calls == []


def test_finance_word_does_not_override_clear_out_of_scope_request():
    guard = DigitalCFOScopeGuard(
        question_classifier=(
            _unknown_classifier()
        )
    )

    result = guard.evaluate(
        "Write Python code for a finance website."
    )

    assert result["allowed"] is False
    assert result["reason"] == "non_cfo_request"