const fallbackOrganizations = {
  acss: {
    id: "acss",
    name: "ACSS",
    baseCurrency: "USD",
  },
  naacss: {
    id: "naacss",
    name: "NAACSS",
    baseCurrency: "USD",
  },
};


export let organizations = {
  ...fallbackOrganizations,
};

export let organizationList =
  Object.values(organizations);

export let defaultOrganization =
  organizations.acss;


export function setOrganizationsFromRegistry(
  registryOrganizations = []
) {
  const normalized = {};

  for (const organization of registryOrganizations) {
    if (!organization?.id) {
      continue;
    }

    normalized[organization.id] = {
      id: organization.id,
      name:
        organization.name ??
        organization.id,
      baseCurrency:
        organization.base_currency ??
        "USD",
    };
  }

  if (
    Object.keys(normalized).length === 0
  ) {
    organizations = {
      ...fallbackOrganizations,
    };
  } else {
    organizations = normalized;
  }

  organizationList =
    Object.values(organizations);

  defaultOrganization =
    organizations.acss ??
    organizationList[0] ??
    fallbackOrganizations.acss;

  return organizations;
}


export function getOrganization(
  organizationId
) {
  return (
    organizations[organizationId] ??
    defaultOrganization
  );
}


export {
  fallbackOrganizations,
};