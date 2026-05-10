export interface RaceEntry {
  lane: number;
  name: string;
  nationality: string;
  seed_time: string | null;
  final_time: string | null;
  position: number | null;
  dsq: boolean;
  dns: boolean;
  dnf: boolean;
  /** "WR" = World Record, "OR" = Olympic Record, "ER" = European Record, etc. */
  record_type?: string;
}

export interface Final {
  competition: string;
  year: number;
  location: string;
  pool: "LCM" | "SCM";
  event: string;
  gender: "M" | "F" | "X";
  is_relay: boolean;
  meet_id: string;
  event_id: string;
  entries: RaceEntry[];
}

export interface LaneStat {
  lane: number;
  appearances: number;
  wins: number;
  top3: number;
  winRate: number;
  top3Rate: number;
  avgDifferential: number;
  differentials: number[];
}

export type LaneSeedMap = Record<number, number>;

export interface FilterState {
  competitions: string[];
  yearMin: number;
  yearMax: number;
  gender: "M" | "F" | "both";
  strokes: string[];
  distances: string[];
  pool: "LCM" | "SCM" | "both";
  showRelays: boolean;
}

export interface FilterOptions {
  competitions: string[];
  years: number[];
  strokes: string[];
  distances: string[];
}

export interface Meta {
  scraped_at: string;
  record_count: number;
}
