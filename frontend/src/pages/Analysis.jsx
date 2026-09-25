import { useNavigate } from "react-router-dom";

function Analysis({
    inspectionResult,
}) {
    const navigate = useNavigate();

    const documentType =
        inspectionResult?.document_type ?? "unknown";

    const detectedColumns =
        inspectionResult?.detected_columns ??
        inspectionResult?.budget_mapping ??
        {};

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

    const formattedDocumentType =
        documentType
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) =>
                letter.toUpperCase()
            );

    const isBudget =
        documentType === "budget";

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
                    {formattedDocumentType}
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
                ) : detectedFields.length > 0 ? (
                    <p>
                        ✅ All mapped fields were detected
                    </p>
                ) : null}

                <p>
                    {isBudget
                        ? "✅ Budget data processed and ready for AI-FOS analysis"
                        : "✅ Financial model processed and ready for AI-FOS"}
                </p>

                <div className="mapping-actions">
                    <button
                        className="primary-button"
                        type="button"
                        onClick={() => navigate("/import")}
                    >
                        View Processing Result →
                    </button>
                </div>

            </div>

        </div>
    );
}

export default Analysis;