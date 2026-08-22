import { useEffect, useState } from "react";
import { api } from "../api";
import { prefersReducedMotion } from "../motion";
import { scopeLabel, useAppStore } from "../store";

export function Blocked({ scopeId, label }: { scopeId: string; label?: string }) {
  const name = scopeLabel(scopeId) || label || scopeId;
  return (
    <div className="blocked" role="status">
      <h2>{name} is off</h2>
      <p>This screen stays quiet until you turn that scope on. Every scope starts off.</p>
      <button
        className="primary"
        type="button"
        onClick={async () => {
          await api("/api/consent/grant", {
            method: "POST",
            body: JSON.stringify({ scopes: [scopeId] }),
          });
          window.dispatchEvent(new Event("somatic:refresh"));
        }}
      >
        Turn on {name}
      </button>
    </div>
  );
}

export function Empty({ title, body }: { title: string; body: string }) {
  return (
    <div className="empty" role="status">
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  );
}

export function HonestNull({ text }: { text?: string }) {
  const fallback =
    (useAppStore.getState().meta?.honest_null as string) ||
    "No evidence available; consult a professional.";
  return (
    <div className="honest-null" role="status">
      <h2>No bound evidence</h2>
      <p>{text || fallback}</p>
    </div>
  );
}

export function ResultBlock({ result }: { result: Record<string, unknown> }) {
  const sources = Array.isArray(result.sources) ? (result.sources as string[]) : [];
  return (
    <article className="finding">
      <p>{String(result.summary || "")}</p>
      <p>
        <span className="pill">Grade: {String(result.evidence_grade || "none")}</span>
      </p>
      <p className="muted">
        {sources.length ? `Sources: ${sources.join(", ")}` : "Sources: (none)"}
      </p>
      {result.informational_notice ? (
        <p className="muted">{String(result.informational_notice)}</p>
      ) : null}
      {result.professional_routing ? (
        <p className="muted">{String(result.professional_routing)}</p>
      ) : null}
    </article>
  );
}

export function Skeleton() {
  return (
    <div className="skeleton" aria-busy="true" role="status">
      <span className="sr-only">Loading</span>
      <p className="spinner-braille" aria-hidden="true">
        <BrailleSpinner />
      </p>
      <div className="skeleton-line wide" />
      <div className="skeleton-line mid" />
      <div className="skeleton-line wide" />
    </div>
  );
}

const FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];

export function BrailleSpinner() {
  const [frame, setFrame] = useState(0);
  useEffect(() => {
    if (prefersReducedMotion()) return;
    const id = window.setInterval(() => setFrame((n) => (n + 1) % FRAMES.length), 80);
    return () => window.clearInterval(id);
  }, []);
  return <span className="spinner-braille">{FRAMES[frame]}</span>;
}
