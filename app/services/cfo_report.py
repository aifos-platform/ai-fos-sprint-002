from app.ai.providers.openai_provider import OpenAIProvider


def generate_cfo_report(
    financial_summary: str,
) -> str:
    """
    Generate an executive CFO report using AI.
    """

    provider = OpenAIProvider()

    return provider.generate_text(
        instructions=(
            "You are an experienced nonprofit Chief Financial Officer. "
            "Write a concise executive report for senior management."
        ),
        user_input=financial_summary,
    )
