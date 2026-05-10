import type { FilterState, FilterOptions } from "../../types";

interface Props {
  filters: FilterState;
  options: FilterOptions;
  onFilterChange: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  onReset: () => void;
  resultCount: number;
}

function MultiSelect({
  label,
  options,
  selected,
  onChange,
}: {
  label: string;
  options: string[];
  selected: string[];
  onChange: (v: string[]) => void;
}) {
  const toggle = (val: string) => {
    if (selected.includes(val)) {
      onChange(selected.filter((v) => v !== val));
    } else {
      onChange([...selected, val]);
    }
  };
  return (
    <div className="filter-group">
      <label className="filter-label">{label}</label>
      <div className="chip-group">
        {options.map((opt) => (
          <button
            key={opt}
            className={`chip ${selected.includes(opt) ? "chip--active" : ""}`}
            onClick={() => toggle(opt)}
            type="button"
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}

export function FilterBar({ filters, options, onFilterChange, onReset, resultCount }: Props) {
  const minYear = options.years[0] ?? 2000;
  const maxYear = options.years[options.years.length - 1] ?? 2024;

  return (
    <div className="filter-bar">
      <div className="filter-bar__row">
        <MultiSelect
          label="Competition"
          options={options.competitions}
          selected={filters.competitions}
          onChange={(v) => onFilterChange("competitions", v)}
        />

        <div className="filter-group">
          <label className="filter-label">Year range</label>
          <div className="year-range">
            <input
              type="range"
              min={minYear}
              max={maxYear}
              value={filters.yearMin}
              onChange={(e) => onFilterChange("yearMin", Number(e.target.value))}
            />
            <span className="year-range__display">
              {filters.yearMin} – {filters.yearMax}
            </span>
            <input
              type="range"
              min={minYear}
              max={maxYear}
              value={filters.yearMax}
              onChange={(e) => onFilterChange("yearMax", Number(e.target.value))}
            />
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Gender</label>
          <div className="chip-group">
            {(["both", "M", "F"] as const).map((g) => (
              <button
                key={g}
                className={`chip ${filters.gender === g ? "chip--active" : ""}`}
                onClick={() => onFilterChange("gender", g)}
                type="button"
              >
                {g === "both" ? "Both" : g === "M" ? "Men" : "Women"}
              </button>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Pool</label>
          <div className="chip-group">
            {(["both", "LCM", "SCM"] as const).map((p) => (
              <button
                key={p}
                className={`chip ${filters.pool === p ? "chip--active" : ""}`}
                onClick={() => onFilterChange("pool", p)}
                type="button"
              >
                {p === "both" ? "Both" : p}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="filter-bar__row">
        <MultiSelect
          label="Stroke"
          options={options.strokes}
          selected={filters.strokes}
          onChange={(v) => onFilterChange("strokes", v)}
        />

        <MultiSelect
          label="Distance"
          options={options.distances}
          selected={filters.distances}
          onChange={(v) => onFilterChange("distances", v)}
        />

        <div className="filter-group">
          <label className="filter-label">Relays</label>
          <label className="toggle">
            <input
              type="checkbox"
              checked={filters.showRelays}
              onChange={(e) => onFilterChange("showRelays", e.target.checked)}
            />
            <span>Include relays</span>
          </label>
        </div>
      </div>

      <div className="filter-bar__footer">
        <span className="result-count">{resultCount.toLocaleString()} finals</span>
        <button className="btn-reset" onClick={onReset} type="button">
          Reset filters
        </button>
      </div>
    </div>
  );
}
