import json
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://127.0.0.1:8000"
ORGANISATION_ID = "acss"


TEST_CASES = [
    # ---------------------------------
    # Cash Position
    # ---------------------------------
    {
        "question": "How much cash do we have?",
        "domain": "cash",
        "intent": "cash_position",
        "require_financial_data": True,
    },
    {
        "question": "What is our cash position?",
        "domain": "cash",
        "intent": "cash_position",
        "require_financial_data": True,
    },
    {
        "question": "What is our cash balance?",
        "domain": "cash",
        "intent": "cash_position",
        "require_financial_data": True,
    },
    {
        "question": "How much cash is available?",
        "domain": "cash",
        "intent": "cash_position",
        "require_financial_data": True,
    },
    {
        "question": "How much available cash do we have?",
        "domain": "cash",
        "intent": "cash_position",
        "require_financial_data": True,
    },

    # ---------------------------------
    # Liquidity Intelligence
    # ---------------------------------
    {
        "question": "What is our cash runway?",
        "domain": "liquidity",
        "intent": "cash_runway",
        "require_financial_data": True,
        "answer_contains": "11.44",
    },

    # ---------------------------------
    # Financial Health
    # ---------------------------------
    {
        "question": "What is our financial health?",
        "domain": "financial_health",
        "intent": "financial_health",
        "require_financial_data": True,
    },
    {
        "question": "Are we financially healthy?",
        "domain": "financial_health",
        "intent": "financial_health",
        "require_financial_data": True,
    },
    {
        "question": "How healthy are our finances?",
        "domain": "financial_health",
        "intent": "financial_health",
        "require_financial_data": True,
    },
    {
        "question": "How healthy is our financial position?",
        "domain": "financial_health",
        "intent": "financial_health",
        "require_financial_data": True,
    },

    # ---------------------------------
    # Core Financial Facts
    # ---------------------------------
    {
        "question": "What is our net surplus?",
        "domain": "financial",
        "intent": "net_profit",
        "require_financial_data": True,
    },
    {
        "question": "What are our total expenses?",
        "domain": "financial",
        "intent": "expenses",
        "require_financial_data": True,
        "answer_contains": "9,278,726.83",
    },

    # ---------------------------------
    # Cash Flow
    # ---------------------------------
    {
        "question": "What is our operating cash flow?",
        "domain": "cash_flow",
        "intent": "operating_cash_flow",
        "require_financial_data": True,
    },
    {
        "question": "How much cash comes from operations?",
        "domain": "cash_flow",
        "intent": "operating_cash_flow",
        "require_financial_data": True,
    },
    {
        "question": "What is our investing cash flow?",
        "domain": "cash_flow",
        "intent": "investing_cash_flow",
        "require_financial_data": True,
    },
    {
        "question": "What is our financing cash flow?",
        "domain": "cash_flow",
        "intent": "financing_cash_flow",
        "require_financial_data": True,
    },
    {
        "question": "What is the net change in cash?",
        "domain": "cash_flow",
        "intent": "net_change_in_cash",
        "require_financial_data": True,
    },
]


def ask_ai_fos(question: str) -> dict:
    encoded_question = urllib.parse.quote(question)

    url = (
        f"{BASE_URL}/ask/{ORGANISATION_ID}"
        f"?question={encoded_question}"
    )

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
    print("AI-FOS LIVE FINANCIAL / CASH Q&A TEST SUITE")
    print("=" * 78)
    print(f"Organisation: {ORGANISATION_ID}")
    print(f"API: {BASE_URL}")
    print("=" * 78)

    for index, test_case in enumerate(
        TEST_CASES,
        start=1,
    ):
        question = test_case["question"]
        expected_domain = test_case["domain"]
        expected_intent = test_case["intent"]
        require_financial_data = test_case[
            "require_financial_data"
        ]
        answer_contains = test_case.get(
            "answer_contains"
        )

        reasons = []

        try:
            result = ask_ai_fos(question)

            http_status = result["http_status"]
            body = result["body"]

            actual_status = body.get("status")
            actual_domain = body.get("domain")
            actual_intent = body.get("intent")
            knowledge_used = body.get("knowledge_used")
            financial_data_used = body.get(
                "financial_data_used"
            )
            answer = str(body.get("answer", ""))

            if http_status != 200:
                reasons.append(
                    f"HTTP status was {http_status}"
                )

            if actual_status != "success":
                reasons.append(
                    f"status was {actual_status!r}"
                )

            if actual_domain != expected_domain:
                reasons.append(
                    f"domain was {actual_domain!r}; "
                    f"expected {expected_domain!r}"
                )

            if actual_intent != expected_intent:
                reasons.append(
                    f"intent was {actual_intent!r}; "
                    f"expected {expected_intent!r}"
                )

            if knowledge_used is not True:
                reasons.append(
                    "knowledge_used was not true"
                )

            if (
                require_financial_data
                and financial_data_used is not True
            ):
                reasons.append(
                    "financial_data_used was not true"
                )

            if (
                answer_contains is not None
                and answer_contains not in answer
            ):
                reasons.append(
                    f"answer did not contain "
                    f"{answer_contains!r}"
                )

            success = len(reasons) == 0

            if success:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

            print()
            print(
                f"{index:02d}. [{status}] "
                f"{question}"
            )
            print(
                f"    Domain: {actual_domain}"
            )
            print(
                f"    Intent: {actual_intent}"
            )
            print(
                f"    Answer: {answer}"
            )

            if reasons:
                for reason in reasons:
                    print(
                        f"    ERROR: {reason}"
                    )

        except urllib.error.HTTPError as exc:
            failed += 1

            print()
            print(
                f"{index:02d}. [FAIL] "
                f"{question}"
            )
            print(
                f"    HTTP ERROR: {exc.code}"
            )

        except urllib.error.URLError as exc:
            failed += 1

            print()
            print(
                f"{index:02d}. [FAIL] "
                f"{question}"
            )
            print(
                f"    CONNECTION ERROR: {exc.reason}"
            )

        except Exception as exc:
            failed += 1

            print()
            print(
                f"{index:02d}. [FAIL] "
                f"{question}"
            )
            print(
                f"    ERROR: {exc}"
            )

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