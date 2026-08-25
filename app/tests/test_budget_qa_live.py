import json
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:8000"
ORGANISATION_ID = "acss"


TEST_CASES = [
    # ---------------------------------
    # Budget variance
    # ---------------------------------
    {
        "question": "What is our budget variance?",
        "intent": "portfolio_budget_variance",
        "answer_contains": "592,924.81",
    },
    # ---------------------------------
    # Overall budget position
    # ---------------------------------
    {
        "question": "How much are we over budget?",
        "intent": "portfolio_budget_position",
        "answer_contains": "264,593.66",
    },
    {
        "question": "Are we spending more than we budgeted?",
        "intent": "portfolio_budget_position",
        "answer_contains": "264,593.66",
    },
    {
        "question": "Are we spending less than we budgeted?",
        "intent": "portfolio_budget_position",
        "answer_contains": "264,593.66",
    },
    # ---------------------------------
    # Budget remaining
    # ---------------------------------
    {
        "question": "How much budget do we have left?",
        "intent": "portfolio_budget_remaining",
        "answer_contains": "264,593.66",
    },
    {
        "question": "Do we still have budget remaining?",
        "intent": "portfolio_budget_remaining",
        "answer_contains": "264,593.66",
    },
    {
        "question": "Is there any budget left?",
        "intent": "portfolio_budget_remaining",
        "answer_contains": "264,593.66",
    },
    # ---------------------------------
    # Budget utilization
    # ---------------------------------
    {
        "question": "What is our budget utilization?",
        "intent": "portfolio_budget_utilization",
        "answer_contains": "87.45%",
    },
    {
        "question": "How much of our budget have we used?",
        "intent": "portfolio_budget_utilization",
        "answer_contains": "87.45%",
    },
    {
        "question": "What percentage of our budget have we spent?",
        "intent": "portfolio_budget_utilization",
        "answer_contains": "87.45%",
    },
    # ---------------------------------
    # Unbudgeted actual spending
    # ---------------------------------
    {
        "question": "How much have we spent without a budget?",
        "intent": "unbudgeted_actual",
        "answer_contains": "328,331.15",
    },
    {
        "question": "How much spending do we have without a budget?",
        "intent": "unbudgeted_actual",
        "answer_contains": "328,331.15",
    },
    # ---------------------------------
    # Over-budget lines
    # ---------------------------------
    {
        "question": "How many budget lines are over budget?",
        "intent": "over_budget_count",
        "answer_contains": "25",
    },
    {
        "question": "How many budget lines have exceeded their budgets?",
        "intent": "over_budget_count",
        "answer_contains": "25",
    },
]


def ask_ai_fos(question: str) -> dict:
    encoded_question = urllib.parse.quote(question)

    url = f"{BASE_URL}/ask/{ORGANISATION_ID}" f"?question={encoded_question}"

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        body = response.read().decode("utf-8")

        return {
            "http_status": response.status,
            "body": json.loads(body),
        }


def run_tests() -> None:
    passed = 0
    failed = 0

    print()
    print("=" * 78)
    print("AI-FOS LIVE BUDGET Q&A TEST SUITE")
    print("=" * 78)
    print(f"Organisation: {ORGANISATION_ID}")
    print(f"API: {BASE_URL}")
    print("=" * 78)

    for index, test_case in enumerate(
        TEST_CASES,
        start=1,
    ):
        question = test_case["question"]
        expected_intent = test_case["intent"]
        answer_contains = test_case["answer_contains"]

        reasons = []

        try:
            result = ask_ai_fos(question)

            http_status = result["http_status"]
            body = result["body"]

            actual_status = body.get("status")
            actual_domain = body.get("domain")
            actual_intent = body.get("intent")
            knowledge_used = body.get("knowledge_used")
            financial_data_used = body.get("financial_data_used")
            answer = str(body.get("answer", ""))

            if http_status != 200:
                reasons.append(f"HTTP status was {http_status}")

            if actual_status != "success":
                reasons.append(f"status was {actual_status!r}")

            if actual_domain != "budget":
                reasons.append(f"domain was {actual_domain!r}")

            if actual_intent != expected_intent:
                reasons.append(
                    "intent was " f"{actual_intent!r}; expected " f"{expected_intent!r}"
                )

            if knowledge_used is not True:
                reasons.append("knowledge_used was not true")

            if financial_data_used is not True:
                reasons.append("financial_data_used was not true")

            if answer_contains not in answer:
                reasons.append(f"answer did not contain " f"{answer_contains!r}")

            success = len(reasons) == 0

            if success:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

            print()
            print(f"{index:02d}. [{status}] " f"{question}")
            print(f"    Intent: {actual_intent}")
            print(f"    Answer: {answer}")

            if reasons:
                for reason in reasons:
                    print(f"    ERROR: {reason}")

        except urllib.error.HTTPError as exc:
            failed += 1

            print()
            print(f"{index:02d}. [FAIL] " f"{question}")
            print(f"    HTTP ERROR: {exc.code}")

        except urllib.error.URLError as exc:
            failed += 1

            print()
            print(f"{index:02d}. [FAIL] " f"{question}")
            print(f"    CONNECTION ERROR: {exc.reason}")

        except Exception as exc:
            failed += 1

            print()
            print(f"{index:02d}. [FAIL] " f"{question}")
            print(f"    ERROR: {exc}")

    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"Total tests : {len(TEST_CASES)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print("=" * 78)

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
