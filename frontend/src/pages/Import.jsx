import { useNavigate } from "react-router-dom";

function Import({
    inspectionResult,
}) {
    const navigate = useNavigate();

    const rawDocumentType =
        inspectionResult?.document_type ?? "unknown";

    const documentType =
        rawDocumentType
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) =>
                letter.toUpperCase()
            );

    const rowCount =
        inspectionResult?.row_count ?? 0;

    const columnCount =
        inspectionResult?.column_count ?? 0;

    const modelValidation =
        inspectionResult?.model_validation ?? {};

    const validatedModels =
        Object.values(modelValidation).filter(
            (model) => model?.valid
        ).length;

    const totalModels =
        Object.keys(modelValidation).length;

    const isBudget =
        rawDocumentType === "budget";

    const isGeneralLedger =
        rawDocumentType === "general_ledger";

    const isChartOfAccounts =
        rawDocumentType === "chart_of_accounts";

    let pageTitle =
        "Financial Data Ready";

    let pageDescription =
        "AI-FOS has successfully processed your financial data.";

    let processingSteps = [
        "Workbook processed",
        "Financial structure analysed",
        "Financial data validated",
        "AI-FOS data saved",
    ];

    if (isGeneralLedger) {
        pageTitle =
            "Financial Model Ready";

        pageDescription =
            "AI-FOS has successfully processed your General Ledger and built the organisation's financial model.";

        processingSteps = [
            "Workbook processed",
            "General Ledger normalised",
            "Financial structure analysed",
            "Account hierarchy applied",
            "Financial dimensions created",
            "Financial data validated",
            "AI-FOS intelligence generated",
            "Organisation financial model saved",
        ];
    }

    if (isBudget) {
        pageTitle =
            "Budget Data Ready";

        pageDescription =
            "AI-FOS has successfully processed and saved the organisation's budget data.";

        processingSteps = [
            "Workbook processed",
            "Budget structure analysed",
            "Budget fields mapped",
            "Budget lines validated",
            "Grant period information processed",
            "Budget data saved",
            "Budget data ready for AI-FOS analysis",
        ];
    }

    if (isChartOfAccounts) {
        pageTitle =
            "Chart of Accounts Ready";

        pageDescription =
            "AI-FOS has successfully processed and prepared the organisation's Chart of Accounts.";

        processingSteps = [
            "Workbook processed",
            "Account structure analysed",
            "Account hierarchy validated",
            "Accounts enriched",
            "Account dimension created",
            "Chart of Accounts saved",
        ];
    }

    return (
        <div className="upload-page">

            <h1>{pageTitle}</h1>

            <p>
                {pageDescription}
            </p>

            <div className="inspection-result">

                <h2>Processing Complete</h2>

                <div className="import-summary">
                    <p>
                        <strong>Document:</strong>{" "}
                        {documentType}
                    </p>

                    <p>
                        <strong>Rows processed:</strong>{" "}
                        {rowCount}
                    </p>

                    <p>
                        <strong>Columns analysed:</strong>{" "}
                        {columnCount}
                    </p>

                    {totalModels > 0 && (
                        <p>
                            <strong>
                                Financial models validated:
                            </strong>{" "}
                            {validatedModels} / {totalModels}
                        </p>
                    )}
                </div>

                {processingSteps.map((step) => (
                    <p key={step}>
                        ✅ {step}
                    </p>
                ))}

                <div className="mapping-actions">
                    <button
                        className="primary-button"
                        type="button"
                        onClick={() =>
                            navigate("/dashboard")
                        }
                    >
                        Open AI-FOS Dashboard →
                    </button>
                </div>

            </div>

        </div>
    );
}

export default Import;