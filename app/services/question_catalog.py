from typing import Any


QUESTION_CATALOG: list[dict[str, Any]] = [
    {
        "category": "Financial Health",
        "description": "Understand the organization's overall financial position.",
        "questions": [
            {
                "id": "financial_health_001",
                "question": "What is our current financial health score?",
            },
            {
                "id": "financial_health_002",
                "question": "Why is our financial health score low?",
            },
            {
                "id": "financial_health_003",
                "question": "What are the main weaknesses in our financial position?",
            },
            {
                "id": "financial_health_004",
                "question": "What are the strongest areas of our financial health?",
            },
            {
                "id": "financial_health_005",
                "question": "What is currently hurting our financial health the most?",
            },
            {
                "id": "financial_health_006",
                "question": "What should management do to improve our financial health?",
            },
            {
                "id": "financial_health_007",
                "question": "Are there any serious financial warning signs?",
            },
            {
                "id": "financial_health_008",
                "question": "How would you summarize our financial health for management?",
            },
        ],
    },
    {
        "category": "Cash & Liquidity",
        "description": "Understand cash availability and short-term financial resilience.",
        "questions": [
            {
                "id": "liquidity_001",
                "question": "How much cash do we currently have available?",
            },
            {
                "id": "liquidity_002",
                "question": "How much of our cash is restricted or blocked?",
            },
            {
                "id": "liquidity_003",
                "question": "What is our current cash runway?",
            },
            {
                "id": "liquidity_004",
                "question": "Do we have enough cash to cover our operating expenses?",
            },
            {
                "id": "liquidity_005",
                "question": "Is our liquidity position healthy?",
            },
            {
                "id": "liquidity_006",
                "question": "What are the main risks to our liquidity?",
            },
            {
                "id": "liquidity_007",
                "question": "How long can we operate with our available cash?",
            },
            {
                "id": "liquidity_008",
                "question": "What should management do to protect our cash position?",
            },
        ],
    },
    {
        "category": "Budget",
        "description": "Monitor budget utilization, overspending, and unbudgeted activity.",
        "questions": [
            {
                "id": "budget_001",
                "question": "What is our overall budget utilization?",
            },
            {
                "id": "budget_002",
                "question": "Are we currently over budget?",
            },
            {
                "id": "budget_003",
                "question": "Which areas are over budget?",
            },
            {
                "id": "budget_004",
                "question": "Where do we have the largest budget variances?",
            },
            {
                "id": "budget_005",
                "question": "How much unbudgeted spending do we have?",
            },
            {
                "id": "budget_006",
                "question": "Which budget lines need management attention?",
            },
            {
                "id": "budget_007",
                "question": "Where do we still have available budget?",
            },
            {
                "id": "budget_008",
                "question": "What are the main budget control issues?",
            },
        ],
    },
    {
        "category": "Funding",
        "description": "Understand funding requirements, coverage, and secured funding.",
        "questions": [
            {
                "id": "funding_001",
                "question": "What is our current funding gap?",
            },
            {
                "id": "funding_002",
                "question": "Do we have enough funding?",
            },
            {
                "id": "funding_003",
                "question": "How much of our remaining requirements are funded?",
            },
            {
                "id": "funding_004",
                "question": "How much secured funding do we have?",
            },
            {
                "id": "funding_005",
                "question": "Why can't we use all our secured funding?",
            },
            {
                "id": "funding_006",
                "question": "How much secured funding is eligible to cover our funding needs?",
            },
            {
                "id": "funding_007",
                "question": "How much funding still needs to be secured?",
            },
            {
                "id": "funding_008",
                "question": "What should management do about the funding gap?",
            },
        ],
    },
    {
        "category": "Financial Performance",
        "description": "Understand revenue, expenses, surplus, deficit, and operating performance.",
        "questions": [
            {
                "id": "performance_001",
                "question": "Are we currently operating at a surplus or deficit?",
            },
            {
                "id": "performance_002",
                "question": "What is our current net result?",
            },
            {
                "id": "performance_003",
                "question": "How much revenue have we generated?",
            },
            {
                "id": "performance_004",
                "question": "How much have we spent?",
            },
            {
                "id": "performance_005",
                "question": "What are our largest expenses?",
            },
            {
                "id": "performance_006",
                "question": "What are the main drivers of our financial performance?",
            },
            {
                "id": "performance_007",
                "question": "Is our current operating performance sustainable?",
            },
            {
                "id": "performance_008",
                "question": "What should management focus on to improve financial performance?",
            },
        ],
    },
    {
        "category": "Risks",
        "description": "Identify the organization's most important financial risks.",
        "questions": [
            {
                "id": "risk_001",
                "question": "What are our biggest financial risks?",
            },
            {
                "id": "risk_002",
                "question": "Do we have any high-priority financial risks?",
            },
            {
                "id": "risk_003",
                "question": "Which financial risk needs immediate attention?",
            },
            {
                "id": "risk_004",
                "question": "What liquidity risks are we facing?",
            },
            {
                "id": "risk_005",
                "question": "What budget risks are we facing?",
            },
            {
                "id": "risk_006",
                "question": "What funding risks are we facing?",
            },
            {
                "id": "risk_007",
                "question": "What could negatively affect our financial position?",
            },
            {
                "id": "risk_008",
                "question": "Which risks should management monitor closely?",
            },
        ],
    },
    {
        "category": "Recommendations",
        "description": "Review CFO-level recommendations and management priorities.",
        "questions": [
            {
                "id": "recommendation_001",
                "question": "What should management prioritize?",
            },
            {
                "id": "recommendation_002",
                "question": "What are the most important actions management should take?",
            },
            {
                "id": "recommendation_003",
                "question": "What should we do about our operating deficit?",
            },
            {
                "id": "recommendation_004",
                "question": "What should we do to improve liquidity?",
            },
            {
                "id": "recommendation_005",
                "question": "What should we do about budget overruns?",
            },
            {
                "id": "recommendation_006",
                "question": "What should we do about our funding gap?",
            },
            {
                "id": "recommendation_007",
                "question": "What actions require immediate management attention?",
            },
            {
                "id": "recommendation_008",
                "question": "What should management discuss at the next finance meeting?",
            },
        ],
    },
    {
        "category": "Grants",
        "description": "Understand the organization's grant portfolio and grant-related financial issues.",
        "questions": [
            {
                "id": "grant_001",
                "question": "How many grants do we currently have?",
            },
            {
                "id": "grant_002",
                "question": "Which grants require financial attention?",
            },
            {
                "id": "grant_003",
                "question": "Which grants have remaining budget?",
            },
            {
                "id": "grant_004",
                "question": "Which grants have high utilization?",
            },
            {
                "id": "grant_005",
                "question": "Are there grants with spending but no identified budget?",
            },
            {
                "id": "grant_006",
                "question": "Are there grants with budget but no spending?",
            },
            {
                "id": "grant_007",
                "question": "Which grants may have funding or budget issues?",
            },
            {
                "id": "grant_008",
                "question": "What should management know about our grant portfolio?",
            },
        ],
    },
]


def get_question_catalog() -> list[dict[str, Any]]:
    """
    Return the AI-FOS suggested-question catalogue.

    A copy is returned so callers cannot accidentally
    modify the global catalogue.
    """

    return [
        {
            "category": category["category"],
            "description": category["description"],
            "questions": [
                dict(question)
                for question in category["questions"]
            ],
        }
        for category in QUESTION_CATALOG
    ]