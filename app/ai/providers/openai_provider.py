from app.ai.provider import AIProvider
from app.services.openai_service import OpenAIService


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of the AI provider interface.
    """

    def __init__(self):
        self.client = OpenAIService()

    def generate_text(
        self,
        instructions: str,
        user_input: str,
    ) -> str:
        return self.client.generate_text(
            instructions=instructions,
            user_input=user_input,
        )