from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class WorkspaceService:
    """
    Manages persistent AI-FOS workspaces.

    Each organisation receives one workspace containing:
    - uploaded source files
    - financial-model outputs
    - generated reports
    - AI knowledge
    - workspace metadata
    """

    def __init__(self, storage_root: str | Path = "data/workspaces") -> None:
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def create_workspace(
        self,
        organisation_id: str,
        organisation_name: str,
        base_currency: str = "USD",
    ) -> dict[str, Any]:
        """
        Create a workspace for an organisation.

        If a workspace already exists for the organisation,
        the existing workspace is returned.
        """

        organisation_id = organisation_id.strip().lower()
        organisation_name = organisation_name.strip()
        base_currency = base_currency.strip().upper()

        if not organisation_id:
            raise ValueError("Organisation ID is required.")

        if not organisation_name:
            raise ValueError("Organisation name is required.")

        existing_workspace = self.get_workspace_by_organisation(organisation_id)

        if existing_workspace is not None:
            return existing_workspace

        workspace_id = str(uuid4())
        created_at = self._utc_now()

        workspace_path = self.storage_root / workspace_id

        folders = {
            "uploads": workspace_path / "uploads",
            "financial_model": workspace_path / "financial_model",
            "reports": workspace_path / "reports",
            "ai_knowledge": workspace_path / "ai_knowledge",
        }

        for folder in folders.values():
            folder.mkdir(parents=True, exist_ok=True)

        metadata = {
            "workspace_id": workspace_id,
            "organisation_id": organisation_id,
            "organisation_name": organisation_name,
            "base_currency": base_currency,
            "status": "ready",
            "created_at": created_at,
            "updated_at": created_at,
            "last_import_at": None,
            "upload_count": 0,
            "document_counts": {},
            "paths": {name: str(path) for name, path in folders.items()},
        }

        self._write_metadata(workspace_path, metadata)

        return metadata

    def ensure_organization_workspace(
        self,
        organisation_id: str,
        organisation_name: str,
        base_currency: str = "USD",
    ) -> dict[str, Any]:
        """
        Ensure that an organization has exactly one
        persistent AI-FOS workspace.

        Existing workspaces are reused. A new workspace
        is created only when none exists.
        """

        existing_workspace = (
            self.get_workspace_by_organisation(
                organisation_id
            )
        )

        if existing_workspace is not None:
            return existing_workspace

        return self.create_workspace(
            organisation_id=organisation_id,
            organisation_name=organisation_name,
            base_currency=base_currency,
        )    

    def get_workspace(
        self,
        workspace_id: str,
    ) -> dict[str, Any] | None:
        """
        Load a workspace by its workspace ID.
        """

        workspace_path = self.storage_root / workspace_id
        metadata_path = workspace_path / "metadata.json"

        if not metadata_path.exists():
            return None

        return self._read_json(metadata_path)

    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ) -> dict[str, Any] | None:
        """
        Find the workspace belonging to an organisation.
        """

        normalized_id = (
            str(organisation_id)
            .strip()
            .lower()
        )

        for metadata_path in self.storage_root.glob(
            "*/metadata.json"
        ):
            metadata = self._read_json(metadata_path)

            workspace_organisation_id = (
                str(
                    metadata.get(
                        "organisation_id",
                        "",
                    )
                )
                .strip()
                .lower()
            )

            if (
                workspace_organisation_id
                == normalized_id
            ):
                return metadata

        return None

    def list_workspaces(self) -> list[dict[str, Any]]:
        """
        Return all available workspaces.
        """

        workspaces: list[dict[str, Any]] = []

        for metadata_path in self.storage_root.glob("*/metadata.json"):
            workspaces.append(self._read_json(metadata_path))

        return sorted(
            workspaces,
            key=lambda item: item.get("created_at", ""),
        )

    def save_upload(
        self,
        workspace_id: str,
        source_file: str | Path,
        document_type: str,
    ) -> dict[str, Any]:
        """
        Copy an uploaded file into the workspace and update
        its metadata.
        """

        metadata = self.get_workspace(workspace_id)

        if metadata is None:
            raise ValueError(f"Workspace '{workspace_id}' was not found.")

        source_path = Path(source_file)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file '{source_path}' was not found.")

        workspace_path = self.storage_root / workspace_id
        upload_folder = workspace_path / "uploads"
        upload_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        destination_name = f"{timestamp}_{source_path.name}"

        destination_path = upload_folder / destination_name

        shutil.copy2(
            source_path,
            destination_path,
        )

        document_type = document_type.strip().lower() or "unknown"

        document_counts = metadata.get(
            "document_counts",
            {},
        )

        document_counts[document_type] = document_counts.get(document_type, 0) + 1

        metadata["upload_count"] = metadata.get("upload_count", 0) + 1
        metadata["document_counts"] = document_counts
        metadata["last_import_at"] = self._utc_now()
        metadata["updated_at"] = self._utc_now()
        metadata["status"] = "data_uploaded"

        self._write_metadata(
            workspace_path,
            metadata,
        )

        return {
            "workspace_id": workspace_id,
            "document_type": document_type,
            "original_filename": source_path.name,
            "stored_filename": destination_name,
            "stored_path": str(destination_path),
            "size_bytes": destination_path.stat().st_size,
            "uploaded_at": metadata["last_import_at"],
        }

    def update_status(
        self,
        workspace_id: str,
        status: str,
    ) -> dict[str, Any]:
        """
        Update the current workspace processing status.
        """

        metadata = self.get_workspace(workspace_id)

        if metadata is None:
            raise ValueError(f"Workspace '{workspace_id}' was not found.")

        metadata["status"] = status.strip()
        metadata["updated_at"] = self._utc_now()

        workspace_path = self.storage_root / workspace_id

        self._write_metadata(
            workspace_path,
            metadata,
        )

        return metadata

    def save_financial_model_file(
        self,
        workspace_id: str,
        filename: str,
        data: Any,
    ) -> Path:
        """
        Save a JSON financial-model output inside the workspace.

        Examples:
        - dim_account.json
        - fact_gl.json
        - dim_calendar.json
        """

        metadata = self.get_workspace(workspace_id)

        if metadata is None:
            raise ValueError(f"Workspace '{workspace_id}' was not found.")

        workspace_path = self.storage_root / workspace_id
        model_folder = workspace_path / "financial_model"
        model_folder.mkdir(parents=True, exist_ok=True)

        safe_filename = filename.strip()

        if not safe_filename:
            raise ValueError("Filename is required.")

        if not safe_filename.endswith(".json"):
            safe_filename = f"{safe_filename}.json"

        output_path = model_folder / safe_filename

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        metadata["updated_at"] = self._utc_now()

        self._write_metadata(
            workspace_path,
            metadata,
        )

        return output_path

    def get_workspace_summary(
        self,
        workspace_id: str,
    ) -> dict[str, Any]:
        """
        Return a frontend-friendly workspace summary.
        """

        metadata = self.get_workspace(workspace_id)

        if metadata is None:
            raise ValueError(f"Workspace '{workspace_id}' was not found.")

        workspace_path = self.storage_root / workspace_id

        upload_folder = workspace_path / "uploads"
        model_folder = workspace_path / "financial_model"
        report_folder = workspace_path / "reports"

        return {
            **metadata,
            "stored_uploads": self._count_files(upload_folder),
            "financial_model_files": self._count_files(model_folder),
            "generated_reports": self._count_files(report_folder),
        }

    def _write_metadata(
        self,
        workspace_path: Path,
        metadata: dict[str, Any],
    ) -> None:
        metadata_path = workspace_path / "metadata.json"

        with metadata_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    @staticmethod
    def _read_json(
        path: Path,
    ) -> dict[str, Any]:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    @staticmethod
    def _count_files(folder: Path) -> int:
        if not folder.exists():
            return 0

        return sum(1 for path in folder.iterdir() if path.is_file())

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()
