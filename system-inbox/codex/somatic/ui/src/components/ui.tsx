import type { ReactNode } from "react";
import { navigate } from "../routes";

export function Link({
  href,
  children,
  className,
}: {
  href: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <a
      href={href}
      className={className}
      onClick={(event) => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) {
          return;
        }
        event.preventDefault();
        navigate(href);
      }}
    >
      {children}
    </a>
  );
}

export function Heading({
  title,
  lead,
  kicker,
}: {
  title: string;
  lead?: string;
  kicker?: string;
}) {
  return (
    <>
      {kicker ? <p className="kicker">{kicker}</p> : null}
      <h1>{title}</h1>
      {lead ? <p className="lead">{lead}</p> : null}
      <p className="info-banner">
        Informational only. Not a diagnosis or treatment. Confirm anything that matters with a
        licensed professional.
      </p>
    </>
  );
}

export function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

export function parseJsonObject(raw: string, label: string): Record<string, unknown> {
  const text = raw.trim();
  if (!text) return {};
  const parsed = JSON.parse(text) as unknown;
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error(`${label} must be a JSON object`);
  }
  return parsed as Record<string, unknown>;
}
