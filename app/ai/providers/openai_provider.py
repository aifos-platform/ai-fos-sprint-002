from typing import Any

from app.ai.provider import AIProvider
from app.services.openai_service import OpenAIService


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of the AI provider interface.

    Supports both:
    - backward-compatible text generation
    - usage-aware generation for AI usage control
    """

    def __init__(self):
        self.client = OpenAIService()

    def generate_text(
        self,
        instructions: str,
        user_input: str,
    ) -> str:
        """
        Preserve the existing provider contract.

        Existing callers receive only generated text.
        """

        return self.client.generate_text(
            instructions=instructions,
            user_input=user_input,
        )

    def generate_text_with_usage(
        self,
        instructions: str,
        user_input: str,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate text and return OpenAI usage metadata.

        max_output_tokens is supplied by the AI-FOS usage
        policy and is enforced by OpenAIService.
        """

        return self.client.generate_text_with_usage(
            instructions=instructions,
            user_input=user_input,
            max_output_tokens=max_output_tokens,
        )