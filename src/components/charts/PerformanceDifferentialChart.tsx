import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts";
import type { LaneStat } from "../../types";

interface Props {
  laneStats: LaneStat[];
  showDistribution?: boolean;
  height?: number;
}

interface TooltipPayload {
  payload: LaneStat & { laneLabel: string };
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  const avg = data.avgDifferential;
  return (
    <div className="chart-tooltip">
      <p className="tooltip-title">{data.laneLabel}</p>
      <p>Avg differential: {avg > 0 ? "+" : ""}{avg.toFixed(2)} positions</p>
      <p>{avg < 0 ? "Outperforms seed on average" : avg > 0 ? "Underperforms seed on average" : "Exactly as expected"}</p>
      <p>Sample size: {data.differentials.length} races</p>
    </div>
  );
}

export function PerformanceDifferentialChart({
  laneStats,
  showDistribution = true,
  height = 340,
}: Props) {
  const data = laneStats
    .filter((s) => s.differentials.length > 0)
    .map((s) => ({
      ...s,
      laneLabel: `Lane ${s.lane}`,
      avgDiffRounded: parseFloat(s.avgDifferential.toFixed(3)),
    }));

  if (data.length === 0) {
    return <div className="chart-empty">No data for selected filters.</div>;
  }

  // Scatter points for individual differentials
  const scatterData = laneStats.flatMap((s) =>
    s.differentials.map((d) => ({ laneLabel: `Lane ${s.lane}`, diff: d, size: 1 }))
  );

  return (
    <div className="chart-wrapper">
      <h2 className="chart-title">Performance vs. Seed Expectation</h2>
      <p className="chart-subtitle">
        Avg (actual finish − seeded finish). Negative = better than seeded.
      </p>

      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="laneLabel" tick={{ fontSize: 13 }} />
          <YAxis
            tickFormatter={(v) => (v > 0 ? `+${v}` : `${v}`)}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#374151" strokeWidth={1.5} label={{ value: "Expected", position: "insideTopRight", fontSize: 11, fill: "#374151" }} />
          <Bar dataKey="avgDiffRounded" name="Avg differential" radius={[3, 3, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.lane}
                fill={entry.avgDiffRounded < 0 ? "#1d6fb8" : entry.avgDiffRounded > 0 ? "#dc2626" : "#9ca3af"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {showDistribution && scatterData.length > 0 && (
        <div className="scatter-wrapper">
          <p className="chart-subtitle" style={{ marginTop: 12 }}>
            Individual race differentials (each dot = one final)
          </p>
          <ResponsiveContainer width="100%" height={180}>
            <ScatterChart margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="laneLabel" type="category" name="Lane" tick={{ fontSize: 12 }} />
              <YAxis dataKey="diff" name="Differential" tick={{ fontSize: 12 }} />
              <ZAxis range={[12, 12]} />
              <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} formatter={(v: number) => [v > 0 ? `+${v}` : `${v}`, "Diff"]} />
              <Scatter data={scatterData} fill="#1d6fb8" fillOpacity={0.25} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
