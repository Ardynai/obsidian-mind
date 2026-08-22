import { type FormEvent, type ReactNode, useState } from "react";
import { api } from "../api";
import { CitationList } from "../components/CitationList";
import { Blocked } from "../components/States";
import { Heading } from "../components/ui";
import { granted } from "../store";

function CiteForm({
  title,
  lead,
  path,
  fieldName,
  extra,
}: {
  title: string;
  lead: string;
  path: string;
  fieldName: string;
  extra?: (data: Record<string, unknown>) => ReactNode;
}) {
  const [error, setError] = useState("");
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);
    const value = (event.currentTarget.elements.namedItem(fieldName) as HTMLTextAreaElement).value;
    try {
      const result = await api<Record<string, unknown>>(path, {
        method: "POST",
        body: JSON.stringify({ [fieldName]: value, question: value, query: value }),
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="workspace">
      <Heading title={title} lead={lead} />
      <form onSubmit={onSubmit}>
        <label>
          <span>Question</span>
          <textarea id={fieldName} name={fieldName} />
        </label>
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button className="primary" type="submit" aria-busy={busy}>
          Search local corpus
        </button>
      </form>
      {busy && !data ? <p className="muted">Looking up…</p> : null}
      {data ? (
        <>
          {extra ? extra(data) : null}
          <CitationList data={data} />
        </>
      ) : null}
    </div>
  );
}

export function ResearchPage() {
  if (!granted("autonomous-research")) {
    return (
      <div className="workspace">
        <Heading
          kicker="Library"
          title="Research"
          lead="Local corpus by default. Optional live lookup is off unless you set SOMATIC_RESEARCH_LIVE. Claims must cite a retrieved passage."
        />
        <Blocked scopeId="autonomous-research" label="autonomous research" />
      </div>
    );
  }
  return (
    <CiteForm
      title="Research"
      lead="Local lookup by default. If nothing binds, you will see: No evidence available; consult a professional."
      path="/api/research"
      fieldName="question"
    />
  );
}

export function RemedyPage() {
  if (!granted("remedy-library")) {
    return (
      <div className="workspace">
        <Heading title="Remedy library" lead="Informational only. Unbound entries stay grade none." />
        <Blocked scopeId="remedy-library" label="remedy library" />
      </div>
    );
  }
  return (
    <CiteForm
      title="Remedy library"
      lead="Not a prescription. Default evidence grade is none when nothing binds."
      path="/api/remedy"
      fieldName="query"
      extra={(data) => {
        const entries =
          ((data.report as { entries?: Array<Record<string, unknown>> } | undefined)?.entries) || [];
        return entries.map((entry, i) => (
          <article className="finding" key={i}>
            <p>{String(entry.claim || "")}</p>
            <p>
              <span className="pill grade">Grade: {String(entry.evidence_grade)}</span>
            </p>
            <p className="muted">{Array.isArray(entry.safety_notes) ? entry.safety_notes.join(" ") : ""}</p>
          </article>
        ));
      }}
    />
  );
}

export function ParasitePage() {
  if (!granted("autonomous-research")) {
    return (
      <div className="workspace">
        <Heading title="Parasite Q&A" lead="Informational only. This path does not name a species." />
        <Blocked scopeId="autonomous-research" label="autonomous research" />
      </div>
    );
  }
  return (
    <CiteForm
      title="Parasite Q&A"
      lead="This path does not identify a parasite species and does not replace a clinician."
      path="/api/parasite"
      fieldName="question"
      extra={(data) => (
        <>
          <p>{String(data.routing_note || "")}</p>
          <p className="muted">Species identification: not provided.</p>
        </>
      )}
    />
  );
}
