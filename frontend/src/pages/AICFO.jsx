import {
  useEffect,
  useMemo,
  useState,
} from "react";
import ReactMarkdown from "react-markdown";

import api from "../api";
import AppShell from "../components/AppShell";
import "./AICFO.css";


function AICFO({
  readiness,
  organizationList,
  currentOrganization,
  setCurrentOrganization,
}) {
  const [catalog, setCatalog] = useState([]);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);

  const [selectedCategory, setSelectedCategory] = useState("Suggested");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);

  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");


  const organisationId =
    currentOrganization?.id ?? "acss";

  const organisationName =
    currentOrganization?.name ?? "ACSS";

  const hasFinancialIntelligence =
    readiness?.has_executive_dashboard === true;


  useEffect(() => {
    let cancelled = false;

    setQuestion("");
    setAnswer(null);
    setError("");
    setSelectedCategory("Suggested");

    if (!hasFinancialIntelligence) {
      setCatalog([]);
      setSuggestedQuestions([]);
      setLoadingQuestions(false);

      return () => {
        cancelled = true;
      };
    }

    const loadQuestions = async () => {
      setLoadingQuestions(true);
      setError("");

      try {
        const [
          catalogResponse,
          suggestedResponse,
        ] = await Promise.all([
          api.get("/ai-cfo/questions"),
          api.get(
            `/ai-cfo/suggested/${organisationId}`
          ),
        ]);

        if (cancelled) {
          return;
        }

        setCatalog(
          catalogResponse.data?.categories ?? []
        );

        setSuggestedQuestions(
          suggestedResponse.data?.suggested_questions ?? []
        );

      } catch (requestError) {
        console.error(
          "AI CFO question load error:",
          requestError
        );

        if (!cancelled) {
          setError(
            "AI CFO questions could not be loaded."
          );
        }

      } finally {
        if (!cancelled) {
          setLoadingQuestions(false);
        }
      }
    };

    loadQuestions();

    return () => {
      cancelled = true;
    };
  }, [
    organisationId,
    hasFinancialIntelligence,
  ]);


  const categories = useMemo(() => {
    return [
      "Suggested",
      ...catalog.map(
        (category) => category.category
      ),
    ];
  }, [catalog]);


  const visibleQuestions = useMemo(() => {
    if (selectedCategory === "Suggested") {
      return suggestedQuestions;
    }

    const selectedCatalogCategory =
      catalog.find(
        (category) =>
          category.category === selectedCategory
      );

    return (
      selectedCatalogCategory?.questions ?? []
    );
  }, [
    selectedCategory,
    suggestedQuestions,
    catalog,
  ]);


  const askQuestion = async (
    questionText
  ) => {
    if (!hasFinancialIntelligence) {
      return;
    }

    const cleanQuestion =
      questionText?.trim();

    if (!cleanQuestion) {
      return;
    }

    setQuestion(cleanQuestion);
    setAsking(true);
    setError("");
    setAnswer(null);

    try {
      const response = await api.get(
        `/ask/${organisationId}`,
        {
          params: {
            question: cleanQuestion,
          },
        }
      );

      setAnswer(
        response.data ?? null
      );

    } catch (requestError) {
      console.error(
        "AI CFO answer error:",
        requestError
      );

      setError(
        "AI CFO could not answer this question."
      );

    } finally {
      setAsking(false);
    }
  };


  const handleSubmit = async (
    event
  ) => {
    event.preventDefault();

    if (!hasFinancialIntelligence) {
      return;
    }

    await askQuestion(
      question
    );
  };


  return (
    <AppShell
      eyebrow="Financial intelligence"
      title="AI CFO"
      organizationList={organizationList}
      currentOrganization={currentOrganization}
      setCurrentOrganization={setCurrentOrganization}
      mainClassName="ai-cfo-main"
    >
        {!hasFinancialIntelligence ? (

          <section className="ai-cfo-section">
            <div className="ai-cfo-hero">
              <div>
                <p className="card-label">
                  Organization readiness
                </p>

                <h3>
                  AI CFO not available yet
                </h3>

                <p className="ai-cfo-intro">
                  {organisationName} does not yet have
                  validated financial intelligence
                  available in AI-FOS. Upload and process
                  the organization&apos;s financial data
                  to activate the Digital CFO.
                </p>
              </div>
            </div>
          </section>

        ) : (

          <section className="ai-cfo-section">

            <div className="ai-cfo-hero">
              <div>
                <p className="card-label">
                  Digital CFO
                </p>

                <h3>
                  What would you like to know?
                </h3>

                <p className="ai-cfo-intro">
                  Ask AI-FOS about financial health,
                  liquidity, funding, budgets, grants,
                  risks, performance, and management
                  priorities.
                </p>
              </div>

              <div className="ai-cfo-status">
                <span className="ai-cfo-status-dot" />

                Financial intelligence ready
              </div>
            </div>


            {error && (
              <div className="ai-cfo-error">
                {error}
              </div>
            )}


            <div className="ai-cfo-category-tabs">
              {categories.map(
                (category) => (
                  <button
                    key={category}
                    type="button"
                    className={`ai-cfo-category-tab ${selectedCategory === category
                      ? "active"
                      : ""
                      }`}
                    onClick={() =>
                      setSelectedCategory(
                        category
                      )
                    }
                  >
                    {category}
                  </button>
                )
              )}
            </div>


            <section className="ai-cfo-question-section">

              <div className="ai-cfo-section-heading">
                <div>
                  <p className="card-label">
                    {selectedCategory === "Suggested"
                      ? "Suggested for you"
                      : selectedCategory}
                  </p>

                  <h3>
                    {selectedCategory === "Suggested"
                      ? "Questions based on your financial position"
                      : "Explore your financial data"}
                  </h3>
                </div>
              </div>


              {loadingQuestions ? (
                <p className="card-note">
                  Loading AI CFO questions...
                </p>
              ) : visibleQuestions.length > 0 ? (
                <div className="ai-cfo-question-grid">

                  {visibleQuestions.map(
                    (item, index) => {
                      const questionText =
                        typeof item === "string"
                          ? item
                          : item.question;

                      const itemId =
                        typeof item === "string"
                          ? `${selectedCategory}-${index}`
                          : item.id ??
                          `${selectedCategory}-${index}`;

                      return (
                        <button
                          key={itemId}
                          type="button"
                          className="ai-cfo-question-card"
                          onClick={() =>
                            askQuestion(
                              questionText
                            )
                          }
                        >
                          <span className="ai-cfo-question-icon">
                            ?
                          </span>

                          <span className="ai-cfo-question-content">
                            <strong>
                              {questionText}
                            </strong>

                            {item?.reason && (
                              <small>
                                {item.reason}
                              </small>
                            )}
                          </span>
                        </button>
                      );
                    }
                  )}

                </div>
              ) : (
                <p className="card-note">
                  No questions are available in this category.
                </p>
              )}

            </section>


            <section className="ai-cfo-answer-section">

              <div className="ai-cfo-section-heading">
                <div>
                  <p className="card-label">
                    Ask anything
                  </p>

                  <h3>
                    Ask your Digital CFO
                  </h3>
                </div>
              </div>


              <form
                className="ai-cfo-form"
                onSubmit={handleSubmit}
              >
                <textarea
                  className="ai-cfo-input"
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value
                    )
                  }
                  placeholder="Ask a financial question..."
                  rows={3}
                />

                <div className="ai-cfo-form-footer">

                  <p className="card-note">
                    Answers use AI-FOS financial
                    intelligence for {organisationName}.
                  </p>

                  <button
                    className="ai-cfo-submit"
                    type="submit"
                    disabled={
                      asking ||
                      !question.trim()
                    }
                  >
                    {asking
                      ? "Analyzing..."
                      : "Ask AI CFO"}
                  </button>

                </div>
              </form>


              {asking && (
                <div className="ai-cfo-answer-card">
                  <p className="card-label">
                    AI CFO
                  </p>

                  <p>
                    Analyzing the financial data...
                  </p>
                </div>
              )}


              {!asking && answer && (
                <div className="ai-cfo-answer-card">

                  <div className="ai-cfo-answer-header">
                    <div>
                      <p className="card-label">
                        AI CFO response
                      </p>

                      <h3>
                        {answer.question ??
                          question}
                      </h3>
                    </div>

                    <span className="ai-cfo-domain-badge">
                      {answer.answer_source ===
                        "openai_verified_cfo_context"
                        ? "AI CFO Analysis · Verified AI-FOS Data"
                        : answer.answer_source ===
                          "openai_general_cfo"
                          ? "General CFO Guidance"
                          : answer.answer_source ===
                            "scope_guard"
                            ? "Out of Scope"
                            : answer.answer_source ===
                              "ai_usage_control"
                              ? "AI Usage Limit"
                              : "Verified AI-FOS Answer"}
                    </span>
                  </div>


                  <div className="ai-cfo-answer-text">
                    <ReactMarkdown>
                      {answer.answer ?? "No answer was returned."}
                    </ReactMarkdown>
                  </div>


                  <div className="ai-cfo-answer-meta">

                    {answer.intent && (
                      <span>
                        Intent: {answer.intent}
                      </span>
                    )}

                    {answer.knowledge_used ===
                      true && (
                        <span>
                          Organization knowledge used
                        </span>
                      )}

                    {answer.financial_data_used ===
                      true && (
                        <span>
                          Financial data used
                        </span>
                      )}

                  </div>

                </div>
              )}

            </section>

          </section>

        )}

    </AppShell>
  );
}


export default AICFO;