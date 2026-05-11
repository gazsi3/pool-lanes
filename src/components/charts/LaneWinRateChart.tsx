import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { LaneStat } from "../../types";
import { SEED_ORDER_8 } from "../../analytics";

interface Props {
  laneStats: LaneStat[];
  height?: number;
}

const LANE_COLORS = {
  win: "#1d6fb8",
  top3: "#7fb3e0",
};

interface TooltipPayload {
  name: string;
  value: number;
  payload: LaneStat & { expectedSeed: number };
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <p className="tooltip-title">Lane {label}</p>
      <p>Seed position: {data.expectedSeed}</p>
      <p>Appearances: {data.appearances}</p>
      <p>
        Wins: {data.wins} ({payload.find((p) => p.name === "Win %")?.value.toFixed(1)}%)
      </p>
      <p>
        Top 3: {data.top3} ({payload.find((p) => p.name === "Top-3 %")?.value.toFixed(1)}%)
      </p>
    </div>
  );
}

export function LaneWinRateChart({ laneStats, height = 340 }: Props) {
  const [hidden, setHidden] = useState<Set<string>>(new Set());

  // Only show lanes 1-8
  const data = laneStats
    .filter((s) => s.lane >= 1 && s.lane <= 8)
    .map((s) => ({
      ...s,
      lane: `Lane ${s.lane}`,
      winRateRounded: parseFloat(s.winRate.toFixed(2)),
      top3RateRounded: parseFloat(s.top3Rate.toFixed(2)),
      expectedSeed: SEED_ORDER_8[s.lane] ?? s.lane,
    }));

  if (data.length === 0) {
    return <div className="chart-empty">No data for selected filters.</div>;
  }

  const toggleSeries = (key: string) => {
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  return (
    <div className="chart-wrapper">
      <h2 className="chart-title">Win &amp; Top-3 Rate by Lane</h2>
      <p className="chart-subtitle">
        Based on {data[0]?.appearances ?? 0}–
        {Math.max(...data.map((s) => s.appearances))} appearances per lane · lanes 1–8
      </p>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="lane" tick={{ fontSize: 13 }} />
          <YAxis
            tickFormatter={(v) => `${v}%`}
            domain={[0, "auto"]}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 13, cursor: "pointer" }}
            onClick={(e) => toggleSeries(e.dataKey as string)}
            formatter={(value, entry) => (
              <span style={{ opacity: hidden.has(entry.dataKey as string) ? 0.4 : 1 }}>
                {value}
              </span>
            )}
          />
          <ReferenceLine
            y={100 / 8}
            stroke="#9ca3af"
            strokeDasharray="4 4"
            label={{ value: "Expected (12.5%)", position: "insideTopRight", fontSize: 11, fill: "#9ca3af" }}
          />
          <Bar
            dataKey="winRateRounded"
            name="Win %"
            fill={LANE_COLORS.win}
            radius={[3, 3, 0, 0]}
            hide={hidden.has("winRateRounded")}
          />
          <Bar
            dataKey="top3RateRounded"
            name="Top-3 %"
            fill={LANE_COLORS.top3}
            radius={[3, 3, 0, 0]}
            hide={hidden.has("top3RateRounded")}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
