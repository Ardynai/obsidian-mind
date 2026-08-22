import { useMemo } from "react";
import type { PoseJoints } from "../api";

export function namedJoints(joints: PoseJoints): Record<string, number[]> {
  if (Array.isArray(joints)) {
    const out: Record<string, number[]> = {};
    const names = ["head", "torso", "pelvis", "l_shoulder", "r_shoulder"];
    joints.slice(0, names.length).forEach((coords, i) => {
      if (Array.isArray(coords)) out[names[i]] = coords;
    });
    return out;
  }
  return joints && typeof joints === "object" ? joints : {};
}

export function AudioReadout({
  breathing,
  coughs,
  speechActivity,
}: {
  breathing?: number;
  coughs?: number;
  speechActivity?: number;
}) {
  return (
    <div className="gauges">
      <div className="gauge em">
        <span className="lab">Breathing</span>
        <span className="num">
          {String(breathing ?? "n/a")}
          <small> /min</small>
        </span>
      </div>
      <div className="gauge amber">
        <span className="lab">Cough events</span>
        <span className="num">{String(coughs ?? 0)}</span>
      </div>
      <div className="gauge cyan">
        <span className="lab">Speech activity</span>
        <span className="num">{String(speechActivity ?? "n/a")}</span>
      </div>
    </div>
  );
}

export function OccupancyStrip({
  history,
}: {
  history: number[][];
}) {
  const { width, height, cells } = useMemo(() => {
    const w = 480;
    const h = 180;
    const rows = history.slice(-48);
    const cols = rows[0]?.length || 0;
    const out: Array<{ x: number; y: number; w: number; h: number; o: number }> = [];
    if (!rows.length || !cols) return { width: w, height: h, cells: out };
    const cw = w / cols;
    const rh = h / rows.length;
    rows.forEach((row, y) => {
      row.forEach((value, x) => {
        out.push({ x: x * cw, y: y * rh, w: cw, h: rh, o: Math.max(0, Math.min(1, Number(value) || 0)) });
      });
    });
    return { width: w, height: h, cells: out };
  }, [history]);

  return (
    <svg
      className="occupancy-strip"
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Occupancy waterfall from CSI envelope features. Never raw IQ."
    >
      <rect width={width} height={height} fill="#050d0a" />
      {cells.map((cell, i) => (
        <rect
          key={i}
          x={cell.x}
          y={cell.y}
          width={cell.w}
          height={cell.h}
          fill={cell.o > 0.55 ? "#4CC4F5" : "#35E7A6"}
          fillOpacity={0.18 + cell.o * 0.82}
        />
      ))}
    </svg>
  );
}

export function FieldReadout({ snapshot }: { snapshot: Record<string, unknown> }) {
  const present = Boolean(snapshot.presence);
  const row = Array.isArray(snapshot.occupancy_row)
    ? (snapshot.occupancy_row as number[])
    : Array.isArray(snapshot.envelope)
      ? (snapshot.envelope as number[])
      : [];
  const occupancy =
    row.length > 0 ? (row.reduce((a, b) => a + Number(b || 0), 0) / row.length).toFixed(2) : "n/a";
  return (
    <div className="gauges">
      <div className="gauge em">
        <span className="lab">Breathing</span>
        <span className="num">
          {String(snapshot.breathing_rate_per_min ?? "n/a")}
          <small> /min</small>
        </span>
      </div>
      <div className="gauge cyan">
        <span className="lab">Occupancy</span>
        <span className="num">{occupancy}</span>
      </div>
      <div className="gauge amber">
        <span className="lab">Motion</span>
        <span className="num">{String(snapshot.motion_energy ?? "n/a")}</span>
      </div>
      <div className="gauge">
        <span className="lab">Presence</span>
        <span className="num" style={{ fontSize: "1.35rem", color: "var(--emerald)" }}>
          {present ? "PRESENT" : "ABSENT"}
        </span>
      </div>
    </div>
  );
}

export function TemplateBodySvg({
  joints,
  live,
}: {
  joints: PoseJoints;
  live?: boolean;
}) {
  if (live) {
    return (
      <p className="muted">
        Live CSI mode hides the skeleton. Occupancy features only. Not a body scan.
      </p>
    );
  }
  const named = namedJoints(joints);
  const head = named.head || [0.5, 0.12, 0.5];
  const torso = named.torso || [0.5, 0.42, 0.5];
  const hx = 20 + Number(head[0]) * 140;
  const hy = 16 + Number(head[1]) * 200;
  const tx = 20 + Number(torso[0]) * 140;
  const ty = 16 + Number(torso[1]) * 200;
  const lShoulder = [tx - 28, ty + 8];
  const rShoulder = [tx + 28, ty + 8];
  const hip = [tx, ty + 42];
  return (
    <svg
      className="body-fallback"
      viewBox="0 0 180 240"
      role="img"
      aria-label="2D fallback of the synthetic template body. Head and torso from sandbox joints; limbs are a template. Not a real person."
    >
      <rect width="180" height="240" fill="currentColor" fillOpacity="0.06" />
      <circle cx={hx} cy={hy} r="12" fill="currentColor" />
      <line x1={hx} y1={hy + 12} x2={tx} y2={ty} stroke="currentColor" strokeWidth="4" />
      <line
        x1={lShoulder[0]}
        y1={lShoulder[1]}
        x2={rShoulder[0]}
        y2={rShoulder[1]}
        stroke="currentColor"
        strokeWidth="4"
      />
      <line
        x1={lShoulder[0]}
        y1={lShoulder[1]}
        x2={lShoulder[0] - 6}
        y2={lShoulder[1] + 36}
        stroke="currentColor"
        strokeWidth="3"
      />
      <line
        x1={rShoulder[0]}
        y1={rShoulder[1]}
        x2={rShoulder[0] + 6}
        y2={rShoulder[1] + 36}
        stroke="currentColor"
        strokeWidth="3"
      />
      <line x1={tx} y1={ty} x2={hip[0]} y2={hip[1]} stroke="currentColor" strokeWidth="5" />
      <line
        x1={hip[0]}
        y1={hip[1]}
        x2={hip[0] - 16}
        y2={hip[1] + 52}
        stroke="currentColor"
        strokeWidth="3"
      />
      <line
        x1={hip[0]}
        y1={hip[1]}
        x2={hip[0] + 16}
        y2={hip[1] + 52}
        stroke="currentColor"
        strokeWidth="3"
      />
      <text x="90" y="228" textAnchor="middle" fontSize="9" fill="currentColor">
        2D fallback · synthetic
      </text>
    </svg>
  );
}

export function StagePoster({
  snapshot,
}: {
  snapshot: {
    live?: boolean;
    show_skeleton?: boolean;
    occupancy_row?: number[];
    envelope?: number[];
    pose3d?: { joints?: PoseJoints };
  };
}) {
  const live = snapshot.show_skeleton === false || Boolean(snapshot.live);
  const row = snapshot.occupancy_row || snapshot.envelope || [];
  const named = namedJoints(snapshot.pose3d?.joints || {});
  const head = named.head || [0.5, 0.18, 0.5];
  const torso = named.torso || [0.5, 0.42, 0.5];
  const hx = 210 + (Number(head[0]) - 0.5) * 80;
  const hy = 96 + Number(head[1]) * 20;
  const tx = 210 + (Number(torso[0]) - 0.5) * 80;
  const ty = 176 + Number(torso[1]) * 16;
  return (
    <svg className="stage-poster" viewBox="0 0 420 340" aria-hidden="true">
      <defs>
        <radialGradient id="bio-glow" cx="50%" cy="42%" r="60%">
          <stop offset="0" stopColor="#35E7A6" stopOpacity="0.28" />
          <stop offset="1" stopColor="#35E7A6" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="bio-bar" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0" stopColor="#12A574" />
          <stop offset="1" stopColor="#35E7A6" />
        </linearGradient>
      </defs>
      <rect width="420" height="340" fill="#050d0a" />
      <rect width="420" height="340" fill="url(#bio-glow)" />
      {row.map((value, i) => {
        const x = 30 + (i / Math.max(row.length - 1, 1)) * 360;
        const h = 24 + Number(value) * 88;
        return (
          <rect
            key={i}
            x={x}
            y={284 - h}
            width="6"
            height={h}
            fill="url(#bio-bar)"
            opacity={0.45 + Number(value) * 0.5}
          />
        );
      })}
      {!live ? (
        <g stroke="#8DF6C9" strokeWidth="4" fill="none" strokeLinecap="round">
          <circle cx={hx} cy={hy} r="20" fill="#0a1b14" stroke="#35E7A6" />
          <line x1={hx} y1={hy + 20} x2={tx} y2={ty} />
          <line x1={tx} y1={ty - 20} x2={tx - 34} y2={ty + 36} />
          <line x1={tx} y1={ty - 20} x2={tx + 34} y2={ty + 36} />
          <line x1={tx} y1={ty} x2={tx - 24} y2={ty + 54} />
          <line x1={tx} y1={ty} x2={tx + 24} y2={ty + 54} />
        </g>
      ) : null}
      <ellipse cx="210" cy="262" rx="66" ry="10" fill="#35E7A6" opacity="0.1" />
      <text
        x="210"
        y="28"
        textAnchor="middle"
        fill="#35E7A6"
        fontSize="11"
        fontFamily="IBM Plex Mono, monospace"
      >
        SANDBOX · SYNTHETIC TEMPLATE
      </text>
    </svg>
  );
}
