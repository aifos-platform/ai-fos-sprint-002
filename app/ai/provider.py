from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Base interface for every AI provider used by AI-FOS.
    """

    @abstractmethod
    def generate_text(
        self,
        instructions: str,
        user_input: str,
    ) -> str:
        """
        Generate a text response from an AI model.
        """

        raise NotImplementedError
