import { Link, useNavigate } from "react-router-dom";

function Upload({
    selectedFile,
    setSelectedFile,
    uploadStatus,
    setUploadStatus,
    handleUpload,
    inspectionResult,
    setInspectionResult,
}) {

    const navigate = useNavigate();

    return (
        <div className="upload-page">
            <Link to="/" className="secondary-button">
                Back to dashboard
            </Link>

            <h1>Upload Financial Data</h1>

            <p>Select the financial files you want AI-FOS to process.</p>

            <input
                type="file"
                accept=".xlsx,.xls,.csv"
                style={{ marginTop: "30px" }}
                onChange={(event) => {
                    const file = event.target.files?.[0] ?? null;

                    setSelectedFile(file);
                    setUploadStatus("");
                    setInspectionResult(null);
                }}
            />

            <button
                className="secondary-button"
                type="button"
                onClick={handleUpload}
                style={{ marginTop: "20px" }}
            >
                Upload file
            </button>

            <p style={{ marginTop: "15px" }}>{uploadStatus}</p>

            {inspectionResult && (
                <div className="inspection-result">
                    <h2>Workbook Inspection</h2>

                    <p>
                        <strong>Document type:</strong>{" "}
                        {inspectionResult.document_type}
                    </p>

                    <p>
                        <strong>Sheet:</strong>{" "}
                        {inspectionResult.sheet_name}
                    </p>

                    <p>
                        <strong>Rows:</strong>{" "}
                        {inspectionResult.row_count}
                    </p>

                    <p>
                        <strong>Columns:</strong>{" "}
                        {inspectionResult.column_count}
                    </p>

                    <h3>Detected Headers</h3>

                    <div className="headers-grid">
                        {inspectionResult.headers?.map((header, index) => (
                            <div
                                key={`${header}-${index}`}
                                className="header-card"
                            >
                                {header}
                            </div>
                        ))}
                    </div>

                    <h3>AI-FOS Column Mapping</h3>

                    <div className="mapping-table">
                        <div className="mapping-row mapping-header">
                            <span>AI-FOS Field</span>
                            <span>Detected Excel Column</span>
                            <span>Status</span>
                        </div>

                        {Object.entries(
                            inspectionResult.detected_columns ?? {}
                        ).map(([aiFosField, excelColumn]) => (
                            <div
                                className="mapping-row"
                                key={aiFosField}
                            >
                                <span>
                                    {aiFosField
                                        .replaceAll("_", " ")
                                        .replace(
                                            /\b\w/g,
                                            (letter) =>
                                                letter.toUpperCase()
                                        )}
                                </span>

                                <span>
                                    {excelColumn ?? "Not detected"}
                                </span>

                                <span
                                    className={
                                        excelColumn
                                            ? "mapping-success"
                                            : "mapping-warning"
                                    }
                                >
                                    {excelColumn
                                        ? "Detected"
                                        : "Missing"}
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className="mapping-actions">
                        <button
                            className="primary-button"
                            type="button"
                            onClick={() => navigate("/analysis")}
                        >
                            Continue →
                        </button>
                    </div>

                    {inspectionResult.model_validation && (
                        <>
                            <h3>Financial Model Validation</h3>

                            <div className="mapping-table">

                                <div className="mapping-row mapping-header">
                                    <span>Model</span>
                                    <span>Records</span>
                                    <span>Status</span>
                                </div>

                                <div className="mapping-row">
                                    <span>FACT_GL</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.fact_gl?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.fact_gl?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.fact_gl?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_ACCOUNT</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_account?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_account?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_account?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_FUND</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_fund?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_fund?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_fund?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_DONOR</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_donor?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_donor?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_donor?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_PROGRAM</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_program?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_program?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_program?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_CATEGORY</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_category?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_category?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_category?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_BUDGET_LINE</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_budget_line?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_budget_line?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_budget_line?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_DONOR_LINE</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_donor_line?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_donor_line?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_donor_line?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                                <div className="mapping-row">
                                    <span>DIM_CALENDAR</span>
                                    <span>
                                        {inspectionResult.model_validation
                                            ?.dim_calendar?.record_count ?? 0}
                                    </span>
                                    <span
                                        className={
                                            inspectionResult.model_validation
                                                ?.dim_calendar?.valid
                                                ? "mapping-success"
                                                : "mapping-warning"
                                        }
                                    >
                                        {inspectionResult.model_validation
                                            ?.dim_calendar?.valid
                                            ? "Valid"
                                            : "Missing"}
                                    </span>
                                </div>

                            </div>
                        </>
                    )}

                </div>
            )}
        </div>
    );
}

export default Upload;