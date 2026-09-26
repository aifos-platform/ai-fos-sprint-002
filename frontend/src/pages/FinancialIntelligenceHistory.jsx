import {
  useCallback,
  useEffect,
  useState,
} from "react";

import api from "../api";
import AppShell from "../components/AppShell";


function FinancialIntelligenceHistory({
  organizationList,
  currentOrganization,
  setCurrentOrganization,
}) {
  const [
    historyData,
    setHistoryData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  const loadHistory = useCallback(
    async () => {
      if (!currentOrganization?.id) {
        setHistoryData(null);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          (
            `/organisations/${currentOrganization.id}` +
            "/financial-intelligence-history"
          )
        );

        setHistoryData(
          response.data ?? null
        );

      } catch (requestError) {
        console.error(
          "Financial Intelligence History load error:",
          requestError
        );

        setHistoryData(null);

        setError(
          "Could not load Financial Intelligence History."
        );

      } finally {
        setLoading(false);
      }
    },
    [currentOrganization?.id]
  );


  useEffect(() => {
    loadHistory();
  }, [
    currentOrganization?.id,
    loadHistory,
  ]);


  const latestChange =
    historyData?.latest_change ??
    {};

  const historicalDecision =
    historyData?.historical_decision ??
    {};

  const snapshots =
    historyData?.snapshots ??
    [];

  const evidenceSummary =
    latestChange?.evidence_summary ??
    {};

  const metricChange =
    latestChange?.metric_change ??
    {};

  const riskChange =
    latestChange?.risk_change ??
    {};

  const comparisons =
    metricChange?.comparisons ??
    [];

  const riskMovements =
    riskChange?.movements ??
    [];

  const riskSummary =
    riskChange?.summary ??
    {};

  const priorities =
    historicalDecision?.priorities ??
    [];

  const improvements =
    historicalDecision?.improvements ??
    [];


  const formatLabel = (value) =>
    String(
      value ??
      ""
    )
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );


  const formatDateTime = (value) => {
    if (!value) {
      return "Not available";
    }

    const date = new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return String(value);
    }

    return date.toLocaleString();
  };


  const formatValue = (
    value,
    unit
  ) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "N/A";
    }

    if (
      typeof value === "number"
    ) {
      const formatted =
        new Intl.NumberFormat(
          undefined,
          {
            maximumFractionDigits: 2,
          }
        ).format(value);

      if (
        unit === "months"
      ) {
        return `${formatted} months`;
      }

      if (
        unit === "points"
      ) {
        return `${formatted} points`;
      }

      if (
        unit === "percentage"
      ) {
        return `${formatted}%`;
      }

      return formatted;
    }

    return String(value);
  };


  const priorityClass = (priority) => {
    const normalized =
      String(priority ?? "")
        .trim()
        .toLowerCase();

    if (normalized === "critical") {
      return "critical";
    }

    if (normalized === "high") {
      return "high";
    }

    if (normalized === "medium") {
      return "medium";
    }

    return "low";
  };


  const signalClass = (signal) => {
    const normalized =
      String(signal ?? "")
        .trim()
        .toLowerCase();

    if (
      normalized === "deteriorated" ||
      normalized === "decreased"
    ) {
      return "negative";
    }

    if (
      normalized === "improved"
    ) {
      return "positive";
    }

    return "";
  };


  const movementTitle = (
    movement
  ) => {
    const type =
      String(
        movement?.movement ??
        ""
      );

    if (
      type === "new"
    ) {
      return (
        movement?.current?.title ??
        "New financial risk"
      );
    }

    if (
      type === "resolved"
    ) {
      return (
        movement?.previous?.title ??
        "Resolved financial risk"
      );
    }

    return (
      movement?.current?.title ??
      movement?.previous?.title ??
      "Financial risk"
    );
  };


  const movementSeverity = (
    movement
  ) =>
    (
      movement?.current?.severity ??
      movement?.previous?.severity ??
      "Medium"
    );


  const hasAvailableHistory =
    historyData?.status === "available";


  return (
    <AppShell
      eyebrow="Historical financial intelligence"
      title="Financial Intelligence History"
      organizationList={organizationList}
      currentOrganization={currentOrganization}
      setCurrentOrganization={setCurrentOrganization}
    >
        {error && (
          <section className="card">
            <p className="card-note negative">
              {error}
            </p>
          </section>
        )}


        {loading ? (

          <section className="card">
            <p className="card-note">
              Loading historical financial intelligence...
            </p>
          </section>

        ) : !hasAvailableHistory ? (

          <section className="card">

            <p className="card-label">
              Historical Intelligence
            </p>

            <h3>
              More financial history is required
            </h3>

            <p className="card-note">
              AI-FOS needs at least two completed
              verified financial processing snapshots
              before it can compare financial movement
              and identify change-driven management
              priorities.
            </p>

            <div
              className="action-attention-list"
              style={{
                marginTop: "20px",
              }}
            >
              <div className="attention-row">
                <span>
                  Available snapshots
                </span>

                <strong>
                  {historyData?.snapshot_count ?? 0}
                </strong>
              </div>

              <div className="attention-row">
                <span>
                  Required
                </span>

                <strong>
                  2
                </strong>
              </div>
            </div>

          </section>

        ) : (

          <>

            <section className="action-summary-grid">

              <article className="card">
                <p className="card-label">
                  Historical Direction
                </p>

                <h3
                  className={signalClass(
                    latestChange
                      ?.overall_direction
                  )}
                >
                  {formatLabel(
                    latestChange
                      ?.overall_direction ??
                    "Stable"
                  )}
                </h3>

                <p className="card-note">
                  Latest verified movement
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Management Attention
                </p>

                <h3>
                  {formatLabel(
                    latestChange
                      ?.management_attention ??
                    "Monitor"
                  )}
                </h3>

                <p className="card-note">
                  Deterministic historical assessment
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Highest Priority
                </p>

                <h3>
                  {
                    historicalDecision
                      ?.highest_priority ??
                    "Low"
                  }
                </h3>

                <p className="card-note">
                  Change-driven management priority
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Historical Signal
                </p>

                <h3>
                  {formatLabel(
                    historicalDecision
                      ?.historical_signal ??
                    "Monitor"
                  )}
                </h3>

                <p className="card-note">
                  Management response level
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Negative Evidence
                </p>

                <h3 className="negative">
                  {
                    evidenceSummary
                      ?.negative_evidence_count ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Deteriorations and new risks
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Positive Evidence
                </p>

                <h3 className="positive">
                  {
                    evidenceSummary
                      ?.positive_evidence_count ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Improvements and resolved risks
                </p>
              </article>

            </section>


            <section className="action-center-grid">

              <article className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Previous Verified Position
                    </p>

                    <h3>
                      Historical baseline
                    </h3>
                  </div>
                </div>

                <div className="action-attention-list">

                  <div className="attention-row">
                    <span>
                      Snapshot
                    </span>

                    <strong>
                      {
                        latestChange
                          ?.snapshot_a
                          ?.snapshot_id ??
                        "N/A"
                      }
                    </strong>
                  </div>

                  <div className="attention-row">
                    <span>
                      Captured
                    </span>

                    <strong>
                      {formatDateTime(
                        latestChange
                          ?.snapshot_a
                          ?.captured_at
                      )}
                    </strong>
                  </div>

                </div>

              </article>


              <article className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Latest Verified Position
                    </p>

                    <h3>
                      Current comparison point
                    </h3>
                  </div>
                </div>

                <div className="action-attention-list">

                  <div className="attention-row">
                    <span>
                      Snapshot
                    </span>

                    <strong>
                      {
                        latestChange
                          ?.snapshot_b
                          ?.snapshot_id ??
                        "N/A"
                      }
                    </strong>
                  </div>

                  <div className="attention-row">
                    <span>
                      Captured
                    </span>

                    <strong>
                      {formatDateTime(
                        latestChange
                          ?.snapshot_b
                          ?.captured_at
                      )}
                    </strong>
                  </div>

                </div>

              </article>

            </section>


            <section className="card">

              <div className="card-header">
                <div>
                  <p className="card-label">
                    Financial Movement
                  </p>

                  <h3>
                    What changed financially?
                  </h3>

                  <p className="card-note">
                    Comparison of verified metrics between
                    the latest two Financial Intelligence
                    snapshots.
                  </p>
                </div>

                <span className="action-count">
                  {comparisons.length} metrics
                </span>
              </div>


              {comparisons.length === 0 ? (

                <p className="card-note">
                  No comparable financial metrics are
                  available.
                </p>

              ) : (

                <div className="action-table-wrap">

                  <table className="action-table">

                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th>Previous</th>
                        <th>Latest</th>
                        <th>Change</th>
                        <th>Signal</th>
                      </tr>
                    </thead>

                    <tbody>

                      {comparisons.map(
                        (
                          comparison,
                          index
                        ) => (
                          <tr
                            key={
                              comparison
                                ?.metric_id ??
                              comparison
                                ?.label ??
                              index
                            }
                          >
                            <td>
                              <strong>
                                {
                                  comparison
                                    ?.label ??
                                  "Financial metric"
                                }
                              </strong>
                            </td>

                            <td>
                              {formatValue(
                                comparison
                                  ?.previous_value,
                                comparison
                                  ?.unit
                              )}
                            </td>

                            <td>
                              {formatValue(
                                comparison
                                  ?.current_value,
                                comparison
                                  ?.unit
                              )}
                            </td>

                            <td>
                              {formatValue(
                                comparison
                                  ?.absolute_change,
                                comparison
                                  ?.unit
                              )}
                            </td>

                            <td>
                              <span
                                className={
                                  signalClass(
                                    comparison
                                      ?.signal
                                  )
                                }
                              >
                                {formatLabel(
                                  comparison
                                    ?.signal ??
                                  "Unavailable"
                                )}
                              </span>
                            </td>
                          </tr>
                        )
                      )}

                    </tbody>

                  </table>

                </div>

              )}

            </section>


            <section className="action-center-grid">

              <article className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Risk Movement
                    </p>

                    <h3>
                      What changed in financial risk?
                    </h3>
                  </div>

                  <span className="action-count">
                    {riskMovements.length} movements
                  </span>
                </div>


                <div className="action-attention-list">

                  <div className="attention-row">
                    <span>
                      New risks
                    </span>

                    <strong>
                      {
                        riskSummary
                          ?.new_count ??
                        0
                      }
                    </strong>
                  </div>

                  <div className="attention-row">
                    <span>
                      Resolved risks
                    </span>

                    <strong>
                      {
                        riskSummary
                          ?.resolved_count ??
                        0
                      }
                    </strong>
                  </div>

                  <div className="attention-row">
                    <span>
                      Severity increased
                    </span>

                    <strong>
                      {
                        riskSummary
                          ?.severity_increased_count ??
                        0
                      }
                    </strong>
                  </div>

                  <div className="attention-row">
                    <span>
                      Severity decreased
                    </span>

                    <strong>
                      {
                        riskSummary
                          ?.severity_decreased_count ??
                        0
                      }
                    </strong>
                  </div>

                </div>

              </article>


              <article className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Snapshot History
                    </p>

                    <h3>
                      Verified processing history
                    </h3>
                  </div>

                  <span className="action-count">
                    {
                      historyData
                        ?.snapshot_count ??
                      0
                    } snapshots
                  </span>
                </div>


                {snapshots.length === 0 ? (

                  <p className="card-note">
                    No verified snapshots are available.
                  </p>

                ) : (

                  <div className="action-list">

                    {snapshots
                      .slice()
                      .reverse()
                      .map(
                        (
                          snapshot,
                          index
                        ) => (
                          <div
                            className="action-list-item"
                            key={
                              snapshot
                                ?.snapshot_id ??
                              index
                            }
                          >
                            <div>
                              <strong>
                                {
                                  snapshot
                                    ?.snapshot_id ??
                                  "Financial snapshot"
                                }
                              </strong>

                              <p className="card-note">
                                {formatDateTime(
                                  snapshot
                                    ?.captured_at
                                )}
                              </p>
                            </div>
                          </div>
                        )
                      )}

                  </div>

                )}

              </article>

            </section>


            <section className="card">

              <div className="card-header">
                <div>
                  <p className="card-label">
                    Risk Details
                  </p>

                  <h3>
                    New, resolved and changing risks
                  </h3>
                </div>
              </div>


              {riskMovements.length === 0 ? (

                <p className="card-note">
                  No financial risk movements were
                  identified between the latest two
                  snapshots.
                </p>

              ) : (

                <div className="action-list">

                  {riskMovements.map(
                    (
                      movement,
                      index
                    ) => (
                      <div
                        className="action-list-item"
                        key={
                          movement
                            ?.risk_family ??
                          index
                        }
                      >
                        <span
                          className={`risk-dot ${priorityClass(
                            movementSeverity(
                              movement
                            )
                          )}`}
                        />

                        <div
                          style={{
                            flex: 1,
                          }}
                        >
                          <div className="card-header">
                            <div>
                              <strong>
                                {movementTitle(
                                  movement
                                )}
                              </strong>

                              <p className="card-note">
                                {formatLabel(
                                  movement
                                    ?.movement ??
                                  "Risk movement"
                                )}
                              </p>
                            </div>

                            <span
                              className={`action-priority ${priorityClass(
                                movementSeverity(
                                  movement
                                )
                              )}`}
                            >
                              {movementSeverity(
                                movement
                              )}
                            </span>
                          </div>
                        </div>
                      </div>
                    )
                  )}

                </div>

              )}

            </section>


            <section className="card">

              <div className="card-header">
                <div>
                  <p className="card-label">
                    Historical Decision Intelligence
                  </p>

                  <h3>
                    Change-driven management priorities
                  </h3>

                  <p className="card-note">
                    These priorities come from verified
                    historical deterioration. Positive
                    developments remain separate and do
                    not cancel management risks.
                  </p>
                </div>

                <span className="action-count">
                  {
                    historicalDecision
                      ?.priority_count ??
                    priorities.length
                  } priorities
                </span>
              </div>


              {priorities.length === 0 ? (

                <p className="card-note">
                  No historical deterioration currently
                  requires a management priority.
                </p>

              ) : (

                <div className="action-list">

                  {priorities.map(
                    (
                      priority,
                      index
                    ) => (
                      <div
                        className="action-list-item"
                        key={
                          (
                            priority?.title ??
                            `historical-priority-${index}`
                          )
                        }
                      >
                        <span
                          className={`risk-dot ${priorityClass(
                            priority
                              ?.priority
                          )}`}
                        />

                        <div
                          style={{
                            flex: 1,
                          }}
                        >
                          <div className="card-header">

                            <div>
                              <strong>
                                {
                                  priority
                                    ?.title ??
                                  "Historical management priority"
                                }
                              </strong>

                              <p className="card-note">
                                {
                                  priority
                                    ?.evidence ??
                                  "Verified historical deterioration."
                                }
                              </p>
                            </div>

                            <span
                              className={`action-priority ${priorityClass(
                                priority
                                  ?.priority
                              )}`}
                            >
                              {
                                priority
                                  ?.priority ??
                                "Medium"
                              }
                            </span>

                          </div>

                          <p className="card-note">
                            Change:{" "}
                            {formatLabel(
                              priority
                                ?.historical_change ??
                              "Historical change"
                            )}
                          </p>

                        </div>

                      </div>
                    )
                  )}

                </div>

              )}

            </section>


            <section className="card">

              <div className="card-header">
                <div>
                  <p className="card-label">
                    Positive Developments
                  </p>

                  <h3>
                    Improvements since the previous snapshot
                  </h3>

                  <p className="card-note">
                    Improvements are shown separately from
                    risks and priorities so positive movement
                    does not hide material deterioration.
                  </p>
                </div>

                <span className="action-count">
                  {
                    historicalDecision
                      ?.improvement_count ??
                    improvements.length
                  } improvements
                </span>
              </div>


              {improvements.length === 0 ? (

                <p className="card-note">
                  No verified positive historical
                  developments were identified.
                </p>

              ) : (

                <div className="action-list">

                  {improvements.map(
                    (
                      improvement,
                      index
                    ) => (
                      <div
                        className="action-list-item"
                        key={
                          (
                            improvement?.title ??
                            `improvement-${index}`
                          )
                        }
                      >

                        <div
                          style={{
                            flex: 1,
                          }}
                        >
                          <strong>
                            {
                              improvement
                                ?.title ??
                              "Financial improvement"
                            }
                          </strong>

                          {improvement?.evidence && (
                            <p className="card-note">
                              {
                                improvement
                                  .evidence
                              }
                            </p>
                          )}

                          <p className="card-note positive">
                            {formatLabel(
                              improvement
                                ?.historical_change ??
                              "Improved"
                            )}
                          </p>
                        </div>

                      </div>
                    )
                  )}

                </div>

              )}

            </section>


            <section className="card">

              <p className="card-label">
                Historical Intelligence Controls
              </p>

              <h3>
                Verified and read-only
              </h3>

              <p className="card-note">
                This page interprets immutable verified
                Financial Intelligence snapshots. Viewing
                historical intelligence does not recalculate
                financials, modify snapshots, include
                hypothetical scenarios, or change the CFO
                Action Plan.
              </p>

            </section>

          </>

        )}

    </AppShell>
  );
}


export default FinancialIntelligenceHistory;