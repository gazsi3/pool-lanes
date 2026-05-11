import { useState } from "react";
import { useFinalsData } from "./hooks/useFinalsData";
import { useFilters } from "./hooks/useFilters";
import { DashboardPage } from "./pages/DashboardPage";
import { DatabasePage } from "./pages/DatabasePage";

type Tab = "dashboard" | "database";

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const { finals, loading, error, meta } = useFinalsData();
  const { filters, setFilter, resetFilters, filteredFinals, filterOptions } = useFilters(finals);

  return (
    <div className="app">
      <header className="header">
        <div className="header__inner">
          <div className="header__brand">
            <span className="header__icon">🏊</span>
            <div>
              <h1 className="header__title">Pool Lanes</h1>
              <p className="header__subtitle">Swimming finals lane analysis · 2000 – 2024</p>
            </div>
          </div>
          <nav className="tabs">
            <button
              className={`tab ${tab === "dashboard" ? "tab--active" : ""}`}
              onClick={() => setTab("dashboard")}
              type="button"
            >
              Analysis
            </button>
            <button
              className={`tab ${tab === "database" ? "tab--active" : ""}`}
              onClick={() => setTab("database")}
              type="button"
            >
              Database
            </button>
          </nav>
        </div>
      </header>

      <main className="main">
        {loading && (
          <div className="loading">
            <div className="spinner" />
            <p>Loading finals data…</p>
          </div>
        )}

        {error && (
          <div className="error">
            <strong>Could not load data:</strong> {error}
          </div>
        )}

        {!loading && !error && (
          <>
            {tab === "dashboard" && (
              <DashboardPage
                filters={filters}
                filteredFinals={filteredFinals}
                filterOptions={filterOptions}
                onFilterChange={setFilter}
                onReset={resetFilters}
              />
            )}
            {tab === "database" && (
              <DatabasePage
                filters={filters}
                filteredFinals={filteredFinals}
                filterOptions={filterOptions}
                onFilterChange={setFilter}
                onReset={resetFilters}
              />
            )}
          </>
        )}
      </main>

      {meta && (
        <footer className="footer">
          Data from worldaquatics.com · Last updated{" "}
          {new Date(meta.scraped_at).toLocaleDateString("en-GB", { year: "numeric", month: "long", day: "numeric" })}
          {" · "}{meta.record_count.toLocaleString()} finals
        </footer>
      )}
    </div>
  );
}
