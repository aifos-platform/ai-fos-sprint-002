import json

from fastapi.testclient import TestClient

from app.main import (
    app,
    organization_registry_service,
    workspace_service,
)
from app.services.organization_registry_service import (
    OrganizationRegistryService,
)


def test_registry_creates_default_organizations(
    tmp_path,
):
    registry_file = (
        tmp_path / "organization_registry.json"
    )

    service = OrganizationRegistryService(
        registry_file=registry_file
    )

    organizations = service.list_organizations()

    assert registry_file.exists()

    assert organizations == [
        {
            "id": "acss",
            "name": "ACSS",
            "base_currency": "USD",
            "active": True,
        },
        {
            "id": "naacss",
            "name": "NAACSS",
            "base_currency": "USD",
            "active": True,
        },
    ]


def test_registry_gets_organization_by_id(
    tmp_path,
):
    registry_file = (
        tmp_path / "organization_registry.json"
    )

    service = OrganizationRegistryService(
        registry_file=registry_file
    )

    organization = service.get_organization(
        "ACSS"
    )

    assert organization is not None
    assert organization["id"] == "acss"
    assert organization["name"] == "ACSS"
    assert (
        organization["base_currency"]
        == "USD"
    )


def test_registry_filters_inactive_organizations(
    tmp_path,
):
    registry_file = (
        tmp_path / "organization_registry.json"
    )

    registry_file.write_text(
        json.dumps(
            {
                "organizations": [
                    {
                        "id": "acss",
                        "name": "ACSS",
                        "base_currency": "USD",
                        "active": True,
                    },
                    {
                        "id": "inactive-org",
                        "name": "Inactive Org",
                        "base_currency": "USD",
                        "active": False,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    service = OrganizationRegistryService(
        registry_file=registry_file
    )

    active_organizations = (
        service.list_organizations()
    )

    all_organizations = (
        service.list_organizations(
            active_only=False
        )
    )

    assert len(active_organizations) == 1
    assert (
        active_organizations[0]["id"]
        == "acss"
    )

    assert len(all_organizations) == 2


def test_registry_endpoint_returns_organizations(
    tmp_path,
):
    original_registry_file = (
        organization_registry_service.registry_file
    )

    test_registry_file = (
        tmp_path / "organization_registry.json"
    )

    try:
        organization_registry_service.registry_file = (
            test_registry_file
        )

        client = TestClient(app)

        response = client.get(
            "/organisations/registry"
        )

        assert response.status_code == 200

        payload = response.json()

        assert "organizations" in payload

        assert payload["organizations"] == [
            {
                "id": "acss",
                "name": "ACSS",
                "base_currency": "USD",
                "active": True,
            },
            {
                "id": "naacss",
                "name": "NAACSS",
                "base_currency": "USD",
                "active": True,
            },
        ]

    finally:
        organization_registry_service.registry_file = (
            original_registry_file
        )


def test_registry_creates_new_organization(
    tmp_path,
):
    registry_file = (
        tmp_path / "organization_registry.json"
    )

    service = OrganizationRegistryService(
        registry_file=registry_file
    )

    organization = service.create_organization(
        organisation_id="Example NGO",
        name="Example NGO",
        base_currency="eur",
    )

    assert organization == {
        "id": "example-ngo",
        "name": "Example NGO",
        "base_currency": "EUR",
        "active": True,
    }

    stored_organization = (
        service.get_organization(
            "example-ngo"
        )
    )

    assert stored_organization == organization


def test_registry_rejects_duplicate_organization(
    tmp_path,
):
    registry_file = (
        tmp_path / "organization_registry.json"
    )

    service = OrganizationRegistryService(
        registry_file=registry_file
    )

    try:
        service.create_organization(
            organisation_id="acss",
            name="Duplicate ACSS",
            base_currency="USD",
        )
    except ValueError as exc:
        assert str(exc) == (
            "Organization already exists."
        )
    else:
        raise AssertionError(
            "Expected duplicate organization "
            "to be rejected."
        )


def test_onboarding_endpoint_creates_registry_and_workspace(
    tmp_path,
):
    original_registry_file = (
        organization_registry_service.registry_file
    )

    original_storage_root = (
        workspace_service.storage_root
    )

    test_registry_file = (
        tmp_path / "organization_registry.json"
    )

    test_storage_root = (
        tmp_path / "workspaces"
    )

    try:
        organization_registry_service.registry_file = (
            test_registry_file
        )

        workspace_service.storage_root = (
            test_storage_root
        )

        workspace_service.storage_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        client = TestClient(app)

        response = client.post(
            "/organisations/onboard",
            json={
                "id": "Example NGO",
                "name": "Example NGO",
                "base_currency": "eur",
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["status"] == "created"

        assert payload["organization"] == {
            "id": "example-ngo",
            "name": "Example NGO",
            "base_currency": "EUR",
            "active": True,
        }

        assert (
            payload["workspace"][
                "organisation_id"
            ]
            == "example-ngo"
        )

        workspace_id = (
            payload["workspace"][
                "workspace_id"
            ]
        )

        assert workspace_id

        metadata_path = (
            test_storage_root
            / workspace_id
            / "metadata.json"
        )

        assert metadata_path.exists()

        workspace = (
            workspace_service
            .get_workspace_by_organisation(
                "example-ngo"
            )
        )

        assert workspace is not None
        assert (
            workspace["organisation_name"]
            == "Example NGO"
        )
        assert (
            workspace["base_currency"]
            == "EUR"
        )

    finally:
        organization_registry_service.registry_file = (
            original_registry_file
        )

        workspace_service.storage_root = (
            original_storage_root
        )


def test_onboarding_endpoint_rejects_duplicate(
    tmp_path,
):
    original_registry_file = (
        organization_registry_service.registry_file
    )

    original_storage_root = (
        workspace_service.storage_root
    )

    test_registry_file = (
        tmp_path / "organization_registry.json"
    )

    test_storage_root = (
        tmp_path / "workspaces"
    )

    try:
        organization_registry_service.registry_file = (
            test_registry_file
        )

        workspace_service.storage_root = (
            test_storage_root
        )

        workspace_service.storage_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        client = TestClient(app)

        first_response = client.post(
            "/organisations/onboard",
            json={
                "id": "example-ngo",
                "name": "Example NGO",
                "base_currency": "USD",
            },
        )

        second_response = client.post(
            "/organisations/onboard",
            json={
                "id": "example-ngo",
                "name": "Example NGO",
                "base_currency": "USD",
            },
        )

        assert first_response.status_code == 200
        assert (
            second_response.status_code
            == 409
        )

        assert second_response.json() == {
            "detail": (
                "An organization with this ID "
                "already exists."
            )
        }

    finally:
        organization_registry_service.registry_file = (
            original_registry_file
        )

        workspace_service.storage_root = (
            original_storage_root
        )


def test_onboarding_endpoint_rejects_invalid_currency(
    tmp_path,
):
    original_registry_file = (
        organization_registry_service.registry_file
    )

    original_storage_root = (
        workspace_service.storage_root
    )

    test_registry_file = (
        tmp_path / "organization_registry.json"
    )

    test_storage_root = (
        tmp_path / "workspaces"
    )

    try:
        organization_registry_service.registry_file = (
            test_registry_file
        )

        workspace_service.storage_root = (
            test_storage_root
        )

        workspace_service.storage_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        client = TestClient(app)

        response = client.post(
            "/organisations/onboard",
            json={
                "id": "example-ngo",
                "name": "Example NGO",
                "base_currency": "US",
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "detail": (
                "Base currency must be a "
                "3-letter currency code."
            )
        }

    finally:
        organization_registry_service.registry_file = (
            original_registry_file
        )

        workspace_service.storage_root = (
            original_storage_root
        )