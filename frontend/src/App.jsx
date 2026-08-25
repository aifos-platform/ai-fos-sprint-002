import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";

import api from "./api";
import "./App.css";

import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Analysis from "./pages/Analysis";
import Import from "./pages/Import";
import AICFO from "./pages/AICFO";


function App() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [inspectionResult, setInspectionResult] = useState(null);

  const [currentOrganization, setCurrentOrganization] = useState({
    id: "acss",
    name: "ACSS",
  });


  useEffect(() => {
    api
      .get("/dashboard")
      .then((response) => {
        setDashboard(response.data);
      })
      .catch((requestError) => {
        console.error(
          "Dashboard load error:",
          requestError
        );

        setError(
          "Could not load dashboard data."
        );
      });
  }, []);


  const handleUpload = async () => {
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

    const formData = new FormData();

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
      "USD"
    );


    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          `Upload failed (${response.status}): ${errorText}`
        );
      }

      const result = await response.json();

      console.log(
        "Workbook inspection result:",
        result
      );

      setInspectionResult(result);

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
      const dashboardResponse = await api.get(
        "/dashboard"
      );

      setDashboard(
        dashboardResponse.data
      );

      setError("");

    } catch (dashboardError) {
      console.error(
        "Dashboard refresh error:",
        dashboardError
      );
    }
  };


  const health = dashboard?.financial_health;
  const kpis = dashboard?.kpis;
  const alerts = dashboard?.alerts ?? [];


  return (
    <Routes>

      <Route
        path="/"
        element={
          <Dashboard
            health={health}
            kpis={kpis}
            alerts={alerts}
            currentOrganization={currentOrganization}
            setCurrentOrganization={setCurrentOrganization}
            setSelectedFile={setSelectedFile}
            setUploadStatus={setUploadStatus}
            setInspectionResult={setInspectionResult}
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
            currentOrganization={currentOrganization}
            setCurrentOrganization={setCurrentOrganization}
            setSelectedFile={setSelectedFile}
            setUploadStatus={setUploadStatus}
            setInspectionResult={setInspectionResult}
          />
        }
      />

      <Route
        path="/ai-cfo"
        element={
          <AICFO
            currentOrganization={currentOrganization}
            setCurrentOrganization={setCurrentOrganization}
          />
        }
      />

      <Route
        path="/upload"
        element={
          <Upload
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            uploadStatus={uploadStatus}
            setUploadStatus={setUploadStatus}
            handleUpload={handleUpload}
            inspectionResult={inspectionResult}
            setInspectionResult={setInspectionResult}
          />
        }
      />

      <Route
        path="/analysis"
        element={
          <Analysis
            inspectionResult={inspectionResult}
          />
        }
      />

      <Route
        path="/import"
        element={
          <Import
            inspectionResult={inspectionResult}
          />
        }
      />

    </Routes>
  );
}


export default App;