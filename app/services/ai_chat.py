from app.ai.providers.openai_provider import OpenAIProvider


def ask_ai(
    context: str,
    question: str,
) -> str:
    """
    Ask the AI questions about the organization's financial data.
    """

    provider = OpenAIProvider()

    return provider.generate_text(
        instructions=(
            "You are the AI-FOS Digital CFO.\n"
            "Answer only using the financial information provided.\n"
            "If the answer is not contained in the supplied data, clearly say so."
        ),
        user_input=f"""
Financial Data

{context}

User Question

{question}
""",
    )