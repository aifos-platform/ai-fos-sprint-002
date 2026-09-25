from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module


class FakeWorkspaceService:
    def __init__(
        self,
        financial_model_folder: Path,
    ):
        self.financial_model_folder = (
            financial_model_folder
        )

    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ) -> dict:
        return {
            "paths": {
                "financial_model": str(
                    self.financial_model_folder
                ),
                "ai_knowledge": str(
                    self.financial_model_folder
                ),
            }
        }


class MissingWorkspaceService:
    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ):
        return None


def test_download_cfo_report_pdf_returns_pdf(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf_path = (
        financial_model_folder
        / "cfo_report.pdf"
    )

    pdf_path.write_bytes(
        b"%PDF-1.4\nAI-FOS test report"
    )

    monkeypatch.setattr(
        main_module,
        "workspace_service",
        FakeWorkspaceService(
            financial_model_folder
        ),
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/test-org/cfo/pdf"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "content-type"
        ]
        == "application/pdf"
    )

    assert (
        "AI-FOS_CFO_Financial_Intelligence_Report.pdf"
        in response.headers[
            "content-disposition"
        ]
    )

    assert response.content.startswith(
        b"%PDF"
    )


def test_download_cfo_report_pdf_returns_404_when_missing(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        main_module,
        "workspace_service",
        FakeWorkspaceService(
            financial_model_folder
        ),
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/test-org/cfo/pdf"
    )

    assert response.status_code == 404

    assert (
        "not available yet"
        in response.json()[
            "detail"
        ].lower()
    )


def test_download_cfo_report_excel_returns_xlsx(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    excel_path = (
        financial_model_folder
        / "cfo_report.xlsx"
    )

    expected_bytes = (
        b"PK\x03\x04AI-FOS test workbook"
    )

    excel_path.write_bytes(
        expected_bytes
    )

    monkeypatch.setattr(
        main_module,
        "workspace_service",
        FakeWorkspaceService(
            financial_model_folder
        ),
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/test-org/cfo/excel"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "content-type"
        ]
        == (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

    assert (
        "AI-FOS_CFO_Financial_Intelligence_Report.xlsx"
        in response.headers[
            "content-disposition"
        ]
    )

    assert response.content == expected_bytes


def test_download_cfo_report_excel_returns_404_when_missing(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        main_module,
        "workspace_service",
        FakeWorkspaceService(
            financial_model_folder
        ),
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/test-org/cfo/excel"
    )

    assert response.status_code == 404

    assert (
        "not available yet"
        in response.json()[
            "detail"
        ].lower()
    )


def test_download_cfo_report_excel_returns_404_when_workspace_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        main_module,
        "workspace_service",
        MissingWorkspaceService(),
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/missing-org/cfo/excel"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == (
            "No workspace found for this "
            "organization."
        )
    )


def test_download_cfo_report_excel_serves_persisted_file_without_generation(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    excel_path = (
        financial_model_folder
        / "cfo_report.xlsx"
    )

    expected_bytes = (
        b"PK\x03\x04persisted-ai-fos-workbook"
    )

    excel_path.write_bytes(
        expected_bytes
    )

    monkeypatch.setattr(
        main_module,
        "workspace_service",
        FakeWorkspaceService(
            financial_model_folder
        ),
    )

    def fail_if_generator_is_called(*args, **kwargs):
        raise AssertionError(
            "Excel report generator must not be "
            "called by the download endpoint."
        )

    monkeypatch.setattr(
        main_module,
        "generate_cfo_report_excel",
        fail_if_generator_is_called,
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/test-org/cfo/excel"
    )

    assert response.status_code == 200
    assert response.content == expected_bytes

def test_download_cfo_report_word_returns_docx(
    tmp_path,
    monkeypatch,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    financial_model_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    word_path = (
        financial_model_folder
        / "cfo_report.docx"
    )

    expected_bytes = (
        b"persisted-word-report"
    )

    word_path.write_bytes(
        expected_bytes
    )

    monkeypatch.setattr(
        main_module,
        "workspace_service",
        FakeWorkspaceService(
            financial_model_folder
        ),
    )

    client = TestClient(
        main_module.app
    )

    response = client.get(
        "/reports/test-org/cfo/word"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "content-type"
        ]
        == (
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        )
    )

    assert (
        "AI-FOS_CFO_Financial_Intelligence_Report.docx"
        in response.headers[
            "content-disposition"
        ]
    )

    assert response.content == expected_bytes
