from types import SimpleNamespace

from app.services.openai_service import OpenAIService


class StubResponses:
    def __init__(self, response) -> None:
        self.response = response
        self.calls = []


    def create(
        self,
        model,
        instructions,
        input,
        **kwargs,
    ):
        call = {
            "model": model,
            "instructions": instructions,
            "input": input,
        }

        call.update(kwargs)

        self.calls.append(call)

        return self.response


class StubClient:
    def __init__(self, response) -> None:
        self.responses = StubResponses(response=response)


def _build_service(response):
    service = OpenAIService.__new__(OpenAIService)

    service.model = "test-model"
    service.client = StubClient(response=response)

    return service


def test_generate_text_preserves_string_contract():
    response = SimpleNamespace(
        output_text="CFO answer.",
        model="test-model",
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
        ),
    )

    service = _build_service(response)

    result = service.generate_text(
        instructions="Instructions",
        user_input="Question",
    )

    assert result == "CFO answer."
    assert isinstance(result, str)


def test_generate_text_with_usage_returns_token_metadata():
    response = SimpleNamespace(
        output_text="CFO answer.",
        model="gpt-test",
        usage=SimpleNamespace(
            input_tokens=125,
            output_tokens=35,
            total_tokens=160,
        ),
    )

    service = _build_service(response)

    result = service.generate_text_with_usage(
        instructions="Instructions",
        user_input="Question",
    )

    assert result["text"] == "CFO answer."
    assert result["model"] == "gpt-test"

    assert result["usage"]["input_tokens"] == 125

    assert result["usage"]["output_tokens"] == 35

    assert result["usage"]["total_tokens"] == 160


def test_usage_dictionary_is_supported():
    response = SimpleNamespace(
        output_text="Answer.",
        model="test-model",
        usage={
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
        },
    )

    service = _build_service(response)

    result = service.generate_text_with_usage(
        instructions="Instructions",
        user_input="Question",
    )

    assert result["usage"] == {
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
    }


def test_missing_usage_returns_zero_without_failure():
    response = SimpleNamespace(
        output_text="Answer.",
        model="test-model",
        usage=None,
    )

    service = _build_service(response)

    result = service.generate_text_with_usage(
        instructions="Instructions",
        user_input="Question",
    )

    assert result["usage"] == {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }


def test_request_uses_configured_model():
    response = SimpleNamespace(
        output_text="Answer.",
        model="test-model",
        usage=None,
    )

    service = _build_service(response)

    service.generate_text_with_usage(
        instructions="System instructions",
        user_input="User question",
    )

    call = service.client.responses.calls[0]

    assert call["model"] == "test-model"
    assert call["instructions"] == "System instructions"
    assert call["input"] == "User question"


def test_output_token_cap_is_sent_to_openai():
    response = SimpleNamespace(
        output_text="Answer.",
        model="test-model",
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        ),
    )

    service = _build_service(response)

    service.generate_text_with_usage(
        instructions="Instructions",
        user_input="Question",
        max_output_tokens=2000,
    )

    call = service.client.responses.calls[0]

    assert call["max_output_tokens"] == 2000


def test_output_token_cap_is_omitted_when_not_supplied():
    response = SimpleNamespace(
        output_text="Answer.",
        model="test-model",
        usage=None,
    )

    service = _build_service(response)

    service.generate_text_with_usage(
        instructions="Instructions",
        user_input="Question",
    )

    call = service.client.responses.calls[0]

    assert "max_output_tokens" not in call
