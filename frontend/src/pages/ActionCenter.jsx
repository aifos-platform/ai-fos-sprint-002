import {
  useCallback,
  useEffect,
  useState,
} from "react";

import api from "../api";
import AppShell from "../components/AppShell";


function ActionCenter({
  organizationList,
  currentOrganization,
  setCurrentOrganization,
}) {
  const [
    actionCenter,
    setActionCenter,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const [
    successMessage,
    setSuccessMessage,
  ] = useState("");

  const [
    mutationError,
    setMutationError,
  ] = useState("");

  const [
    mutationBusy,
    setMutationBusy,
  ] = useState("");

  const [
    actionDrafts,
    setActionDrafts,
  ] = useState({});


  const buildActionDrafts = (
    actions = []
  ) => {
    const drafts = {};

    actions.forEach((action) => {
      drafts[action.action_id] = {
        owner:
          action.owner ??
          "",
        dueDate:
          action.due_date ??
          "",
        progress:
          Number(
            action.progress_percentage ??
            0
          ),
        notes:
          action.management_notes ??
          "",
      };
    });

    return drafts;
  };


  const loadActionCenter = useCallback(
    async ({
      showLoading = true,
    } = {}) => {
      if (!currentOrganization?.id) {
        setActionCenter(null);

        if (showLoading) {
          setLoading(false);
        }

        return;
      }

      try {
        if (showLoading) {
          setLoading(true);
        }

        setError("");

        const response = await api.get(
          `/organisations/${currentOrganization.id}/cfo-action-center`
        );

        const data =
          response.data ??
          null;

        setActionCenter(data);

        setActionDrafts(
          buildActionDrafts(
            data?.actions ??
            []
          )
        );
      } catch (requestError) {
        console.error(
          "CFO Action Center load error:",
          requestError
        );

        setActionCenter(null);

        setError(
          "Could not load the Executive Action Center."
        );
      } finally {
        if (showLoading) {
          setLoading(false);
        }
      }
    },
    [currentOrganization?.id]
  );


  useEffect(() => {
    setSuccessMessage("");
    setMutationError("");
    setMutationBusy("");
    setActionDrafts({});

    loadActionCenter();
  }, [
    currentOrganization?.id,
    loadActionCenter,
  ]);


  const summary =
    actionCenter?.summary ??
    {};

  const actions =
    actionCenter?.actions ??
    [];

  const monitoring =
    actionCenter?.monitoring ??
    {};

  const escalation =
    actionCenter?.escalation ??
    {};

  const performance =
    actionCenter?.performance ??
    {};

  const executivePriorities =
    actionCenter?.executive_priorities ??
    [];


  const overdueActions =
    monitoring?.overdue_actions ??
    [];

  const dueSoonActions =
    monitoring?.due_soon_actions ??
    [];

  const blockedActions =
    monitoring?.blocked_actions ??
    [];

  const escalations =
    escalation?.escalations ??
    [];


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


  const formatStatus = (status) =>
    String(status ?? "open")
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );


  const extractApiError = (
    requestError,
    fallback
  ) => {
    const detail =
      requestError?.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (
      detail &&
      typeof detail === "object"
    ) {
      try {
        return JSON.stringify(detail);
      } catch {
        return fallback;
      }
    }

    return fallback;
  };


  const setActionDraftField = (
    actionId,
    field,
    value
  ) => {
    setActionDrafts(
      (currentDrafts) => ({
        ...currentDrafts,
        [actionId]: {
          ...(
            currentDrafts[actionId] ??
            {}
          ),
          [field]: value,
        },
      })
    );
  };


  const runActionCommand = async (
    actionId,
    command,
    {
      value,
      managementNotes,
      successText,
    } = {}
  ) => {
    if (
      !currentOrganization?.id ||
      !actionId
    ) {
      return;
    }

    const busyKey =
      `${actionId}:${command}`;

    try {
      setMutationBusy(busyKey);
      setMutationError("");
      setSuccessMessage("");

      const payload = {
        command,
      };

      if (value !== undefined) {
        payload.value = value;
      }

      if (
        managementNotes !== undefined
      ) {
        payload.management_notes =
          managementNotes;
      }

      await api.post(
        (
          `/organisations/${currentOrganization.id}` +
          `/cfo-actions/${actionId}/command`
        ),
        payload
      );

      await loadActionCenter({
        showLoading: false,
      });

      setSuccessMessage(
        successText ??
        "Action updated successfully."
      );
    } catch (requestError) {
      console.error(
        "CFO Action command error:",
        requestError
      );

      setMutationError(
        extractApiError(
          requestError,
          "Could not update the management action."
        )
      );
    } finally {
      setMutationBusy("");
    }
  };


  const createActionFromPriority = async (
    priorityIndex
  ) => {
    if (!currentOrganization?.id) {
      return;
    }

    const busyKey =
      `priority:${priorityIndex}`;

    try {
      setMutationBusy(busyKey);
      setMutationError("");
      setSuccessMessage("");

      await api.post(
        (
          `/organisations/${currentOrganization.id}` +
          "/cfo-actions/from-executive-priority"
        ),
        {
          priority_index: priorityIndex,
        }
      );

      await loadActionCenter({
        showLoading: false,
      });

      setSuccessMessage(
        "Executive priority added to the CFO Action Plan."
      );
    } catch (requestError) {
      console.error(
        "CFO Action creation error:",
        requestError
      );

      setMutationError(
        extractApiError(
          requestError,
          "Could not create the management action."
        )
      );
    } finally {
      setMutationBusy("");
    }
  };


  const priorityAlreadyCreated = (
    executivePriority
  ) => {
    const title =
      String(
        executivePriority?.title ??
        ""
      )
        .trim()
        .toLowerCase();

    if (!title) {
      return false;
    }

    return actions.some((action) => {
      const sourceType =
        String(
          action?.source_type ??
          ""
        )
          .trim()
          .toLowerCase();

      const sourceTitle =
        String(
          action?.source_title ??
          action?.title ??
          ""
        )
          .trim()
          .toLowerCase();

      return (
        sourceType ===
          "executive_decision_intelligence" &&
        sourceTitle === title
      );
    });
  };


  const getDraft = (action) =>
    actionDrafts[action.action_id] ?? {
      owner:
        action.owner ??
        "",
      dueDate:
        action.due_date ??
        "",
      progress:
        Number(
          action.progress_percentage ??
          0
        ),
      notes:
        action.management_notes ??
        "",
    };


  return (
    <AppShell
      eyebrow="Management execution"
      title="Executive Action Center"
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


        {mutationError && (
          <section className="card">
            <p className="card-note negative">
              {mutationError}
            </p>
          </section>
        )}


        {successMessage && (
          <section className="card">
            <p className="card-note positive">
              {successMessage}
            </p>
          </section>
        )}


        {loading ? (

          <section className="card">
            <p className="card-note">
              Loading management actions...
            </p>
          </section>

        ) : (

          <>

            <section className="action-summary-grid">

              <article className="card">
                <p className="card-label">
                  Total actions
                </p>

                <h3>
                  {summary.total_actions ?? 0}
                </h3>

                <p className="card-note">
                  Management actions tracked
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  In progress
                </p>

                <h3>
                  {
                    summary
                      .in_progress_actions ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Currently being executed
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Overdue
                </p>

                <h3 className="negative">
                  {
                    summary
                      .overdue_actions ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Require follow-up
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Blocked
                </p>

                <h3>
                  {
                    summary
                      .blocked_actions ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Execution obstacles
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Due soon
                </p>

                <h3>
                  {
                    summary
                      .due_soon_actions ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Upcoming deadlines
                </p>
              </article>


              <article className="card">
                <p className="card-label">
                  Escalations
                </p>

                <h3>
                  {
                    summary
                      .total_escalations ??
                    0
                  }
                </h3>

                <p className="card-note">
                  Management attention
                </p>
              </article>

            </section>


            <section className="card">

              <div className="card-header">
                <div>
                  <p className="card-label">
                    Executive Decision Intelligence
                  </p>

                  <h3>
                    Priorities ready for management action
                  </h3>

                  <p className="card-note">
                    Create an Action Plan item directly
                    from a verified executive priority.
                    Owner and due date remain explicit
                    management decisions.
                  </p>
                </div>

                <span className="action-count">
                  {executivePriorities.length} priorities
                </span>
              </div>


              {executivePriorities.length === 0 ? (

                <p className="card-note">
                  No executive priorities are currently
                  available.
                </p>

              ) : (

                <div className="action-list">

                  {executivePriorities.map(
                    (
                      executivePriority,
                      priorityIndex
                    ) => {
                      const alreadyCreated =
                        priorityAlreadyCreated(
                          executivePriority
                        );

                      const busy =
                        mutationBusy ===
                        `priority:${priorityIndex}`;

                      return (
                        <div
                          className="action-list-item"
                          key={
                            (
                              executivePriority.title ??
                              `priority-${priorityIndex}`
                            )
                          }
                        >
                          <span
                            className={`risk-dot ${priorityClass(
                              executivePriority.priority
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
                                    executivePriority.title ??
                                    "Executive priority"
                                  }
                                </strong>

                                <p className="card-note">
                                  {
                                    executivePriority
                                      .management_action ??
                                    "Management action required."
                                  }
                                </p>
                              </div>

                              <span
                                className={`action-priority ${priorityClass(
                                  executivePriority.priority
                                )}`}
                              >
                                {
                                  executivePriority.priority ??
                                  "Medium"
                                }
                              </span>
                            </div>

                            <div
                              style={{
                                marginTop: "12px",
                              }}
                            >
                              <button
                                className="secondary-button"
                                type="button"
                                disabled={
                                  busy ||
                                  alreadyCreated
                                }
                                onClick={() =>
                                  createActionFromPriority(
                                    priorityIndex
                                  )
                                }
                              >
                                {
                                  alreadyCreated
                                    ? "Already in Action Plan"
                                    : busy
                                      ? "Creating..."
                                      : "Create Action"
                                }
                              </button>
                            </div>

                          </div>
                        </div>
                      );
                    }
                  )}

                </div>

              )}

            </section>


            <section className="action-center-grid">

              <article className="card action-main-card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      CFO Action Plan
                    </p>

                    <h3>
                      Active management actions
                    </h3>
                  </div>

                  <span className="action-count">
                    {actions.length} actions
                  </span>
                </div>


                {actions.length === 0 ? (

                  <p className="card-note">
                    No CFO management actions
                    have been created yet.
                  </p>

                ) : (

                  <div className="action-table-wrap">

                    <table className="action-table">
                      <thead>
                        <tr>
                          <th>Priority</th>
                          <th>Action</th>
                          <th>Owner</th>
                          <th>Due date</th>
                          <th>Status</th>
                          <th>Progress</th>
                        </tr>
                      </thead>

                      <tbody>
                        {actions.map((action) => {
                          const draft =
                            getDraft(action);

                          return (
                            <tr
                              key={
                                action.action_id
                              }
                            >
                              <td>
                                <span
                                  className={`action-priority ${priorityClass(
                                    action.priority
                                  )}`}
                                >
                                  {
                                    action.priority ??
                                    "Medium"
                                  }
                                </span>
                              </td>

                              <td>
                                <strong>
                                  {
                                    action.title ??
                                    "Untitled action"
                                  }
                                </strong>

                                {action.description && (
                                  <p className="action-description">
                                    {
                                      action.description
                                    }
                                  </p>
                                )}
                              </td>

                              <td>
                                {
                                  action.owner ??
                                  "Unassigned"
                                }
                              </td>

                              <td>
                                {
                                  action.due_date ??
                                  "No due date"
                                }
                              </td>

                              <td>
                                <span className="action-status">
                                  {formatStatus(
                                    action.status
                                  )}
                                </span>
                              </td>

                              <td>
                                <div className="action-progress-cell">
                                  <div className="action-progress-track">
                                    <div
                                      className="action-progress-bar"
                                      style={{
                                        width: `${Math.min(
                                          Math.max(
                                            Number(
                                              action.progress_percentage ??
                                              0
                                            ),
                                            0
                                          ),
                                          100
                                        )}%`,
                                      }}
                                    />
                                  </div>

                                  <span>
                                    {
                                      action
                                        .progress_percentage ??
                                      0
                                    }%
                                  </span>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>

                  </div>
                )}

              </article>


              <article className="card">

                <p className="card-label">
                  Management attention
                </p>

                <h3>
                  Immediate follow-up
                </h3>


                <div className="action-attention-list">

                  <div className="attention-row">
                    <span>
                      Overdue
                    </span>

                    <strong>
                      {overdueActions.length}
                    </strong>
                  </div>


                  <div className="attention-row">
                    <span>
                      Due soon
                    </span>

                    <strong>
                      {dueSoonActions.length}
                    </strong>
                  </div>


                  <div className="attention-row">
                    <span>
                      Blocked
                    </span>

                    <strong>
                      {blockedActions.length}
                    </strong>
                  </div>


                  <div className="attention-row">
                    <span>
                      Escalated
                    </span>

                    <strong>
                      {escalations.length}
                    </strong>
                  </div>

                </div>

              </article>

            </section>


            {actions.length > 0 && (

              <section className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Action Management
                    </p>

                    <h3>
                      Manage execution
                    </h3>

                    <p className="card-note">
                      All changes are validated by the
                      protected CFO Action lifecycle and
                      recorded in Action History.
                    </p>
                  </div>
                </div>


                <div className="action-list">

                  {actions.map((action) => {
                    const draft =
                      getDraft(action);

                    const status =
                      String(
                        action.status ??
                        "open"
                      )
                        .trim()
                        .toLowerCase();

                    const isCompleted =
                      status === "completed";

                    const isCancelled =
                      status === "cancelled";

                    const isBlocked =
                      status === "blocked";

                    const canStart =
                      (
                        status === "open" ||
                        status === "in_progress"
                      );

                    return (
                      <div
                        className="action-list-item"
                        key={
                          `manage-${action.action_id}`
                        }
                      >
                        <span
                          className={`risk-dot ${priorityClass(
                            action.priority
                          )}`}
                        />

                        <div
                          style={{
                            flex: 1,
                            minWidth: 0,
                          }}
                        >

                          <div className="card-header">
                            <div>
                              <strong>
                                {
                                  action.title ??
                                  "Management action"
                                }
                              </strong>

                              <p className="card-note">
                                Status:{" "}
                                {formatStatus(
                                  action.status
                                )}
                                {" · "}
                                Progress:{" "}
                                {
                                  action.progress_percentage ??
                                  0
                                }%
                              </p>
                            </div>

                            <span
                              className={`action-priority ${priorityClass(
                                action.priority
                              )}`}
                            >
                              {
                                action.priority ??
                                "Medium"
                              }
                            </span>
                          </div>


                          <div
                            style={{
                              display: "grid",
                              gridTemplateColumns:
                                "repeat(auto-fit, minmax(180px, 1fr))",
                              gap: "12px",
                              marginTop: "16px",
                            }}
                          >

                            <div>
                              <p className="card-label">
                                Owner
                              </p>

                              <input
                                type="text"
                                value={
                                  draft.owner ??
                                  ""
                                }
                                placeholder="Enter owner"
                                disabled={
                                  isCompleted ||
                                  isCancelled
                                }
                                onChange={(event) =>
                                  setActionDraftField(
                                    action.action_id,
                                    "owner",
                                    event.target.value
                                  )
                                }
                              />

                              <div
                                style={{
                                  display: "flex",
                                  gap: "8px",
                                  marginTop: "8px",
                                  flexWrap: "wrap",
                                }}
                              >
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    isCompleted ||
                                    isCancelled ||
                                    mutationBusy ===
                                      `${action.action_id}:assign`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "assign",
                                      {
                                        value:
                                          draft.owner,
                                        successText:
                                          "Action owner updated.",
                                      }
                                    )
                                  }
                                >
                                  Assign
                                </button>

                                {action.owner && (
                                  <button
                                    className="secondary-button"
                                    type="button"
                                    disabled={
                                      isCompleted ||
                                      isCancelled ||
                                      mutationBusy ===
                                        `${action.action_id}:unassign`
                                    }
                                    onClick={() =>
                                      runActionCommand(
                                        action.action_id,
                                        "unassign",
                                        {
                                          successText:
                                            "Action owner removed.",
                                        }
                                      )
                                    }
                                  >
                                    Unassign
                                  </button>
                                )}
                              </div>
                            </div>


                            <div>
                              <p className="card-label">
                                Due date
                              </p>

                              <input
                                type="date"
                                value={
                                  draft.dueDate ??
                                  ""
                                }
                                disabled={
                                  isCompleted ||
                                  isCancelled
                                }
                                onChange={(event) =>
                                  setActionDraftField(
                                    action.action_id,
                                    "dueDate",
                                    event.target.value
                                  )
                                }
                              />

                              <div
                                style={{
                                  display: "flex",
                                  gap: "8px",
                                  marginTop: "8px",
                                  flexWrap: "wrap",
                                }}
                              >
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    isCompleted ||
                                    isCancelled ||
                                    mutationBusy ===
                                      `${action.action_id}:set_due_date`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "set_due_date",
                                      {
                                        value:
                                          draft.dueDate,
                                        successText:
                                          "Action due date updated.",
                                      }
                                    )
                                  }
                                >
                                  Set date
                                </button>

                                {action.due_date && (
                                  <button
                                    className="secondary-button"
                                    type="button"
                                    disabled={
                                      isCompleted ||
                                      isCancelled ||
                                      mutationBusy ===
                                        `${action.action_id}:clear_due_date`
                                    }
                                    onClick={() =>
                                      runActionCommand(
                                        action.action_id,
                                        "clear_due_date",
                                        {
                                          successText:
                                            "Action due date cleared.",
                                        }
                                      )
                                    }
                                  >
                                    Clear
                                  </button>
                                )}
                              </div>
                            </div>


                            <div>
                              <p className="card-label">
                                Progress %
                              </p>

                              <input
                                type="number"
                                min="0"
                                max="100"
                                step="1"
                                value={
                                  draft.progress ??
                                  0
                                }
                                disabled={
                                  isCompleted ||
                                  isCancelled
                                }
                                onChange={(event) =>
                                  setActionDraftField(
                                    action.action_id,
                                    "progress",
                                    event.target.value
                                  )
                                }
                              />

                              <div
                                style={{
                                  marginTop: "8px",
                                }}
                              >
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    isCompleted ||
                                    isCancelled ||
                                    mutationBusy ===
                                      `${action.action_id}:update_progress`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "update_progress",
                                      {
                                        value:
                                          Number(
                                            draft.progress
                                          ),
                                        successText:
                                          "Action progress updated.",
                                      }
                                    )
                                  }
                                >
                                  Update progress
                                </button>
                              </div>
                            </div>


                            <div>
                              <p className="card-label">
                                Management notes
                              </p>

                              <input
                                type="text"
                                value={
                                  draft.notes ??
                                  ""
                                }
                                placeholder="Optional note"
                                onChange={(event) =>
                                  setActionDraftField(
                                    action.action_id,
                                    "notes",
                                    event.target.value
                                  )
                                }
                              />

                              <div
                                style={{
                                  marginTop: "8px",
                                }}
                              >
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    mutationBusy ===
                                    `${action.action_id}:update_notes`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "update_notes",
                                      {
                                        value:
                                          draft.notes,
                                        successText:
                                          "Management notes updated.",
                                      }
                                    )
                                  }
                                >
                                  Save notes
                                </button>
                              </div>
                            </div>

                          </div>


                          <div
                            style={{
                              display: "flex",
                              flexWrap: "wrap",
                              gap: "8px",
                              marginTop: "18px",
                            }}
                          >

                            {canStart && (
                              <button
                                className="secondary-button"
                                type="button"
                                disabled={
                                  mutationBusy ===
                                  `${action.action_id}:start`
                                }
                                onClick={() =>
                                  runActionCommand(
                                    action.action_id,
                                    "start",
                                    {
                                      successText:
                                        "Action moved to in progress.",
                                    }
                                  )
                                }
                              >
                                Start
                              </button>
                            )}


                            {!isBlocked &&
                              !isCompleted &&
                              !isCancelled && (
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    mutationBusy ===
                                    `${action.action_id}:block`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "block",
                                      {
                                        managementNotes:
                                          draft.notes ||
                                          undefined,
                                        successText:
                                          "Action marked as blocked.",
                                      }
                                    )
                                  }
                                >
                                  Block
                                </button>
                              )}


                            {isBlocked && (
                              <button
                                className="secondary-button"
                                type="button"
                                disabled={
                                  mutationBusy ===
                                  `${action.action_id}:unblock`
                                }
                                onClick={() =>
                                  runActionCommand(
                                    action.action_id,
                                    "unblock",
                                    {
                                      successText:
                                        "Action unblocked.",
                                    }
                                  )
                                }
                              >
                                Unblock
                              </button>
                            )}


                            {!isCompleted &&
                              !isCancelled && (
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    mutationBusy ===
                                    `${action.action_id}:complete`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "complete",
                                      {
                                        managementNotes:
                                          draft.notes ||
                                          undefined,
                                        successText:
                                          "Action completed.",
                                      }
                                    )
                                  }
                                >
                                  Complete
                                </button>
                              )}


                            {(isCompleted ||
                              isCancelled) && (
                              <button
                                className="secondary-button"
                                type="button"
                                disabled={
                                  mutationBusy ===
                                  `${action.action_id}:reopen`
                                }
                                onClick={() =>
                                  runActionCommand(
                                    action.action_id,
                                    "reopen",
                                    {
                                      successText:
                                        "Action reopened.",
                                    }
                                  )
                                }
                              >
                                Reopen
                              </button>
                            )}


                            {!isCompleted &&
                              !isCancelled && (
                                <button
                                  className="secondary-button"
                                  type="button"
                                  disabled={
                                    mutationBusy ===
                                    `${action.action_id}:cancel`
                                  }
                                  onClick={() =>
                                    runActionCommand(
                                      action.action_id,
                                      "cancel",
                                      {
                                        managementNotes:
                                          draft.notes ||
                                          undefined,
                                        successText:
                                          "Action cancelled.",
                                      }
                                    )
                                  }
                                >
                                  Cancel
                                </button>
                              )}

                          </div>

                        </div>
                      </div>
                    );
                  })}

                </div>

              </section>

            )}


            <section className="action-center-grid">

              <article className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Escalation Intelligence
                    </p>

                    <h3>
                      Management intervention
                    </h3>
                  </div>
                </div>


                {escalations.length === 0 ? (

                  <p className="card-note">
                    No actions currently require
                    escalation.
                  </p>

                ) : (

                  <div className="action-list">
                    {escalations
                      .slice(0, 5)
                      .map(
                        (
                          escalationItem,
                          index
                        ) => (
                          <div
                            className="action-list-item"
                            key={
                              escalationItem
                                .action_id ??
                              index
                            }
                          >
                            <span
                              className={`risk-dot ${priorityClass(
                                escalationItem
                                  .priority
                              )}`}
                            />

                            <div>
                              <strong>
                                {
                                  escalationItem
                                    .title ??
                                  "Management action"
                                }
                              </strong>

                              <p className="card-note">
                                {
                                  escalationItem
                                    .reason ??
                                  escalationItem
                                    .management_attention ??
                                  "Management attention required."
                                }
                              </p>
                            </div>
                          </div>
                        )
                      )}
                  </div>

                )}

              </article>


              <article className="card">

                <div className="card-header">
                  <div>
                    <p className="card-label">
                      Execution Performance
                    </p>

                    <h3>
                      Action history
                    </h3>
                  </div>
                </div>


                <div className="action-attention-list">

                  <div className="attention-row">
                    <span>
                      History events
                    </span>

                    <strong>
                      {
                        summary
                          .history_events ??
                        performance
                          ?.summary
                          ?.total_events ??
                        0
                      }
                    </strong>
                  </div>


                  <div className="attention-row">
                    <span>
                      Completed
                    </span>

                    <strong>
                      {
                        summary
                          .completed_actions ??
                        0
                      }
                    </strong>
                  </div>


                  <div className="attention-row">
                    <span>
                      Reopened
                    </span>

                    <strong>
                      {
                        summary
                          .reopened_actions ??
                        0
                      }
                    </strong>
                  </div>


                  <div className="attention-row">
                    <span>
                      Repeated blocks
                    </span>

                    <strong>
                      {
                        summary
                          .actions_with_repeated_blocks ??
                        0
                      }
                    </strong>
                  </div>

                </div>

              </article>

            </section>

          </>

        )}

    </AppShell>
  );
}


export default ActionCenter;