import { useMemo } from "react";
import { LaneWinRateChart } from "../components/charts/LaneWinRateChart";
import { PerformanceDifferentialChart } from "../components/charts/PerformanceDifferentialChart";
import { FilterBar } from "../components/table/FilterBar";
import { computeLaneStats, computeSummaryStats } from "../analytics";
import type { FilterState, FilterOptions, Final } from "../types";

interface Props {
  filters: FilterState;
  filteredFinals: Final[];
  filterOptions: FilterOptions;
  onFilterChange: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  onReset: () => void;
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="stat-card">
      <div className="stat-card__value">{value}</div>
      <div className="stat-card__label">{label}</div>
      {sub && <div className="stat-card__sub">{sub}</div>}
    </div>
  );
}

export function DashboardPage({ filters, filteredFinals, filterOptions, onFilterChange, onReset }: Props) {
  const laneStats = useMemo(() => computeLaneStats(filteredFinals), [filteredFinals]);
  const summary = useMemo(() => computeSummaryStats(filteredFinals), [filteredFinals]);

  return (
    <div className="page">
      <FilterBar
        filters={filters}
        options={filterOptions}
        onFilterChange={onFilterChange}
        onReset={onReset}
        resultCount={filteredFinals.length}
      />

      <div className="stat-row">
        <StatCard label="Finals" value={summary.totalFinals.toLocaleString()} />
        <StatCard label="Unique athletes" value={summary.totalAthletes.toLocaleString()} />
        <StatCard
          label="Years covered"
          value={`${summary.yearRange[0]}–${summary.yearRange[1]}`}
        />
        <StatCard
          label="Most wins"
          value={`Lane ${summary.mostWinningLane}`}
          sub={`${summary.mostWinningLaneWinRate.toFixed(1)}% win rate`}
        />
      </div>

      <div className="charts-grid">
        <LaneWinRateChart laneStats={laneStats} />
        <PerformanceDifferentialChart laneStats={laneStats} />
      </div>
    </div>
  );
}
