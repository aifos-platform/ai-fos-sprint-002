import { useLocation, useNavigate } from "react-router-dom";

const navigationItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Financial Health", path: "/financial-health" },
  { label: "Financial History", path: "/financial-history" },
  { label: "AI CFO", path: "/ai-cfo" },
  { label: "Action Center", path: "/action-center" },
  { label: "Budget", path: "/budget" },
  { label: "Grants", path: "/grants" },
  { label: "Projects", path: "/projects" },
  { label: "Reports", path: "/reports" },
  { label: "Settings", path: "/settings" },
];

function AppShell({
  children,
  eyebrow = "Executive workspace",
  title,
  organizationList = [],
  currentOrganization,
  setCurrentOrganization,
  onUploadData,
}) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleOrganizationChange = (event) => {
    const selected = organizationList.find(
      (organization) =>
        organization.id === event.target.value
    );

    if (selected && setCurrentOrganization) {
      setCurrentOrganization(selected);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">AF</div>

          <div>
            <h1>AI-FOS</h1>
            <p>Financial Intelligence</p>
          </div>
        </div>

        <nav className="nav-list">
          {navigationItems.map((item) => {
            const isActive =
              location.pathname === item.path;

            return (
              <button
                key={item.path}
                className={
                  isActive
                    ? "nav-item active"
                    : "nav-item"
                }
                type="button"
                onClick={() => navigate(item.path)}
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="dashboard-heading">
            <p className="eyebrow">
              {eyebrow}
            </p>

            {title && (
              <h2>
                {title}
              </h2>
            )}

            <p className="card-note">
              Organization:{" "}
              {currentOrganization?.name ??
                "No organization selected"}
            </p>
          </div>

          <div className="topbar-actions">
            {organizationList.length > 0 && (
              <select
                className="organization-selector"
                value={
                  currentOrganization?.id ?? ""
                }
                onChange={
                  handleOrganizationChange
                }
              >
                {organizationList.map(
                  (organization) => (
                    <option
                      key={organization.id}
                      value={organization.id}
                    >
                      {organization.name}
                    </option>
                  )
                )}
              </select>
            )}

            {onUploadData && (
              <button
                className="secondary-button"
                type="button"
                onClick={onUploadData}
              >
                Upload data
              </button>
            )}

            <div className="user-avatar">
              ER
            </div>
          </div>
        </header>

        {children}
      </main>
    </div>
  );
}

export default AppShell;