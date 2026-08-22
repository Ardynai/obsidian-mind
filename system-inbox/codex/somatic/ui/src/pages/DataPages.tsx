import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "../api";
import { packetCharts } from "../charts";
import { Blocked, Empty, ResultBlock } from "../components/States";
import { Heading, parseJsonObject } from "../components/ui";
import { granted, useAppStore } from "../store";

function showAlertFromEmergency(data: Record<string, unknown>) {
  const emergency = data.emergency as { triggered?: boolean; guidance?: string; kind?: string } | undefined;
  if (emergency?.triggered && emergency.guidance) {
    useAppStore.getState().setAlert({ text: emergency.guidance, kind: emergency.kind });
  }
}

export function AnalyzePage() {
  const [error, setError] = useState("");
  const [out, setOut] = useState<ReturnType<typeof packetCharts> | null>(null);
  const [results, setResults] = useState<Array<Record<string, unknown>>>([]);
  const [notes, setNotes] = useState<string[]>([]);
  if (!granted("analysis-insight") && !granted("ai-advisory")) {
    return (
      <div className="workspace">
        <Heading
          kicker="Your numbers"
          title="Analyze"
          lead="Compare a reading to your own baseline or a range you supply."
        />
        <Blocked scopeId="analysis-insight" label="analysis insight" />
      </div>
    );
  }
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = event.currentTarget;
    try {
      const payload = {
        question: (form.elements.namedItem("question") as HTMLTextAreaElement).value,
        packet: parseJsonObject((form.elements.namedItem("packet") as HTMLTextAreaElement).value, "Data packet"),
        references: parseJsonObject(
          (form.elements.namedItem("references") as HTMLTextAreaElement).value,
          "References",
        ),
        baselines: parseJsonObject(
          (form.elements.namedItem("baselines") as HTMLTextAreaElement).value,
          "Baselines",
        ),
      };
      const data = await api<Record<string, unknown>>("/api/analyze", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showAlertFromEmergency(data);
      const report = data.report as { results?: Array<Record<string, unknown>>; notes?: string[] };
      setOut(packetCharts(payload.packet));
      setResults(report?.results || []);
      setNotes(report?.notes || []);
    } catch (err) {
      if (err instanceof ApiError && err.payload.scope_id) {
        setError("");
        setResults([]);
        setOut(null);
        setNotes([`blocked:${String(err.payload.scope_id)}`]);
        return;
      }
      setError(err instanceof Error ? err.message : "Request failed");
    }
  }
  return (
    <div className="workspace">
      <Heading
        title="Analyze"
        lead="Informational comparison against your series or a range you pasted. Not a diagnosis."
      />
      <form onSubmit={onSubmit}>
        <label>
          <span>Question</span>
          <textarea id="question" name="question" defaultValue="What patterns stand out in my data?" />
        </label>
        <label>
          <span>Data packet (JSON)</span>
          <textarea id="packet" name="packet" defaultValue={'{\n  "resting_hr": [62, 64, 63, 70]\n}'} />
          <span className="help">Use your numbers. Somatic does not invent medical normals.</span>
        </label>
        <label>
          <span>Caller-supplied reference ranges (JSON, optional)</span>
          <textarea id="references" name="references" defaultValue="{}" />
        </label>
        <label>
          <span>Your own baseline series (JSON, optional)</span>
          <textarea id="baselines" name="baselines" defaultValue="{}" />
        </label>
        {error ? (
          <p className="error" id="analyze-error" role="alert">
            {error}
          </p>
        ) : null}
        <button className="primary" type="submit">
          Run analysis
        </button>
      </form>
      <div id="analyze-out">
        {notes[0]?.startsWith("blocked:") ? <Blocked scopeId={notes[0].slice(8)} /> : null}
        {out}
        {results.length === 0 && out ? (
          <Empty title="No findings" body="Check the notes below. Somatic does not invent a result." />
        ) : (
          results.map((result, i) => <ResultBlock key={i} result={result} />)
        )}
        {notes.filter((note) => !note.startsWith("blocked:")).map((note) => (
          <p key={note}>{note}</p>
        ))}
      </div>
    </div>
  );
}

export function SharePage() {
  const [error, setError] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [note, setNote] = useState("");
  if (!granted("professional-sharing")) {
    return (
      <div className="workspace">
        <Heading title="Share" lead="Build a clinician-facing summary that stays on this machine." />
        <Blocked scopeId="professional-sharing" label="professional sharing" />
      </div>
    );
  }
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = event.currentTarget;
    try {
      const data = await api<Record<string, unknown>>("/api/share", {
        method: "POST",
        body: JSON.stringify({
          question: (form.elements.namedItem("question") as HTMLTextAreaElement).value,
          packet: parseJsonObject((form.elements.namedItem("packet") as HTMLTextAreaElement).value, "Data packet"),
          patient_label: (form.elements.namedItem("patient") as HTMLInputElement).value,
          clinician_note: (form.elements.namedItem("clinician") as HTMLInputElement).value,
        }),
      });
      setNote(String(data.note || ""));
      setMarkdown(String(data.markdown || ""));
    } catch (err) {
      if (err instanceof ApiError && err.payload.scope_id) {
        setError(`blocked:${String(err.payload.scope_id)}`);
        return;
      }
      setError(err instanceof Error ? err.message : "Request failed");
    }
  }
  return (
    <div className="workspace">
      <Heading title="Share" lead="Preview the clinician summary before you keep a local copy. Nothing is uploaded." />
      <form onSubmit={onSubmit}>
        <label>
          <span>Question</span>
          <textarea id="question" name="question" defaultValue="What patterns stand out in my data?" />
        </label>
        <label>
          <span>Data packet (JSON)</span>
          <textarea id="packet" name="packet" defaultValue={'{\n  "resting_hr": [62, 64, 63, 70]\n}'} />
        </label>
        <label>
          <span>Optional patient label</span>
          <input id="patient" name="patient" />
        </label>
        <label>
          <span>Optional clinician note</span>
          <input id="clinician" name="clinician" />
        </label>
        {error && !error.startsWith("blocked:") ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button className="primary" type="submit">
          Preview summary
        </button>
      </form>
      {error.startsWith("blocked:") ? <Blocked scopeId={error.slice(8)} /> : null}
      {markdown ? (
        <>
          <h2>Preview (not sent anywhere)</h2>
          <p className="muted">{note}</p>
          <pre className="code">{markdown}</pre>
          <button
            type="button"
            className="primary"
            onClick={() => {
              const blob = new Blob([markdown], { type: "text/markdown" });
              const url = URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = "somatic-summary.md";
              document.body.append(link);
              link.click();
              link.remove();
              URL.revokeObjectURL(url);
            }}
          >
            Download Markdown
          </button>
        </>
      ) : null}
    </div>
  );
}

export function IngestPage() {
  const [error, setError] = useState("");
  const [count, setCount] = useState<number | null>(null);
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);
  const [saved, setSaved] = useState(false);
  const [pending, setPending] = useState<{ path: string; text: string } | null>(null);
  useEffect(() => {
    api<{ reading_count: number }>("/api/ingest")
      .then((data) => setCount(data.reading_count))
      .catch((err: Error) => setError(err.message));
  }, []);
  if (!granted("data-ingestion")) {
    return (
      <div className="workspace">
        <Heading title="Data ingestion" lead="Import a CSV or Apple Health export after a preview." />
        <Blocked scopeId="data-ingestion" label="data ingestion" />
      </div>
    );
  }
  async function runIngest(path: string, text: string, save: boolean) {
    setError("");
    const data = await api<{ saved: boolean; packet: { readings: unknown[] } }>(path, {
      method: "POST",
      body: JSON.stringify({ text, save }),
    });
    if (!data.packet.readings.length) {
      setPreview(null);
      setPending(null);
      setSaved(false);
      setError("empty");
      return;
    }
    setPreview(data.packet as unknown as Record<string, unknown>);
    setSaved(data.saved);
    setPending(data.saved ? null : { path, text });
    if (data.saved) {
      const stored = await api<{ reading_count: number }>("/api/ingest");
      setCount(stored.reading_count);
    }
  }
  return (
    <div className="workspace">
      <Heading title="Data ingestion" lead="Preview first. Nothing is stored until you confirm." />
      <p>Currently stored readings: {count ?? "…"}</p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          const csv = (event.currentTarget.elements.namedItem("csv") as HTMLTextAreaElement).value;
          try {
            await runIngest("/api/ingest/csv", csv, false);
          } catch (err) {
            setError(err instanceof Error ? err.message : "Request failed");
          }
        }}
      >
        <h2>CSV</h2>
        <label>
          <span>CSV text</span>
          <textarea
            id="csv"
            name="csv"
            defaultValue={"metric,value,observed_at\nresting_hr,72,2026-01-01T00:00:00Z\n"}
          />
          <span className="help">Header must include metric, value, observed_at.</span>
        </label>
        <button className="primary" type="submit">
          Preview CSV
        </button>
      </form>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          const xml = (event.currentTarget.elements.namedItem("xml") as HTMLTextAreaElement).value;
          try {
            await runIngest("/api/ingest/apple-health", xml, false);
          } catch (err) {
            setError(err instanceof Error ? err.message : "Request failed");
          }
        }}
      >
        <h2>Apple Health export.xml</h2>
        <label>
          <span>XML text</span>
          <textarea id="xml" name="xml" />
        </label>
        <button type="submit">Preview Apple Health XML</button>
      </form>
      {error && error !== "empty" ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {error === "empty" ? (
        <Empty
          title="Nothing to store"
          body="The preview contained no readings. Check CSV headers (metric, value, observed_at) or the Apple Health export."
        />
      ) : null}
      {preview ? (
        <>
          <h2>{saved ? "Stored" : "Preview (not stored yet)"}</h2>
          <p>
            Readings in this packet:{" "}
            {Array.isArray(preview.readings) ? preview.readings.length : 0}
          </p>
          <pre className="code">{JSON.stringify(preview, null, 2)}</pre>
          {pending ? (
            <button className="primary" type="button" onClick={() => runIngest(pending.path, pending.text, true)}>
              Store these readings
            </button>
          ) : null}
        </>
      ) : null}
    </div>
  );
}

export function ExperimentsPage() {
  const [listed, setListed] = useState<{ tags: Array<Record<string, string>> } | null>(null);
  const [error, setError] = useState("");
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  useEffect(() => {
    if (!granted("data-ingestion") && !granted("analysis-insight")) return;
    api<{ tags: Array<Record<string, string>> }>("/api/experiments")
      .then(setListed)
      .catch((err: Error) => setError(err.message));
  }, []);
  if (!granted("data-ingestion") && !granted("analysis-insight")) {
    return (
      <div className="workspace">
        <Heading title="N-of-1 experiments" lead="Tag an interval and compare your own series." />
        <Blocked scopeId="data-ingestion" label="data ingestion" />
      </div>
    );
  }
  return (
    <div className="workspace">
      <Heading
        title="N-of-1 experiments"
        lead="Own-baseline only. No population normals, no effectiveness claims."
      />
      <p>Saved tags: {listed?.tags.length ?? 0}</p>
      {listed && listed.tags.length ? (
        <ul>
          {listed.tags.map((tag) => (
            <li key={`${tag.name}-${tag.started_at}`}>
              {tag.name} / {tag.metric} @ {tag.started_at}
            </li>
          ))}
        </ul>
      ) : (
        <Empty
          title="No tags yet"
          body="Save an interval name and start time, then evaluate against your own series."
        />
      )}
      {granted("data-ingestion") ? (
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            setError("");
            try {
              const data = await api<Record<string, unknown>>("/api/experiments/tag", {
                method: "POST",
                body: JSON.stringify({
                  name: (form.elements.namedItem("name") as HTMLInputElement).value,
                  metric: (form.elements.namedItem("metric") as HTMLInputElement).value,
                  started_at: (form.elements.namedItem("started") as HTMLInputElement).value,
                  note: (form.elements.namedItem("note") as HTMLInputElement).value,
                }),
              });
              if (data.emergency) {
                useAppStore.getState().setAlert({
                  text: String(data.guidance || ""),
                  kind: String(data.kind || ""),
                });
                return;
              }
              window.dispatchEvent(new Event("somatic:refresh"));
            } catch (err) {
              if (err instanceof ApiError && err.payload.scope_id) {
                setError(`blocked:${String(err.payload.scope_id)}`);
                return;
              }
              setError(err instanceof Error ? err.message : "Request failed");
            }
          }}
        >
          <h2>Tag an interval</h2>
          <label>
            <span>Name</span>
            <input id="exp-name" name="name" required />
          </label>
          <label>
            <span>Metric</span>
            <input id="exp-metric" name="metric" required />
          </label>
          <label>
            <span>Started at (UTC)</span>
            <input id="exp-started" name="started" required placeholder="2026-01-01T00:00:00Z" />
          </label>
          <label>
            <span>Note</span>
            <input id="exp-note" name="note" />
          </label>
          <button className="primary" type="submit">
            Save tag
          </button>
        </form>
      ) : (
        <Blocked scopeId="data-ingestion" label="data ingestion" />
      )}
      {granted("analysis-insight") ? (
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const name = (document.getElementById("exp-name") as HTMLInputElement | null)?.value;
            const metric = (document.getElementById("exp-metric") as HTMLInputElement | null)?.value;
            const started = (document.getElementById("exp-started") as HTMLInputElement | null)?.value;
            const note = (document.getElementById("exp-note") as HTMLInputElement | null)?.value;
            try {
              const data = await api<Record<string, unknown>>("/api/experiments/evaluate", {
                method: "POST",
                body: JSON.stringify({
                  name: name || "untagged-interval",
                  metric,
                  started_at: started,
                  note,
                  packet: parseJsonObject(
                    (form.elements.namedItem("packet") as HTMLTextAreaElement).value,
                    "Data packet",
                  ),
                }),
              });
              setReport(data.report as Record<string, unknown>);
            } catch (err) {
              setError(err instanceof Error ? err.message : "Request failed");
            }
          }}
        >
          <h2>Evaluate against your own series</h2>
          <label>
            <span>Data packet</span>
            <textarea
              id="exp-packet"
              name="packet"
              defaultValue={
                '{\n  "resting_hr": [\n    {"value": 62, "observed_at": "2026-01-01T00:00:00Z"},\n    {"value": 70, "observed_at": "2026-01-08T00:00:00Z"}\n  ]\n}'
              }
            />
          </label>
          <button type="submit">Evaluate n-of-1</button>
        </form>
      ) : (
        <Blocked scopeId="analysis-insight" label="analysis insight" />
      )}
      {error.startsWith("blocked:") ? <Blocked scopeId={error.slice(8)} /> : null}
      {error && !error.startsWith("blocked:") ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {report ? (
        <>
          <h2>Experiment report</h2>
          <p>Movement: {String(report.movement)}</p>
          <ResultBlock result={(report.result as Record<string, unknown>) || {}} />
        </>
      ) : null}
    </div>
  );
}
