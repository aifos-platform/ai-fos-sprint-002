import json
from typing import Any

from app.ai.providers.openai_provider import OpenAIProvider
from app.services.ai_question_engine import AIQuestionEngine


class DigitalCFOOrchestrator:
    """
    Orchestrate Digital CFO questions between:

    1. Digital CFO scope control.
    2. Verified deterministic AI-FOS intelligence.
    3. Verified organization-specific CFO context.
    4. AI usage authorization.
    5. OpenAI professional CFO reasoning.

    AI-FOS remains the source of truth for financial facts.

    OpenAI may interpret and synthesize verified AI-FOS
    intelligence, but it must not invent organization-specific
    financial information or silently recalculate validated
    financial results.

    Deterministic AI-FOS answers do not consume OpenAI usage.
    """

    def __init__(
        self,
        ai_question_engine: AIQuestionEngine,
        provider: Any | None = None,
        context_builder: Any | None = None,
        scope_guard: Any | None = None,
        usage_control: Any | None = None,
    ) -> None:
        self.ai_question_engine = ai_question_engine
        self.provider = provider
        self.context_builder = context_builder
        self.scope_guard = scope_guard
        self.usage_control = usage_control

    def answer(
        self,
        question: str,
        organisation_id: str,
    ) -> dict[str, Any]:
        """
        Answer a Digital CFO question.

        Priority:

        1. Block clearly out-of-scope requests before any
           deterministic or paid AI processing.

        2. Return a verified deterministic AI-FOS answer when
           one exists. This consumes no OpenAI allowance.

        3. If organization-specific CFO reasoning is required,
           load Verified CFO Context, authorize the paid AI
           request, then allow OpenAI to reason over validated
           AI-FOS outputs.

        4. Otherwise authorize and use OpenAI only for general
           professional finance / CFO knowledge.
        """

        # --------------------------------------------------
        # 0. Digital CFO scope control
        # --------------------------------------------------

        if self.scope_guard is not None:
            try:
                scope_result = self.scope_guard.evaluate(
                    question=question,
                )

            except Exception as exc:
                print(
                    "❌ Digital CFO scope guard failed:",
                    repr(exc),
                )

                scope_result = {
                    "allowed": False,
                    "reason": "scope_guard_error",
                }

            if not scope_result.get(
                "allowed",
                False,
            ):
                return {
                    "status": "blocked",
                    "question": question,
                    "organisation_id": organisation_id,
                    "intent": "out_of_scope",
                    "domain": "scope_control",
                    "answer": (
                        "AI-FOS Ask CFO is designed for finance, "
                        "accounting, budgeting, funding, grants, "
                        "financial management, governance, and "
                        "related CFO questions. Please ask a "
                        "question within the Digital CFO scope."
                    ),
                    "knowledge_used": False,
                    "financial_data_used": False,
                    "answer_source": "scope_guard",
                    "verified_financial_answer": False,
                    "verified_context_used": False,
                    "openai_used": False,
                    "scope_reason": (
                        scope_result.get("reason") or "scope_not_established"
                    ),
                }

        # --------------------------------------------------
        # 1. Deterministic AI-FOS question engine
        # --------------------------------------------------

        verified_result = self.ai_question_engine.answer(
            question=question,
            organisation_id=organisation_id,
        )

        status = self._normalize_text(verified_result.get("status"))

        intent = self._normalize_text(verified_result.get("intent"))

        # --------------------------------------------------
        # 2. Verified deterministic answer
        # --------------------------------------------------
        #
        # Important commercial rule:
        #
        # Deterministic AI-FOS answers are available even when
        # the organization's paid AI allowance is exhausted.
        # They therefore bypass AI usage authorization.
        #

        # --------------------------------------------------
        # CFO management-state mutation boundary
        # --------------------------------------------------
        #
        # CFO action commands are handled exclusively by the
        # deterministic AI-FOS mutation stack.
        #
        # Whether the command succeeds or is safely rejected,
        # it must never fall through to OpenAI reasoning.
        #
        # This prevents OpenAI from interpreting, retrying, or
        # independently mutating persisted organizational state.
        #

        if intent == "cfo_action_command":
            return verified_result

        # --------------------------------------------------
        # Normal verified deterministic answers
        # --------------------------------------------------

        if status == "success" and intent != "unknown":
            return verified_result

        # --------------------------------------------------
        # 3. Organization-specific CFO reasoning
        # --------------------------------------------------

        if self._requires_verified_context(
            question=question,
            organisation_id=organisation_id,
        ):
            context_result = self._build_verified_context(
                organisation_id=organisation_id
            )

            context = (
                context_result.get(
                    "context",
                    {},
                )
                if isinstance(
                    context_result,
                    dict,
                )
                else {}
            )

            context_status = self._normalize_text(
                (
                    context_result.get("status")
                    if isinstance(
                        context_result,
                        dict,
                    )
                    else None
                )
            )

            if context_status == "available" and context:
                authorization = self._authorize_openai_request(
                    organisation_id=organisation_id,
                    request_type=("verified_cfo_reasoning"),
                )

                if not authorization.get(
                    "allowed",
                    False,
                ):
                    return self._usage_blocked_response(
                        question=question,
                        organisation_id=organisation_id,
                        authorization=authorization,
                    )

                return self._answer_with_verified_context(
                    question=question,
                    organisation_id=organisation_id,
                    verified_result=verified_result,
                    context_result=context_result,
                    authorization=authorization,
                )

        # --------------------------------------------------
        # 4. General CFO knowledge fallback
        # --------------------------------------------------

        authorization = self._authorize_openai_request(
            organisation_id=organisation_id,
            request_type="general_cfo",
        )

        if not authorization.get(
            "allowed",
            False,
        ):
            return self._usage_blocked_response(
                question=question,
                organisation_id=organisation_id,
                authorization=authorization,
            )

        return self._answer_with_openai(
            question=question,
            organisation_id=organisation_id,
            verified_result=verified_result,
            verified_context_used=False,
            authorization=authorization,
        )

    def _authorize_openai_request(
        self,
        organisation_id: str,
        request_type: str,
    ) -> dict[str, Any]:
        """
        Authorize a paid OpenAI request.

        When no usage-control service has been injected, retain
        backward-compatible behavior and allow the request.

        Production wiring will inject AIUsageControlService.
        """

        if self.usage_control is None:
            return {
                "allowed": True,
                "reason": "usage_control_not_configured",
                "max_output_tokens": None,
            }

        try:
            result = self.usage_control.authorize(
                organisation_id=organisation_id,
                request_type=request_type,
            )

        except Exception as exc:
            print(
                "❌ AI usage authorization failed:",
                repr(exc),
            )

            # Fail closed for paid AI usage.
            return {
                "allowed": False,
                "reason": "usage_control_error",
                "max_output_tokens": None,
            }

        if not isinstance(
            result,
            dict,
        ):
            return {
                "allowed": False,
                "reason": "usage_control_error",
                "max_output_tokens": None,
            }

        return result

    def _usage_blocked_response(
        self,
        question: str,
        organisation_id: str,
        authorization: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Return a safe response when the organization's paid
        AI allowance does not authorize another OpenAI request.
        """

        reason = (
            self._normalize_text(authorization.get("reason"))
            or "ai_usage_not_authorized"
        )

        if reason == "daily_token_limit_reached":
            answer = (
                "Your organization's daily AI allowance has "
                "been reached. Verified AI-FOS financial "
                "answers remain available, but additional "
                "AI-generated CFO reasoning is temporarily "
                "unavailable until the daily allowance resets."
            )

        elif reason == "monthly_token_limit_reached":
            answer = (
                "Your organization's monthly AI allowance has "
                "been reached. Verified AI-FOS financial "
                "answers remain available, but additional "
                "AI-generated CFO reasoning is unavailable "
                "until the allowance resets or the plan limit "
                "is increased."
            )

        elif reason == "general_cfo_disabled":
            answer = (
                "General AI CFO guidance is not enabled for "
                "this organization. Verified AI-FOS financial "
                "questions remain available."
            )

        elif reason == "verified_cfo_reasoning_disabled":
            answer = (
                "AI-generated reasoning over verified "
                "organization financial data is not enabled "
                "for this organization. Deterministic AI-FOS "
                "financial answers remain available."
            )

        elif reason == "ai_disabled":
            answer = (
                "AI-generated CFO reasoning is currently "
                "disabled for this organization. Verified "
                "deterministic AI-FOS financial answers remain "
                "available."
            )

        else:
            answer = (
                "AI-generated CFO reasoning is currently "
                "unavailable under this organization's AI "
                "usage policy. Verified deterministic AI-FOS "
                "financial answers remain available."
            )

        return {
            "status": "blocked",
            "question": question,
            "organisation_id": organisation_id,
            "intent": "ai_usage_limit",
            "domain": "ai_usage_control",
            "answer": answer,
            "knowledge_used": False,
            "financial_data_used": False,
            "answer_source": "ai_usage_control",
            "verified_financial_answer": False,
            "verified_context_used": False,
            "openai_used": False,
            "usage_reason": reason,
        }

    def _build_verified_context(
        self,
        organisation_id: str,
    ) -> dict[str, Any]:
        """
        Build verified organization-specific CFO context.

        Context loading failures are treated safely as
        unavailable rather than breaking the Digital CFO.
        """

        if self.context_builder is None:
            return {
                "status": "not_available",
                "organisation_id": organisation_id,
                "context": {},
            }

        try:
            result = self.context_builder.build(organisation_id=organisation_id)

        except Exception as exc:
            print(
                "❌ Digital CFO context build failed:",
                repr(exc),
            )

            return {
                "status": "not_available",
                "organisation_id": organisation_id,
                "context": {},
            }

        if not isinstance(
            result,
            dict,
        ):
            return {
                "status": "not_available",
                "organisation_id": organisation_id,
                "context": {},
            }

        return result

    def _answer_with_verified_context(
        self,
        question: str,
        organisation_id: str,
        verified_result: dict[str, Any],
        context_result: dict[str, Any],
        authorization: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Use OpenAI to provide CFO-level interpretation and
        prioritization based only on verified AI-FOS outputs.

        OpenAI must preserve validated financial facts and must
        not independently recalculate financial results.
        """

        provider = self._get_provider()

        context = (
            context_result.get(
                "context",
                {},
            )
            or {}
        )

        available_sections = (
            context_result.get(
                "available_sections",
                [],
            )
            or []
        )

        missing_sections = (
            context_result.get(
                "missing_sections",
                [],
            )
            or []
        )

        source_files = (
            context_result.get(
                "source_files",
                {},
            )
            or {}
        )

        trust = (
            context_result.get(
                "trust",
                {},
            )
            or {}
        )

        instructions = (
            "You are the AI-FOS Digital CFO. "
            "You are providing professional CFO-level analysis "
            "for an organization using VERIFIED AI-FOS financial "
            "intelligence.\n\n"
            "STRICT FINANCIAL TRUST RULES:\n"
            "1. The financial figures and intelligence supplied "
            "in the VERIFIED AI-FOS CFO CONTEXT come from "
            "validated AI-FOS outputs and must be treated as the "
            "organization-specific source of truth.\n"
            "2. Do not invent, estimate, assume, fabricate, or "
            "silently fill missing organization-specific "
            "financial information.\n"
            "3. Do not recalculate validated AI-FOS financial "
            "results. You may compare, interpret, explain, "
            "prioritize, and reason over the supplied outputs, "
            "but do not replace AI-FOS calculations with your "
            "own calculations.\n"
            "4. Clearly distinguish verified financial facts "
            "from your professional interpretation, judgment, "
            "prioritization, or recommendation.\n"
            "5. If information needed for a conclusion is absent "
            "from the supplied context, explicitly say that the "
            "information is not available rather than guessing.\n"
            "6. Do not claim access to the raw General Ledger, "
            "transactions, source spreadsheets, bank statements, "
            "or other source documents unless such information "
            "is explicitly supplied. The context is intentionally "
            "limited to validated AI-FOS outputs.\n"
            "7. When recommending management actions, connect "
            "each important recommendation to the relevant "
            "verified evidence when possible.\n"
            "8. Focus on material CFO priorities such as "
            "liquidity, operating performance, financial health, "
            "budget control, funding sustainability, grants, "
            "risks, forecasts, opportunities, and management "
            "actions when those areas are present in the context.\n"
            "9. Do not present an AI-generated recommendation as "
            "a deterministic verified AI-FOS financial result.\n\n"
            "Respond in clear, professional CFO language. "
            "Prioritize the most material issues first. "
            "Be concise but sufficiently specific to support "
            "management decision-making."
        )

        verified_context_json = json.dumps(
            context,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        provenance_json = json.dumps(
            {
                "available_sections": (available_sections),
                "missing_sections": (missing_sections),
                "source_files": source_files,
                "trust": trust,
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        user_input = (
            f"Organization ID: {organisation_id}\n\n"
            f"User question:\n{question}\n\n"
            "AI-FOS deterministic result:\n"
            f"Status: {verified_result.get('status')}\n"
            f"Domain: {verified_result.get('domain')}\n"
            f"Intent: {verified_result.get('intent')}\n\n"
            "VERIFIED AI-FOS CFO CONTEXT:\n"
            f"{verified_context_json}\n\n"
            "VERIFIED CONTEXT PROVENANCE:\n"
            f"{provenance_json}\n\n"
            "Use the verified AI-FOS context above to answer "
            "the user's organization-specific CFO question. "
            "Do not introduce organization-specific financial "
            "facts that are not present in the supplied context."
        )

        try:
            answer_text = self._generate_openai_text(
                provider=provider,
                instructions=instructions,
                user_input=user_input,
                organisation_id=organisation_id,
                request_type="verified_cfo_reasoning",
                authorization=authorization,
            )

        except Exception as exc:
            print(
                "❌ Digital CFO verified-context "
                "OpenAI reasoning failed:",
                repr(exc),
            )

            return verified_result

        if not answer_text:
            return verified_result

        return {
            "status": "success",
            "question": question,
            "organisation_id": organisation_id,
            "intent": "verified_cfo_reasoning",
            "domain": "digital_cfo",
            "answer": answer_text,
            "knowledge_used": True,
            "financial_data_used": True,
            "answer_source": ("openai_verified_cfo_context"),
            "verified_financial_answer": False,
            "verified_context_used": True,
            "verified_context_sections": (available_sections),
            "verified_context_sources": (source_files),
        }

    def _answer_with_openai(
        self,
        question: str,
        organisation_id: str,
        verified_result: dict[str, Any],
        verified_context_used: bool = False,
        authorization: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Use OpenAI for general CFO reasoning when no verified
        deterministic AI-FOS answer is available.

        No organization-specific financial figures are supplied
        to OpenAI in this fallback mode.
        """

        provider = self._get_provider()

        instructions = (
            "You are the AI-FOS Digital CFO. "
            "Answer the user's finance, accounting, budgeting, "
            "funding, governance, management, and CFO questions "
            "using your general professional knowledge.\n\n"
            "STRICT FINANCIAL TRUST RULES:\n"
            "1. Do not invent, estimate, assume, or fabricate "
            "organization-specific financial figures.\n"
            "2. Do not claim to know organization-specific "
            "balances, budgets, grants, forecasts, risks, "
            "transactions, or performance unless verified "
            "AI-FOS data has explicitly been supplied.\n"
            "3. In this fallback request, no verified "
            "organization-specific financial figures have been "
            "supplied.\n"
            "4. You may explain financial concepts, accepted "
            "practices, management considerations, accounting "
            "principles, CFO reasoning, and possible actions.\n"
            "5. If the user's question requires organization-"
            "specific financial data to answer reliably, clearly "
            "say which information would be required.\n"
            "6. Clearly distinguish general professional guidance "
            "from verified AI-FOS organization facts.\n"
            "7. Never pretend that a general explanation is a "
            "verified AI-FOS financial result.\n\n"
            "Respond in clear, professional CFO language. "
            "Be concise but useful."
        )

        user_input = (
            f"Organization ID: {organisation_id}\n\n"
            f"User question:\n{question}\n\n"
            "AI-FOS deterministic result:\n"
            f"Status: {verified_result.get('status')}\n"
            f"Domain: {verified_result.get('domain')}\n"
            f"Intent: {verified_result.get('intent')}\n\n"
            "No organization-specific financial figures are "
            "being supplied to the OpenAI fallback."
        )

        try:
            answer_text = self._generate_openai_text(
                provider=provider,
                instructions=instructions,
                user_input=user_input,
                organisation_id=organisation_id,
                request_type="general_cfo",
                authorization=authorization,
            )

        except Exception as exc:
            print(
                "❌ Digital CFO OpenAI fallback failed:",
                repr(exc),
            )

            return verified_result

        if not answer_text:
            return verified_result

        original_intent = self._normalize_text(verified_result.get("intent"))

        original_domain = self._normalize_text(verified_result.get("domain"))

        return {
            "status": "success",
            "question": question,
            "organisation_id": organisation_id,
            "intent": (
                "general_cfo"
                if original_intent
                in {
                    "",
                    "unknown",
                }
                else original_intent
            ),
            "domain": (
                "general_cfo"
                if original_domain
                in {
                    "",
                    "unknown",
                }
                else original_domain
            ),
            "answer": answer_text,
            "knowledge_used": True,
            "financial_data_used": False,
            "answer_source": "openai_general_cfo",
            "verified_financial_answer": False,
            "verified_context_used": (verified_context_used),
        }


    def _generate_openai_text(
        self,
        provider: Any,
        instructions: str,
        user_input: str,
        organisation_id: str,
        request_type: str,
        authorization: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate OpenAI text with usage metering when the provider
        supports it.

        Older or test providers that expose only generate_text()
        remain supported.
        """

        authorization = (
            authorization
            if isinstance(
                authorization,
                dict,
            )
            else {}
        )

        max_output_tokens = authorization.get("max_output_tokens")

        usage_method = getattr(
            provider,
            "generate_text_with_usage",
            None,
        )

        if callable(usage_method):
            result = usage_method(
                instructions=instructions,
                user_input=user_input,
                max_output_tokens=max_output_tokens,
            )

            if not isinstance(
                result,
                dict,
            ):
                return str(result or "").strip()

            usage = (
                result.get(
                    "usage",
                    {},
                )
                or {}
            )

            if self.usage_control is not None and isinstance(
                usage,
                dict,
            ):
                try:
                    self.usage_control.record_usage(
                        organisation_id=organisation_id,
                        request_type=request_type,
                        model=str(
                            result.get(
                                "model",
                                "",
                            )
                            or ""
                        ),
                        input_tokens=usage.get(
                            "input_tokens",
                            0,
                        ),
                        output_tokens=usage.get(
                            "output_tokens",
                            0,
                        ),
                        total_tokens=usage.get(
                            "total_tokens",
                            0,
                        ),
                        status="success",
                    )

                except Exception as exc:
                    print(
                        "❌ AI usage recording failed:",
                        repr(exc),
                    )

            return str(
                result.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

        answer = provider.generate_text(
            instructions=instructions,
            user_input=user_input,
        )

        return str(answer or "").strip()

    def _requires_verified_context(
        self,
        question: str,
        organisation_id: str,
    ) -> bool:
        """
        Determine whether an unsupported question is asking
        for organization-specific CFO reasoning.

        This remains intentionally conservative.
        """

        cleaned_question = str(question or "").strip().lower()

        if not cleaned_question:
            return False

        organisation_token = str(organisation_id or "").strip().lower()

        organization_specific_phrases = (
            "our financial",
            "our current financial",
            "our finances",
            "our budget",
            "our cash",
            "our liquidity",
            "our funding",
            "our grants",
            "our risks",
            "our forecast",
            "our financial health",
            "our financial position",
            "our financial situation",
            "our organization",
            "our organisation",
            "our performance",
            "based on our",
            "based on the organization",
            "based on the organisation",
            "for our organization",
            "for our organisation",
            "what should we focus",
            "what should management focus",
            "what should management prioritize",
            "what should management prioritise",
        )

        if any(phrase in cleaned_question for phrase in organization_specific_phrases):
            return True

        if organisation_token and organisation_token in cleaned_question:
            organization_reasoning_terms = (
                "financial",
                "budget",
                "cash",
                "liquidity",
                "funding",
                "grant",
                "risk",
                "forecast",
                "performance",
                "management",
                "focus",
                "priority",
                "prioritize",
                "prioritise",
                "situation",
                "position",
                "health",
            )

            if any(term in cleaned_question for term in organization_reasoning_terms):
                return True

        return False

    def _get_provider(
        self,
    ) -> Any:
        if self.provider is not None:
            return self.provider

        return OpenAIProvider()

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str:
        return str(value or "").strip().lower()
