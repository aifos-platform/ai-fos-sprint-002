import AppShell from "../components/AppShell";

const categoryLabels = {
  operating_performance: "Operating Performance",
  financial_position: "Financial Position",
  liquidity: "Liquidity",
  budget_control: "Budget Control",
  funding_and_grant_health:
    "Funding & Grant Health",
};

function FinancialHealth({
  health,
  readiness,
  organizationList,
  currentOrganization,
  setCurrentOrganization,
}) {
  const financialHealthUnavailable =
    readiness &&
    !readiness.has_financial_health;

  const categories =
    health?.categories ?? {};

  const score =
    health?.score ?? null;

  const maximum =
    health?.maximum ?? 100;

  const rating =
    health?.rating ?? "Not available";

  const scorePercentage =
    score != null && maximum
      ? Math.min(
          Math.max(
            (score / maximum) * 100,
            0
          ),
          100
        )
      : 0;

  const fundingMetrics =
    categories
      ?.funding_and_grant_health
      ?.metrics ?? {};

  return (
    <AppShell
      eyebrow="Financial intelligence"
      title="Financial Health"
      organizationList={organizationList}
      currentOrganization={currentOrganization}
      setCurrentOrganization={
        setCurrentOrganization
      }
    >
      {financialHealthUnavailable && (
        <div className="readiness-state-card">
          <p className="card-label">
            Organization readiness
          </p>

          <h2>
            Financial Health not available yet
          </h2>

          <p className="card-note">
            {currentOrganization?.name} does not
            yet have a processed Financial Health
            model in AI-FOS.
          </p>

          <p className="card-note">
            Upload and process the
            organization&apos;s financial data to
            activate Financial Health analysis.
          </p>
        </div>
      )}

      {readiness?.has_financial_health && (
        <section className="financial-health-page">
          <div className="financial-health-hero">
            <div className="financial-health-score-card">
              <div>
                <p className="card-label">
                  Overall Financial Health
                </p>

                <div className="financial-health-score">
                  <span className="score-number">
                    {score ?? "--"}
                  </span>

                  <span className="score-maximum">
                    / {maximum}
                  </span>
                </div>

                <span
                  className={`health-rating ${rating
                    .toLowerCase()
                    .replaceAll(" ", "-")}`}
                >
                  {rating}
                </span>
              </div>

              <div
                className="health-score-ring"
                style={{
                  background: `conic-gradient(
                    #183153 ${scorePercentage}%,
                    #e8edf3 ${scorePercentage}% 100%
                  )`,
                }}
              >
                <div className="health-score-ring-inner">
                  <strong>
                    {score ?? "--"}
                  </strong>

                  <span>
                    score
                  </span>
                </div>
              </div>
            </div>

            <div className="financial-health-summary-card">
              <p className="card-label">
                CFO Interpretation
              </p>

              <h3>
                {rating === "Fair"
                  ? "Financial position requires management attention"
                  : `Financial health is rated ${rating}`}
              </h3>

              <p>
                AI-FOS evaluates operating
                performance, financial position,
                liquidity, budget control, and
                funding & grant health using
                validated financial intelligence.
              </p>
            </div>
          </div>

          <div className="health-category-grid">
            {Object.entries(categories).map(
              ([key, category]) => {
                const categoryPercentage =
                  category?.maximum
                    ? (
                        category.score /
                        category.maximum
                      ) * 100
                    : 0;

                return (
                  <article
                    className="health-category-card"
                    key={key}
                  >
                    <div className="health-category-header">
                      <div>
                        <p className="card-label">
                          {categoryLabels[key] ??
                            key}
                        </p>

                        <h3>
                          {category.score}
                          <span>
                            {" "}
                            / {category.maximum}
                          </span>
                        </h3>
                      </div>

                      <div className="health-category-percent">
                        {Math.round(
                          categoryPercentage
                        )}
                        %
                      </div>
                    </div>

                    <div className="health-progress-track">
                      <div
                        className="health-progress-bar"
                        style={{
                          width: `${Math.min(
                            Math.max(
                              categoryPercentage,
                              0
                            ),
                            100
                          )}%`,
                        }}
                      />
                    </div>

                    <p className="health-category-reason">
                      {category.reason}
                    </p>
                  </article>
                );
              }
            )}
          </div>

          <section className="health-detail-section">
            <div className="health-section-heading">
              <div>
                <p className="eyebrow">
                  Funding health
                </p>

                <h3>
                  Funding & Grant Indicators
                </h3>
              </div>
            </div>

            <div className="health-metric-grid">
              <div className="health-metric-card">
                <p>
                  Remaining Requirement
                </p>

                <strong>
                  {fundingMetrics
                    .remaining_requirement != null
                    ? `$${fundingMetrics
                        .remaining_requirement
                        .toLocaleString(
                          undefined,
                          {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          }
                        )}`
                    : "--"}
                </strong>
              </div>

              <div className="health-metric-card">
                <p>
                  Applied Secured Funding
                </p>

                <strong>
                  {fundingMetrics
                    .applied_secured_funding != null
                    ? `$${fundingMetrics
                        .applied_secured_funding
                        .toLocaleString(
                          undefined,
                          {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          }
                        )}`
                    : "--"}
                </strong>
              </div>

              <div className="health-metric-card">
                <p>
                  Funding Gap
                </p>

                <strong>
                  {fundingMetrics
                    .funding_gap != null
                    ? `$${fundingMetrics
                        .funding_gap
                        .toLocaleString(
                          undefined,
                          {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          }
                        )}`
                    : "--"}
                </strong>
              </div>

              <div className="health-metric-card">
                <p>
                  Funding Coverage
                </p>

                <strong>
                  {fundingMetrics
                    .applied_coverage_percentage !=
                  null
                    ? `${fundingMetrics
                        .applied_coverage_percentage
                        .toFixed(2)}%`
                    : "--"}
                </strong>
              </div>
            </div>

            <div className="health-evidence-grid">
              <div className="health-evidence-card">
                <span>
                  {fundingMetrics
                    .matched_requirement_count ??
                    "--"}
                </span>

                <p>
                  Requirements with validated
                  eligible secured funding
                </p>
              </div>

              <div className="health-evidence-card">
                <span>
                  {fundingMetrics
                    .unmatched_requirement_count ??
                    "--"}
                </span>

                <p>
                  Requirements without validated
                  eligible secured funding
                </p>
              </div>

              <div className="health-evidence-card">
                <span>
                  {fundingMetrics
                    .actual_only_grant_count ??
                    "--"}
                </span>

                <p>
                  Grants with actuals but no
                  identified budget
                </p>
              </div>

              <div className="health-evidence-card">
                <span>
                  {fundingMetrics
                    .budget_only_grant_count ??
                    "--"}
                </span>

                <p>
                  Grants with budget but no actual
                  activity
                </p>
              </div>
            </div>
          </section>

          <div className="health-methodology-note">
            <strong>
              Evidence-based score
            </strong>

            <p>
              Financial Health is displayed from
              the validated AI-FOS Financial
              Health engine. The frontend does
              not recalculate the score or its
              category assessments.
            </p>
          </div>
        </section>
      )}
    </AppShell>
  );
}

export default FinancialHealth;