import { useLayoutEffect, useRef } from "react";
import type { Scope } from "./api";
import { prefersReducedMotion } from "./motion";

export function CountUp({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  useLayoutEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (prefersReducedMotion()) {
      node.textContent = String(value);
      return;
    }
    node.textContent = "0";
    const started = performance.now();
    const duration = 640;
    let frame = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - started) / duration);
      const eased = 1 - (1 - t) ** 3;
      node.textContent = String(Math.round(value * eased));
      if (t < 1) frame = window.requestAnimationFrame(tick);
    };
    frame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frame);
  }, [value]);
  return <span ref={ref}>{value}</span>;
}

export function Sparkline({
  values,
  label,
  color = "var(--emerald)",
}: {
  values: number[];
  label: string;
  color?: string;
}) {
  const width = 120;
  const height = 22;
  const pts = values.length
    ? values.map((value, index) => {
        const x = (index / Math.max(values.length - 1, 1)) * width;
        const y = height - 4 - Math.max(0, Math.min(1, value)) * (height - 8);
        return `${x},${y}`;
      })
    : [`0,${height - 4}`, `${width},${height - 4}`];
  return (
    <svg
      className="spark"
      width="100%"
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      role="img"
      aria-label={label}
    >
      <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth="2" opacity="0.85" />
    </svg>
  );
}

export function CapabilityRing({ scopes }: { scopes: Scope[] }) {
  const grantedCount = scopes.filter((row) => row.granted).length;
  const total = scopes.length || 7;
  const radius = 92;
  const circ = 2 * Math.PI * radius;
  const gap = circ * 0.035;
  const slot = circ / total;
  return (
    <div
      className="ringcard"
      role="img"
      aria-label={`${grantedCount} of ${total} consent scopes granted. Default is off.`}
    >
      <svg width="230" height="230" viewBox="0 0 230 230">
        <defs>
          <linearGradient id="bio-em" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#35E7A6" />
            <stop offset="1" stopColor="#12A574" />
          </linearGradient>
        </defs>
        <g transform="translate(115,115)">
          <circle r="92" fill="none" stroke="#173029" strokeWidth="12" />
          {scopes.map((row, index) => {
            const start = index * slot;
            return (
              <circle
                key={row.id}
                r={radius}
                fill="none"
                stroke={row.granted ? "url(#bio-em)" : "#1E6B4E"}
                strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={`${slot - gap} ${circ - (slot - gap)}`}
                strokeDashoffset={-start}
                opacity={row.granted ? 1 : 0.45}
                transform="rotate(-90)"
              />
            );
          })}
          <circle r="72" fill="none" stroke="#0e1f19" strokeWidth="2" />
        </g>
      </svg>
      <div className="cap" aria-hidden="true">
        <b>
          {grantedCount}
          <span style={{ color: "var(--faint)" }}>/{total}</span>
        </b>
        <span>capabilities</span>
      </div>
    </div>
  );
}
