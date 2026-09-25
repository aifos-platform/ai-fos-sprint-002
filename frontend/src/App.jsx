import {
  useEffect,
  useState,
} from "react";

import {
  Route,
  Routes,
} from "react-router-dom";

import api from "./api";
import "./App.css";

import {
  defaultOrganization,
  setOrganizationsFromRegistry,
} from "./organizationRegistry";

import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Analysis from "./pages/Analysis";
import Import from "./pages/Import";
import AICFO from "./pages/AICFO";
import ActionCenter from "./pages/ActionCenter";
import FinancialIntelligenceHistory from "./pages/FinancialIntelligenceHistory";
import Reports from "./pages/Reports";
import FinancialHealth from "./pages/FinancialHealth";
import Budget from "./pages/Budget";
import Grants from "./pages/Grants";
import Projects from "./pages/Projects";
import Settings from "./pages/Settings";


const INSPECTION_STORAGE_KEY =
  "ai-fos-current-inspection-result";


function loadStoredInspectionResult() {
  try {
    const storedResult =
      sessionStorage.getItem(
        INSPECTION_STORAGE_KEY
      );

    if (!storedResult) {
      return null;
    }

    return JSON.parse(
      storedResult
    );
  } catch (storageError) {
    console.error(
      "Inspection result restore error:",
      storageError
    );

    return null;
  }
}


function App() {
  const [
    dashboard,
    setDashboard,
  ] = useState(null);

  const [
    readiness,
    setReadiness,
  ] = useState(null);

  const [
    error,
    setError,
  ] = useState("");

  const [
    selectedFile,
    setSelectedFile,
  ] = useState(null);

  const [
    uploadStatus,
    setUploadStatus,
  ] = useState("");

  const [
    inspectionResult,
    setInspectionResult,
  ] = useState(
    loadStoredInspectionResult
  );

  const [
    organizationList,
    setOrganizationList,
  ] = useState([]);

  const [
    currentOrganization,
    setCurrentOrganization,
  ] = useState(
    defaultOrganization
  );


  useEffect(() => {
    try {
      if (inspectionResult) {
        sessionStorage.setItem(
          INSPECTION_STORAGE_KEY,
          JSON.stringify(
            inspectionResult
          )
        );
      } else {
        sessionStorage.removeItem(
          INSPECTION_STORAGE_KEY
        );
      }
    } catch (storageError) {
      console.error(
        "Inspection result storage error:",
        storageError
      );
    }
  }, [inspectionResult]);


  useEffect(() => {
    let cancelled = false;

    async function loadOrganizationRegistry() {
      try {
        const response =
          await api.get(
            "/organisations/registry"
          );

        if (cancelled) {
          return;
        }

        const registryOrganizations =
          response.data?.organizations ?? [];

        const registry =
          setOrganizationsFromRegistry(
            registryOrganizations
          );

        setOrganizationList(
          Object.values(registry)
        );

        setCurrentOrganization(
          (current) =>
            registry[current?.id] ??
            registry.acss ??
            Object.values(registry)[0] ??
            current
        );
      } catch (registryError) {
        console.error(
          "Organization registry load error:",
          registryError
        );
      }
    }

    loadOrganizationRegistry();

    return () => {
      cancelled = true;
    };
  }, []);


  async function refreshOrganizationRegistry(
    selectOrganizationId = null
  ) {
    const response =
      await api.get(
        "/organisations/registry"
      );

    const registryOrganizations =
      response.data?.organizations ?? [];

    const registry =
      setOrganizationsFromRegistry(
        registryOrganizations
      );

    const refreshedOrganizationList =
      Object.values(registry);

    setOrganizationList(
      refreshedOrganizationList
    );

    if (selectOrganizationId) {
      const selectedOrganization =
        registry[selectOrganizationId];

      if (selectedOrganization) {
        setCurrentOrganization(
          selectedOrganization
        );
      }
    }

    return registry;
  }


  useEffect(() => {
    let cancelled = false;

    async function loadOrganizationData() {
      try {
        setError("");
        setReadiness(null);
        setDashboard(null);

        const readinessResponse =
          await api.get(
            `/organisations/${currentOrganization.id}/readiness`
          );

        if (cancelled) {
          return;
        }

        const readinessData =
          readinessResponse.data ?? null;

        setReadiness(
          readinessData
        );

        if (
          !readinessData
            ?.has_executive_dashboard
        ) {
          return;
        }

        const dashboardResponse =
          await api.get(
            "/dashboard",
            {
              params: {
                organisation_id:
                  currentOrganization.id,
              },
            }
          );

        if (!cancelled) {
          setDashboard(
            dashboardResponse.data
          );
        }
      } catch (requestError) {
        console.error(
          "Organization data load error:",
          requestError
        );

        if (!cancelled) {
          setDashboard(null);

          setError(
            "Could not load organization data."
          );
        }
      }
    }

    loadOrganizationData();

    return () => {
      cancelled = true;
    };
  }, [currentOrganization.id]);


  const handleUpload =
    async () => {
      if (!selectedFile) {
        setUploadStatus(
          "Please select a file first."
        );

        return;
      }

      setUploadStatus(
        "Uploading and inspecting file..."
      );

      setInspectionResult(null);

      const formData =
        new FormData();

      formData.append(
        "file",
        selectedFile
      );

      formData.append(
        "organisation_id",
        currentOrganization.id
      );

      formData.append(
        "organisation_name",
        currentOrganization.name
      );

      formData.append(
        "base_currency",
        currentOrganization.baseCurrency
      );

      try {
        const response =
          await fetch(
            "http://127.0.0.1:8000/upload",
            {
              method: "POST",
              body: formData,
            }
          );

        if (!response.ok) {
          const errorText =
            await response.text();

          throw new Error(
            `Upload failed (${response.status}): ${errorText}`
          );
        }

        const result =
          await response.json();

        console.log(
          "Workbook inspection result:",
          result
        );

        setInspectionResult(
          result
        );

        setUploadStatus(
          `File inspected successfully. Found ${result.sheet_count} sheet(s).`
        );
      } catch (uploadError) {
        console.error(
          "Upload error:",
          uploadError
        );

        setUploadStatus(
          `Upload failed: ${uploadError.message}`
        );

        return;
      }

      try {
        const readinessResponse =
          await api.get(
            `/organisations/${currentOrganization.id}/readiness`
          );

        const readinessData =
          readinessResponse.data ?? null;

        setReadiness(
          readinessData
        );

        if (
          readinessData
            ?.has_executive_dashboard
        ) {
          const dashboardResponse =
            await api.get(
              "/dashboard",
              {
                params: {
                  organisation_id:
                    currentOrganization.id,
                },
              }
            );

          setDashboard(
            dashboardResponse.data
          );
        } else {
          setDashboard(null);
        }

        setError("");
      } catch (refreshError) {
        console.error(
          "Organization refresh error:",
          refreshError
        );
      }
    };


  const health =
    dashboard?.financial_health;

  const budget =
    dashboard?.budget;

  const projectIntelligence =
    dashboard?.budget?.by_program;

  const fundingGap =
    dashboard?.funding_gap;

  const fundingGapInsights =
    dashboard?.funding_gap_insights;

  const grantDiagnostics =
    dashboard?.grant_diagnostics;

  const coreCostCoverage =
    dashboard?.core_cost_coverage;  

  const kpis =
    dashboard?.kpis;

  const alerts =
    dashboard?.alerts ?? [];


  return (
    <Routes>
      <Route
        path="/"
        element={
          <Dashboard
            health={health}
            kpis={kpis}
            alerts={alerts}
            error={error}
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
            setSelectedFile={
              setSelectedFile
            }
            setUploadStatus={
              setUploadStatus
            }
            setInspectionResult={
              setInspectionResult
            }
          />
        }
      />

      <Route
        path="/dashboard"
        element={
          <Dashboard
            health={health}
            kpis={kpis}
            alerts={alerts}
            error={error}
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
            setSelectedFile={
              setSelectedFile
            }
            setUploadStatus={
              setUploadStatus
            }
            setInspectionResult={
              setInspectionResult
            }
          />
        }
      />

      <Route
        path="/financial-health"
        element={
          <FinancialHealth
            health={health}
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/financial-history"
        element={
          <FinancialIntelligenceHistory
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/budget"
        element={
          <Budget
            budget={budget}
            coreCostCoverage={coreCostCoverage}
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/grants"
        element={
          <Grants
            fundingGap={
              fundingGap
            }
            fundingGapInsights={
              fundingGapInsights
            }
            grantDiagnostics={
              grantDiagnostics
            }
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/projects"
        element={
          <Projects
            projectIntelligence={
              projectIntelligence
            }
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/ai-cfo"
        element={
          <AICFO
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/action-center"
        element={
          <ActionCenter
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />      

      <Route
        path="/reports"
        element={
          <Reports
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
          />
        }
      />

      <Route
        path="/settings"
        element={
          <Settings
            readiness={readiness}
            organizationList={
              organizationList
            }
            currentOrganization={
              currentOrganization
            }
            setCurrentOrganization={
              setCurrentOrganization
            }
            refreshOrganizationRegistry={
              refreshOrganizationRegistry
            }
          />
        }
      />

      <Route
        path="/upload"
        element={
          <Upload
            selectedFile={
              selectedFile
            }
            setSelectedFile={
              setSelectedFile
            }
            uploadStatus={
              uploadStatus
            }
            setUploadStatus={
              setUploadStatus
            }
            handleUpload={
              handleUpload
            }
            inspectionResult={
              inspectionResult
            }
            setInspectionResult={
              setInspectionResult
            }
          />
        }
      />

      <Route
        path="/analysis"
        element={
          <Analysis
            inspectionResult={
              inspectionResult
            }
          />
        }
      />

      <Route
        path="/import"
        element={
          <Import
            inspectionResult={
              inspectionResult
            }
          />
        }
      />
    </Routes>
  );
}


export default App;