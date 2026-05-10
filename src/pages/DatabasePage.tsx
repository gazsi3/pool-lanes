import { FilterBar } from "../components/table/FilterBar";
import { FinalsTable } from "../components/table/FinalsTable";
import type { FilterState, FilterOptions, Final } from "../types";

interface Props {
  filters: FilterState;
  filteredFinals: Final[];
  filterOptions: FilterOptions;
  onFilterChange: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  onReset: () => void;
}

export function DatabasePage({ filters, filteredFinals, filterOptions, onFilterChange, onReset }: Props) {
  return (
    <div className="page">
      <FilterBar
        filters={filters}
        options={filterOptions}
        onFilterChange={onFilterChange}
        onReset={onReset}
        resultCount={filteredFinals.length}
      />
      <FinalsTable finals={filteredFinals} />
    </div>
  );
}
