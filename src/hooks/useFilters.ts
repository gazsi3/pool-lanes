import { useState, useMemo, useCallback } from "react";
import type { Final, FilterState, FilterOptions } from "../types";
import { filterFinals, getFilterOptions } from "../analytics";

const DEFAULT_FILTERS: FilterState = {
  competitions: [],
  yearMin: 2000,
  yearMax: 2024,
  gender: "both",
  strokes: [],
  distances: [],
  pool: "both",
  showRelays: false,
};

interface UseFiltersResult {
  filters: FilterState;
  setFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  resetFilters: () => void;
  filteredFinals: Final[];
  filterOptions: FilterOptions;
}

export function useFilters(finals: Final[]): UseFiltersResult {
  const [filters, setFilters] = useState<FilterState>(() => {
    if (finals.length === 0) return DEFAULT_FILTERS;
    const years = finals.map((f) => f.year);
    return {
      ...DEFAULT_FILTERS,
      yearMin: Math.min(...years),
      yearMax: Math.max(...years),
    };
  });

  const filterOptions = useMemo(() => getFilterOptions(finals), [finals]);

  // Sync year bounds when data loads
  const effectiveFilters = useMemo<FilterState>(() => {
    if (finals.length === 0) return filters;
    const years = finals.map((f) => f.year);
    return {
      ...filters,
      yearMin: Math.max(filters.yearMin, Math.min(...years)),
      yearMax: Math.min(filters.yearMax, Math.max(...years)),
    };
  }, [filters, finals]);

  const filteredFinals = useMemo(
    () => filterFinals(finals, effectiveFilters),
    [finals, effectiveFilters]
  );

  const setFilter = useCallback(
    <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const resetFilters = useCallback(() => {
    if (finals.length === 0) {
      setFilters(DEFAULT_FILTERS);
      return;
    }
    const years = finals.map((f) => f.year);
    setFilters({
      ...DEFAULT_FILTERS,
      yearMin: Math.min(...years),
      yearMax: Math.max(...years),
    });
  }, [finals]);

  return { filters: effectiveFilters, setFilter, resetFilters, filteredFinals, filterOptions };
}
