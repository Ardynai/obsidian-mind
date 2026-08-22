import type { ReactElement } from "react";

export function numericSeries(
  packet: Record<string, unknown> | null | undefined,
): Array<{ label: string; values: number[] }> {
  if (!packet || typeof packet !== "object") return [];
  const series: Array<{ label: string; values: number[] }> = [];
  for (const [key, value] of Object.entries(packet)) {
    const nums: number[] = [];
    if (Array.isArray(value)) {
      for (const item of value) {
        const n =
          typeof item === "number"
            ? item
            : Number((item as { value?: unknown } | null)?.value);
        if (Number.isFinite(n)) nums.push(n);
      }
    } else if (typeof value === "number" && Number.isFinite(value)) {
      nums.push(value);
    }
    if (nums.length) series.push({ label: key, values: nums });
  }
  return series;
}

export function seriesChart(label: string, values: number[]): ReactElement {
  const width = 360;
  const height = 96;
  const pad = 10;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const pointAt = (value: number, index: number): [number, number] => {
    const x = pad + (index / Math.max(values.length - 1, 1)) * (width - pad * 2);
    const y = height - pad - ((value - min) / span) * (height - pad * 2);
    return [x, y];
  };
  const linePts = values.map((value, index) => pointAt(value, index).join(","));
  const first = pointAt(values[0], 0);
  const lastPt = pointAt(values[values.length - 1], values.length - 1);
  return (
    <div className="chart-wrap">
      <p className="muted">Your {label} series (own numbers only)</p>
      <svg
        className="chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={`${label}: ${values.length} of your own values, min ${min}, max ${max}. Not a population normal.`}
      >
        <line
          x1={pad}
          x2={width - pad}
          y1={height - pad}
          y2={height - pad}
          stroke="currentColor"
          strokeOpacity={0.2}
        />
        {values.length >= 2 ? (
          <>
            <polygon
              points={`${first[0]},${height - pad} ${linePts.join(" ")} ${lastPt[0]},${height - pad}`}
              fill="currentColor"
              fillOpacity={0.12}
            />
            <polyline
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinejoin="round"
              strokeLinecap="round"
              points={linePts.join(" ")}
            />
          </>
        ) : null}
        <circle cx={lastPt[0]} cy={lastPt[1]} r={3.5} fill="currentColor" />
      </svg>
    </div>
  );
}

export function packetCharts(
  packet: Record<string, unknown> | null | undefined,
): ReactElement[] {
  return numericSeries(packet)
    .filter((item) => item.values.length)
    .map((item) => seriesChart(item.label, item.values));
}
