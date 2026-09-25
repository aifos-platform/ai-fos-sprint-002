import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class OpenAIService:
    """
    Central service for OpenAI requests made by AI-FOS.

    Supports:

    1. Backward-compatible text generation.
    2. Usage-aware generation for AI Usage Control.
    3. Optional per-request output-token limits.
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY was not found in the .env file."
            )

        self.model = (
            str(
                os.getenv("OPENAI_MODEL")
                or ""
            )
            .strip()
        )

        if not self.model:
            raise ValueError(
                "OPENAI_MODEL was not found in the .env file."
            )

        self.client = OpenAI(
            api_key=api_key
        )

        print(
            "✅ OpenAI client initialized successfully."
        )

        print(
            f"Using model: {self.model}"
        )

    def generate_text(
        self,
        instructions: str,
        user_input: str,
    ) -> str:
        """
        Preserve the existing AI-FOS provider contract.

        Existing callers receive only generated text.
        """

        result = self.generate_text_with_usage(
            instructions=instructions,
            user_input=user_input,
        )

        return result["text"]

    def generate_text_with_usage(
        self,
        instructions: str,
        user_input: str,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate text and return OpenAI token usage.

        max_output_tokens may be supplied by the AI-FOS
        Usage Control policy to enforce a per-request cap.
        """

        request: dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "input": user_input,
        }

        if (
            max_output_tokens is not None
            and max_output_tokens > 0
        ):
            request[
                "max_output_tokens"
            ] = int(
                max_output_tokens
            )

        response = (
            self.client.responses.create(
                **request
            )
        )

        usage = getattr(
            response,
            "usage",
            None,
        )

        input_tokens = self._usage_value(
            usage=usage,
            field="input_tokens",
        )

        output_tokens = self._usage_value(
            usage=usage,
            field="output_tokens",
        )

        total_tokens = self._usage_value(
            usage=usage,
            field="total_tokens",
        )

        return {
            "text": str(
                response.output_text
                or ""
            ),
            "model": str(
                getattr(
                    response,
                    "model",
                    self.model,
                )
                or self.model
            ),
            "usage": {
                "input_tokens": (
                    input_tokens
                ),
                "output_tokens": (
                    output_tokens
                ),
                "total_tokens": (
                    total_tokens
                ),
            },
        }

    @staticmethod
    def _usage_value(
        usage: Any,
        field: str,
    ) -> int:
        """
        Safely read a token-usage value.

        Supports both OpenAI SDK objects and dictionaries,
        allowing deterministic unit testing without calling
        the real API.
        """

        if usage is None:
            return 0

        if isinstance(
            usage,
            dict,
        ):
            value = usage.get(
                field,
                0,
            )

        else:
            value = getattr(
                usage,
                field,
                0,
            )

        try:
            return int(
                value or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0