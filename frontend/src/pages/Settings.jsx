import {
  useState,
} from "react";

import api from "../api";
import AppShell from "../components/AppShell";


function availabilityLabel(value) {
  return value
    ? "Available"
    : "Not available";
}


function Settings({
  readiness,
  organizationList,
  currentOrganization,
  setCurrentOrganization,
  refreshOrganizationRegistry,
}) {

  const [
    showAddOrganization,
    setShowAddOrganization,
  ] = useState(false);

  const [
    newOrganization,
    setNewOrganization,
  ] = useState({
    id: "",
    name: "",
    baseCurrency: "USD",
  });

  const [
    onboardingStatus,
    setOnboardingStatus,
  ] = useState("");

  const [
    onboardingError,
    setOnboardingError,
  ] = useState("");

  const [
    isCreatingOrganization,
    setIsCreatingOrganization,
  ] = useState(false);


  function handleNewOrganizationChange(
    event
  ) {
    const {
      name,
      value,
    } = event.target;

    setNewOrganization(
      (current) => ({
        ...current,
        [name]: value,
      })
    );
  }


  function handleCancelOrganization() {
    setShowAddOrganization(false);

    setNewOrganization({
      id: "",
      name: "",
      baseCurrency: "USD",
    });

    setOnboardingError("");
    setOnboardingStatus("");
  }


  async function handleCreateOrganization(
    event
  ) {
    event.preventDefault();

    const organizationId =
      newOrganization.id
        .trim()
        .toLowerCase()
        .replace(
          /[^a-z0-9_-]+/g,
          "-"
        )
        .replace(
          /-+/g,
          "-"
        )
        .replace(
          /^[-_]+|[-_]+$/g,
          ""
        );

    const organizationName =
      newOrganization.name.trim();

    const baseCurrency =
      newOrganization.baseCurrency
        .trim()
        .toUpperCase();

    setOnboardingError("");
    setOnboardingStatus("");

    if (!organizationId) {
      setOnboardingError(
        "Organization ID is required."
      );
      return;
    }

    if (!organizationName) {
      setOnboardingError(
        "Organization name is required."
      );
      return;
    }

    if (
      !/^[A-Z]{3}$/.test(
        baseCurrency
      )
    ) {
      setOnboardingError(
        "Base currency must be a 3-letter currency code."
      );
      return;
    }

    setIsCreatingOrganization(true);

    try {
      const response =
        await api.post(
          "/organisations/onboard",
          {
            id: organizationId,
            name: organizationName,
            base_currency:
              baseCurrency,
          }
        );

      const createdOrganization =
        response.data?.organization;

      if (!createdOrganization?.id) {
        throw new Error(
          "The backend did not return the created organization."
        );
      }

      await refreshOrganizationRegistry(
        createdOrganization.id
      );

      setOnboardingStatus(
        `${createdOrganization.name} was created successfully.`
      );

      setNewOrganization({
        id: "",
        name: "",
        baseCurrency: "USD",
      });

      setShowAddOrganization(false);
    } catch (creationError) {
      console.error(
        "Organization onboarding error:",
        creationError
      );

      const detail =
        creationError
          ?.response
          ?.data
          ?.detail;

      setOnboardingError(
        typeof detail === "string"
          ? detail
          : "Could not create the organization."
      );
    } finally {
      setIsCreatingOrganization(
        false
      );
    }
  }


  const organization =
    organizationList.find(
      (organizationOption) =>
        organizationOption.id ===
        currentOrganization?.id
    ) ??
    currentOrganization ?? {
      id: "--",
      name: "Organization",
      baseCurrency: "--",
    };


  const isRegistered =
    readiness?.registered === true;

  const readinessStatus =
    readiness?.status ??
    "not_available";


  return (
    <AppShell
      eyebrow="Organization configuration"
      title="Settings"
      organizationList={organizationList}
      currentOrganization={currentOrganization}
      setCurrentOrganization={setCurrentOrganization}
      mainClassName="settings-main"
    >
        <section className="settings-intro">

          <div>

            <p className="section-eyebrow">
              AI-FOS configuration
            </p>

            <h2>
              Organization Settings
            </h2>

            <p>
              Review the organization context,
              financial configuration and data
              readiness used by AI-FOS.
              Configuration remains controlled so
              financial intelligence stays
              traceable and reliable.
            </p>

          </div>


          <button
            type="button"
            className="primary-button"
            onClick={() => {
              setShowAddOrganization(
                (current) => !current
              );

              setOnboardingError("");
            }}
          >
            {showAddOrganization
              ? "Close"
              : "Add Organization"}
          </button>

        </section>


        {onboardingStatus && (

          <section className="settings-warning-note">

            <strong>
              Organization Created
            </strong>

            <p>
              {onboardingStatus}
              {" "}
              The organization workspace is
              ready for financial-data
              onboarding.
            </p>

          </section>

        )}


        {showAddOrganization && (

          <section className="settings-card settings-full-card">

            <div className="settings-card-header">

              <div>

                <p className="section-eyebrow">
                  Organization onboarding
                </p>

                <h2>
                  Add Organization
                </h2>

                <p>
                  Register a new organization
                  and create its persistent
                  AI-FOS workspace.
                </p>

              </div>


              <span className="settings-badge system">
                Controlled
              </span>

            </div>


            <form
              onSubmit={
                handleCreateOrganization
              }
            >

              <div className="settings-data-grid">

                <div>

                  <label
                    htmlFor="organization-name"
                  >
                    Organization Name
                  </label>

                  <input
                    id="organization-name"
                    name="name"
                    type="text"
                    value={
                      newOrganization.name
                    }
                    onChange={
                      handleNewOrganizationChange
                    }
                    placeholder="Example NGO"
                    disabled={
                      isCreatingOrganization
                    }
                  />

                  <p>
                    Official organization name
                    displayed throughout AI-FOS.
                  </p>

                </div>


                <div>

                  <label
                    htmlFor="organization-id"
                  >
                    Organization ID
                  </label>

                  <input
                    id="organization-id"
                    name="id"
                    type="text"
                    value={
                      newOrganization.id
                    }
                    onChange={
                      handleNewOrganizationChange
                    }
                    placeholder="example-ngo"
                    disabled={
                      isCreatingOrganization
                    }
                  />

                  <p>
                    Stable organization code used
                    by workspaces and financial
                    intelligence.
                  </p>

                </div>


                <div>

                  <label
                    htmlFor="base-currency"
                  >
                    Base Currency
                  </label>

                  <input
                    id="base-currency"
                    name="baseCurrency"
                    type="text"
                    maxLength="3"
                    value={
                      newOrganization
                        .baseCurrency
                    }
                    onChange={
                      handleNewOrganizationChange
                    }
                    placeholder="USD"
                    disabled={
                      isCreatingOrganization
                    }
                  />

                  <p>
                    Three-letter reporting
                    currency code, for example
                    USD or EUR.
                  </p>

                </div>

              </div>


              {onboardingError && (

                <div className="settings-warning-note">

                  <strong>
                    Organization not created
                  </strong>

                  <p>
                    {onboardingError}
                  </p>

                </div>

              )}


              <div className="settings-header-actions">

                <button
                  type="button"
                  className="nav-item"
                  onClick={
                    handleCancelOrganization
                  }
                  disabled={
                    isCreatingOrganization
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    isCreatingOrganization
                  }
                >
                  {isCreatingOrganization
                    ? "Creating..."
                    : "Create Organization"}
                </button>

              </div>

            </form>

          </section>

        )}


        <section className="settings-card settings-full-card">

          <div className="settings-card-header">

            <div>

              <p className="section-eyebrow">
                Organization readiness
              </p>

              <h2>
                Data & Intelligence Readiness
              </h2>

            </div>


            <span
              className={
                isRegistered
                  ? "settings-badge"
                  : "settings-badge system"
              }
            >
              {isRegistered
                ? "Registered"
                : "Not registered"}
            </span>

          </div>


          <div className="settings-data-grid">

            <div>

              <span>
                Current Status
              </span>

              <strong>
                {readinessStatus
                  .replaceAll("_", " ")}
              </strong>

              <p>
                Backend-controlled organization
                readiness state.
              </p>

            </div>


            <div>

              <span>
                Uploaded Data
              </span>

              <strong>
                {availabilityLabel(
                  readiness?.has_uploaded_data
                )}
              </strong>

              <p>
                Indicates whether organization
                data has been uploaded into its
                workspace.
              </p>

            </div>


            <div>

              <span>
                Financial Model
              </span>

              <strong>
                {availabilityLabel(
                  readiness?.has_financial_model
                )}
              </strong>

              <p>
                Indicates whether validated
                financial-model outputs have
                been generated.
              </p>

            </div>


            <div>

              <span>
                Financial Intelligence
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_financial_intelligence
                )}
              </strong>

              <p>
                Indicates whether the AI-FOS
                intelligence hub is available
                for this organization.
              </p>

            </div>

          </div>

        </section>


        <section className="settings-grid">

          <article className="settings-card">

            <div className="settings-card-header">

              <div>

                <p className="section-eyebrow">
                  Organization
                </p>

                <h2>
                  Organization Profile
                </h2>

              </div>


              <span
                className={
                  isRegistered
                    ? "settings-badge"
                    : "settings-badge system"
                }
              >
                {isRegistered
                  ? "Registered"
                  : "Registry only"}
              </span>

            </div>


            <div className="settings-detail-list">

              <div>

                <span>
                  Organization Name
                </span>

                <strong>
                  {organization.name}
                </strong>

              </div>


              <div>

                <span>
                  Organization ID
                </span>

                <strong>
                  {organization.id}
                </strong>

              </div>


              <div>

                <span>
                  Base Currency
                </span>

                <strong>
                  {
                    organization.baseCurrency
                  }
                </strong>

              </div>

            </div>

          </article>


          <article className="settings-card">

            <div className="settings-card-header">

              <div>

                <p className="section-eyebrow">
                  Financial model
                </p>

                <h2>
                  Financial Configuration
                </h2>

              </div>


              <span className="settings-badge system">
                System
              </span>

            </div>


            <div className="settings-detail-list">

              <div>

                <span>
                  Reporting Currency
                </span>

                <strong>
                  {
                    organization.baseCurrency
                  }
                </strong>

              </div>


              <div>

                <span>
                  Financial Intelligence
                </span>

                <strong>
                  {readiness
                    ?.has_financial_intelligence
                    ? "Ready"
                    : "Not available"}
                </strong>

              </div>


              <div>

                <span>
                  Evidence Validation
                </span>

                <strong>
                  {readiness
                    ?.has_gl_validation
                    ? "Available"
                    : "Not available"}
                </strong>

              </div>

            </div>

          </article>


          <article className="settings-card">

            <div className="settings-card-header">

              <div>

                <p className="section-eyebrow">
                  Funding intelligence
                </p>

                <h2>
                  Grant Configuration
                </h2>

              </div>


              <span className="settings-badge system">
                Controlled
              </span>

            </div>


            <div className="settings-detail-list">

              <div>

                <span>
                  Grant Period Rule
                </span>

                <strong>
                  Fiscal Year Overlap
                </strong>

              </div>


              <div>

                <span>
                  Period Eligibility
                </span>

                <strong>
                  Enabled
                </strong>

              </div>


              <div>

                <span>
                  Unknown Grant Period
                </span>

                <strong>
                  Not Auto-Applied
                </strong>

              </div>

            </div>

          </article>


          <article className="settings-card">

            <div className="settings-card-header">

              <div>

                <p className="section-eyebrow">
                  Intelligence controls
                </p>

                <h2>
                  AI CFO Governance
                </h2>

              </div>


              <span className="settings-badge system">
                Protected
              </span>

            </div>


            <div className="settings-detail-list">

              <div>

                <span>
                  Validated Outputs
                </span>

                <strong>
                  Required
                </strong>

              </div>


              <div>

                <span>
                  Frontend Recalculation
                </span>

                <strong>
                  Disabled
                </strong>

              </div>


              <div>

                <span>
                  Human Oversight
                </span>

                <strong>
                  Required
                </strong>

              </div>

            </div>

          </article>

        </section>


        <section className="settings-card settings-full-card">

          <div className="settings-card-header">

            <div>

              <p className="section-eyebrow">
                Data & intelligence
              </p>

              <h2>
                AI-FOS Data Configuration
              </h2>

            </div>

          </div>


          <div className="settings-data-grid">

            <div>

              <span>
                Chart of Accounts
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_chart_of_accounts
                )}
              </strong>

              <p>
                Account structure and
                classifications are learned
                from validated organization
                data.
              </p>

            </div>


            <div>

              <span>
                General Ledger
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_general_ledger
                )}
              </strong>

              <p>
                Financial intelligence uses
                normalized and validated
                transaction data.
              </p>

            </div>


            <div>

              <span>
                Budget
              </span>

              <strong>
                {availabilityLabel(
                  readiness?.has_budget
                )}
              </strong>

              <p>
                Budget analysis uses mapped
                organization dimensions and
                validated Budget vs Actual
                logic.
              </p>

            </div>


            <div>

              <span>
                Financial Health
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_financial_health
                )}
              </strong>

              <p>
                Financial Health is generated
                from validated AI-FOS
                financial intelligence.
              </p>

            </div>


            <div>

              <span>
                Executive Dashboard
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_executive_dashboard
                )}
              </strong>

              <p>
                Indicates whether validated
                dashboard intelligence has
                been generated.
              </p>

            </div>


            <div>

              <span>
                CFO Report Data
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_cfo_report_data
                )}
              </strong>

              <p>
                Structured CFO report data
                generated from validated
                financial intelligence.
              </p>

            </div>


            <div>

              <span>
                CFO Report PDF
              </span>

              <strong>
                {availabilityLabel(
                  readiness
                    ?.has_cfo_report_pdf
                )}
              </strong>

              <p>
                Indicates whether the
                downloadable CFO PDF report
                is ready.
              </p>

            </div>


            <div>

              <span>
                Organization Knowledge
              </span>

              <strong>
                {isRegistered
                  ? "Organization-specific"
                  : "Not available"}
              </strong>

              <p>
                AI-FOS preserves validated
                organization context for
                financial interpretation.
              </p>

            </div>

          </div>

        </section>


        <section className="settings-warning-note">

          <strong>
            Controlled Configuration
          </strong>

          <p>
            Organization creation is now
            handled through a validated backend
            onboarding workflow. Other financial
            configuration remains read-only so
            changes cannot silently alter
            financial results.
          </p>

        </section>

    </AppShell>
  );
}


export default Settings;