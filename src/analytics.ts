import type { Final, LaneSeedMap, LaneStat, FilterState, FilterOptions } from "./types";

export const SEED_ORDER_8: LaneSeedMap = { 4: 1, 5: 2, 3: 3, 6: 4, 2: 5, 7: 6, 1: 7, 8: 8 };
export const SEED_ORDER_10: LaneSeedMap = { 5: 1, 6: 2, 4: 3, 7: 4, 3: 5, 8: 6, 2: 7, 9: 8, 1: 9, 10: 10 };

export function getSeedMap(final: Final): LaneSeedMap {
  const maxLane = Math.max(...final.entries.map((e) => e.lane));
  return maxLane > 8 ? SEED_ORDER_10 : SEED_ORDER_8;
}

export function parseEvent(event: string): { distance: string; stroke: string } {
  // "100m Freestyle" -> {distance:"100m", stroke:"Freestyle"}
  // "4x100m Freestyle Relay" -> {distance:"4x100m", stroke:"Freestyle Relay"}
  const m = event.match(/^(\d+x?\d*m)\s+(.+)$/);
  if (!m) return { distance: "", stroke: event };
  return { distance: m[1], stroke: m[2] };
}

export function computeLaneStats(finals: Final[], excludeNonFinishers = true): LaneStat[] {
  const stats: Record<number, { appearances: number; wins: number; top3: number; differentials: number[] }> = {};

  for (const final of finals) {
    const seedMap = getSeedMap(final);

    for (const entry of final.entries) {
      // DNS means the lane was empty — don't count it
      if (entry.dns) continue;

      if (!stats[entry.lane]) {
        stats[entry.lane] = { appearances: 0, wins: 0, top3: 0, differentials: [] };
      }
      const s = stats[entry.lane];
      s.appearances += 1;

      if (entry.position !== null) {
        if (entry.position === 1) s.wins += 1;
        if (entry.position <= 3) s.top3 += 1;

        const expectedPos = seedMap[entry.lane];
        if (expectedPos !== undefined) {
          s.differentials.push(entry.position - expectedPos);
        }
      } else if (!excludeNonFinishers) {
        // DSQ/DNF still occupied the lane but didn't finish — differential undefined
      }
    }
  }

  return Object.entries(stats)
    .map(([lane, s]) => {
      const avg =
        s.differentials.length > 0
          ? s.differentials.reduce((a, b) => a + b, 0) / s.differentials.length
          : 0;
      return {
        lane: Number(lane),
        appearances: s.appearances,
        wins: s.wins,
        top3: s.top3,
        winRate: s.appearances > 0 ? (s.wins / s.appearances) * 100 : 0,
        top3Rate: s.appearances > 0 ? (s.top3 / s.appearances) * 100 : 0,
        avgDifferential: avg,
        differentials: s.differentials,
      } satisfies LaneStat;
    })
    .sort((a, b) => a.lane - b.lane);
}

export function filterFinals(finals: Final[], filters: FilterState): Final[] {
  return finals.filter((f) => {
    if (filters.competitions.length > 0 && !filters.competitions.includes(f.competition)) return false;
    if (f.year < filters.yearMin || f.year > filters.yearMax) return false;
    if (filters.gender !== "both" && f.gender !== filters.gender) return false;
    if (filters.pool !== "both" && f.pool !== filters.pool) return false;
    if (!filters.showRelays && f.is_relay) return false;

    if (filters.strokes.length > 0 || filters.distances.length > 0) {
      const { distance, stroke } = parseEvent(f.event);
      if (filters.strokes.length > 0 && !filters.strokes.includes(stroke)) return false;
      if (filters.distances.length > 0 && !filters.distances.includes(distance)) return false;
    }

    return true;
  });
}

export function getFilterOptions(finals: Final[]): FilterOptions {
  const competitions = [...new Set(finals.map((f) => f.competition))].sort();
  const years = [...new Set(finals.map((f) => f.year))].sort((a, b) => a - b);
  const parsed = finals.map((f) => parseEvent(f.event));
  const strokes = [...new Set(parsed.map((p) => p.stroke).filter(Boolean))].sort();
  const distances = [...new Set(parsed.map((p) => p.distance).filter(Boolean))].sort((a, b) => {
    const numA = parseInt(a.replace(/[^0-9]/g, ""), 10);
    const numB = parseInt(b.replace(/[^0-9]/g, ""), 10);
    return numA - numB;
  });
  return { competitions, years, strokes, distances };
}

export function computeSummaryStats(finals: Final[]) {
  if (finals.length === 0) {
    return { totalFinals: 0, totalAthletes: 0, yearRange: [0, 0] as [number, number], mostWinningLane: 0, mostWinningLaneWinRate: 0 };
  }
  const years = finals.map((f) => f.year);
  const athletes = new Set(finals.flatMap((f) => f.entries.map((e) => e.name)));
  const laneStats = computeLaneStats(finals);
  const best = laneStats.reduce((a, b) => (b.winRate > a.winRate ? b : a), laneStats[0]);
  return {
    totalFinals: finals.length,
    totalAthletes: athletes.size,
    yearRange: [Math.min(...years), Math.max(...years)] as [number, number],
    mostWinningLane: best.lane,
    mostWinningLaneWinRate: best.winRate,
  };
}
