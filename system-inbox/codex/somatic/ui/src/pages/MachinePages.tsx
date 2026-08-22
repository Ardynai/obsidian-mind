import { FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import { Empty } from "../components/States";
import { Heading } from "../components/ui";
import { CliTerminal } from "../tools/CliTerminal";

export function ToolsPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api<Record<string, unknown>>("/api/tools")
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);
  const cli = (data?.cli as string[]) || [];
  return (
    <div className="workspace">
      <Heading
        title="CLI companions"
        lead="These stay in the terminal so Fabric vectors and the slow doctor cascade are not reimplemented."
      />
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      <CliTerminal lines={cli} />
      <ul>
        {((data?.notes as string[]) || []).map((note) => (
          <li key={note}>{note}</li>
        ))}
      </ul>
      <h2>Commands on this machine</h2>
      <ul>
        {cli.map((line) => (
          <li key={line}>
            <code>{line}</code>
          </li>
        ))}
      </ul>
      <p className="muted">
        Fabric runtime: {String(data?.fabric_runtime)}. Live CSI capture: {String(data?.csi_live_capture)}.
      </p>
    </div>
  );
}

export function ReplayPage() {
  const [out, setOut] = useState<Record<string, unknown> | null>(null);
  const [missing, setMissing] = useState(false);
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const id = (event.currentTarget.elements.namedItem("run_id") as HTMLInputElement).value;
    const data = await api<Record<string, unknown>>(`/api/replay?id=${encodeURIComponent(id)}`);
    if (!data.found) {
      setMissing(true);
      setOut(null);
      return;
    }
    setMissing(false);
    setOut(data);
  }
  return (
    <div className="workspace">
      <Heading title="Replay" lead="Inspect a local run manifest. No network." />
      <form onSubmit={onSubmit}>
        <label>
          <span>Run id</span>
          <input id="run-id" name="run_id" />
        </label>
        <button className="primary" type="submit">
          Look up local manifest
        </button>
      </form>
      {missing ? (
        <Empty
          title="No local manifest"
          body="That run id is not on this machine. Nothing was fetched from a network."
        />
      ) : null}
      {out ? (
        <>
          <h2>Manifest</h2>
          <pre className="code">{JSON.stringify(out, null, 2)}</pre>
        </>
      ) : null}
    </div>
  );
}
