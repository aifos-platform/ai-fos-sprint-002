import { useNavigate } from "react-router-dom";

function Analysis({
    inspectionResult,
}) {
    const navigate = useNavigate();

    const detectedColumns =
        inspectionResult?.detected_columns ?? {};

    const detectedFields = Object.values(
        detectedColumns
    ).filter(Boolean);

    const missingFields = Object.entries(
        detectedColumns
    )
        .filter(([, excelColumn]) => !excelColumn)
        .map(([aiFosField]) =>
            aiFosField
                .replaceAll("_", " ")
                .replace(/\b\w/g, (letter) =>
                    letter.toUpperCase()
                )
        );

    return (
        <div className="upload-page">

            <h1>AI-FOS Analysis</h1>

            <p>
                AI-FOS has successfully analysed your workbook.
            </p>

            <div className="inspection-result">

                <h2>Analysis Summary</h2>

                <p>
                    ✅ Document recognised:{" "}
                    {inspectionResult?.document_type
                        ?.replaceAll("_", " ")
                        .replace(/\b\w/g, (letter) =>
                            letter.toUpperCase()
                        ) ?? "Unknown"}
                </p>

                <p>
                    ✅ Workbook structure validated
                </p>

                <p>
                    ✅ {detectedFields.length} fields detected
                </p>

                {missingFields.length > 0 ? (
                    <div>
                        <p>
                            ⚠ {missingFields.length} optional field(s) missing:
                        </p>

                        <div className="validation-badges">
                            {missingFields.map((field) => (
                                <span
                                    className="validation-badge"
                                    key={field}
                                >
                                    {field}
                                </span>
                            ))}
                        </div>
                    </div>
                ) : (
                    <p>
                        ✅ No optional fields are missing
                    </p>
                )}

                <p>
                    ✅ Ready to build the financial model
                </p>

                <div className="mapping-actions">
                    <button
                        className="primary-button"
                        type="button"
                        onClick={() => navigate("/import")}
                    >
                        Import into AI-FOS
                    </button>

                </div>

            </div>

        </div>
    );
}

export default Analysis;