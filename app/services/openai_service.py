import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class OpenAIService:
    """
    Central service for OpenAI requests made by AI-FOS.
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY was not found in the .env file.")

        self.client = OpenAI(api_key=api_key)

        print("✅ OpenAI client initialized successfully.")
        print(f"Using model: {os.getenv('OPENAI_MODEL')}")

    def generate_text(
        self,
        instructions: str,
        user_input: str,
    ) -> str:
        """
        Send instructions and financial information to OpenAI.
        """

        response = self.client.responses.create(
            model=os.getenv("OPENAI_MODEL"),
            instructions=instructions,
            input=user_input,
        )

        return response.output_text
