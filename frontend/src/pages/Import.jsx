function Import({
    inspectionResult,
}) {

    const documentType =
        inspectionResult?.document_type
            ?.replaceAll("_", " ")
            .replace(/\b\w/g, (letter) =>
                letter.toUpperCase()
            ) ?? "Unknown";

    const rowCount =
        inspectionResult?.row_count ?? 0;

    const columnCount =
        inspectionResult?.column_count ?? 0;

    return (
        <div className="upload-page">

            <h1>Building Your AI-FOS Financial Model</h1>

            <p>
                AI-FOS is analysing and preparing your financial data.
            </p>

            <div className="inspection-result">

                <h2>Import Progress</h2>

                <div className="import-summary">
                    <p>
                        <strong>Document:</strong> {documentType}
                    </p>

                    <p>
                        <strong>Rows:</strong> {rowCount}
                    </p>

                    <p>
                        <strong>Columns:</strong> {columnCount}
                    </p>
                </div>

                <p>✓ Reading workbook</p>

                <p>⏳ Analysing financial structure</p>

                <p>○ Building account hierarchy</p>

                <p>○ Creating financial dimensions</p>

                <p>○ Validating financial data</p>

                <p>○ Creating AI knowledge</p>

                <p>○ Saving AI-FOS project</p>

            </div>

        </div>
    );
}

export default Import;