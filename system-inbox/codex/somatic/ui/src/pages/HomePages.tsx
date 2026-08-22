import { useEffect, useState } from "react";
import { api, type SensorsPayload } from "../api";
import { Meter } from "../components/Meter";
import { Empty } from "../components/States";
import { Heading, pad2 } from "../components/ui";
import { Link } from "../components/ui";
import { CountUp, Sparkline } from "../viz";
import { useAppStore } from "../store";

export function StatusPage() {
  const status = useAppStore((s) => s.status);
  const [sensors, setSensors] = useState<SensorsPayload | null>(null);
  useEffect(() => {
    api<SensorsPayload>("/api/sensors")
      .then(setSensors)
      .catch(() => setSensors(null));
  }, []);
  if (!status) return <Empty title="Bridge quiet" body="Status has not loaded yet." />;
  const grantedCount = status.scopes.filter((row) => row.granted).length;
  const bits = status.scopes.map((row) => (row.granted ? 1 : 0.18));
  const languageScope = String(
    status.emergency_self_test?.language_scope || "english-spanish-french",
  );
  const poseModel = sensors?.pose_model as
    | { enabled?: boolean; founder_gated?: boolean; note?: string }
    | undefined;
  return (
    <div className="workspace">
      <Heading
        kicker="This machine"
        title={status.all_scopes_off ? "All off." : `${grantedCount} granted.`}
        lead="This machine is local. Capabilities stay off until you grant them. An empty, all-off board is expected."
      />
      <div className="kpis">
        <div className="kpi em">
          <div className="lab">Scopes granted</div>
          <div className="val">
            <CountUp value={grantedCount} />
            <small>/7</small>
          </div>
          <Sparkline values={bits} label={`Granted scopes: ${grantedCount} of 7. Default is off.`} />
        </div>
        <div className="kpi">
          <div className="lab">Emergency screen</div>
          <div className="val">{status.ok ? "OK" : "CHECK"}</div>
          <p className="muted" style={{ marginTop: 8 }}>
            {status.ok ? "self-test passed" : "self-test failed"}
          </p>
        </div>
        <div className="kpi cyan">
          <div className="lab">Sensor lanes</div>
          <div className="val">
            <CountUp value={status.sensor_lanes.length} />
          </div>
          <p className="muted" style={{ marginTop: 8 }}>
            sandbox · features only
          </p>
        </div>
        <div className="kpi amber">
          <div className="lab">Loopback</div>
          <div className="val" style={{ fontSize: "1.35rem" }}>
            127.0.0.1
          </div>
          <p className="muted" style={{ marginTop: 8 }}>
            CSP: script-src 'self'
          </p>
        </div>
      </div>
      <div className="cockpit">
        <Meter scopes={status.scopes} />
        <div className="scoperows">
          {status.scopes.map((row, index) => (
            <div className="srow" key={row.id}>
              <span className="n">{pad2(index + 1)}</span>
              <span className="nm">
                {row.human_label}
                <em>{row.granted ? "Granted on this machine" : "Off until you grant it"}</em>
              </span>
              <span
                className={row.granted ? "toggle on" : "toggle"}
                aria-hidden="true"
              />
            </div>
          ))}
        </div>
      </div>
      <p className="stat-row">
        <span className={status.all_scopes_off ? "pill off" : "pill on"}>
          {status.all_scopes_off ? (
            <>
              <span className="g live-pulse" /> All scopes OFF
            </>
          ) : (
            "Some scopes granted"
          )}
        </span>
        <span className="pill">
          {status.ok ? "Emergency screen self-test passed" : "Emergency screen self-test failed"}
        </span>
        <span className="pill">Adapter {status.adapter_config}</span>
        <span className="pill">Emergency lexicons: {languageScope}</span>
        <span className={status.encryption_at_rest ? "pill on" : "pill"}>
          Encryption at rest {status.encryption_at_rest ? "ON" : "OFF (plaintext + 0600)"}
        </span>
        {sensors ? (
          <span className="pill">Live grants {["csi", "audio", "video", "video3d"].filter((m) => sensors.lanes?.find((lane) => lane.modality === m)?.live_granted).length}/4</span>
        ) : null}
      </p>
      {poseModel ? (
        <p className="muted">
          CSI pose model: {poseModel.enabled ? "enabled" : "off"} · founder-gated ·{" "}
          {String(poseModel.note || "")} Camera pose uses on-device MediaPipe instead; raw frames
          are never stored.
        </p>
      ) : null}
      {status.all_scopes_off ? (
        <Empty
          title="Quiet on purpose"
          body="Nothing is granted yet. Open Consent when you want a capability. Until then, analysis, sharing, research, and sensors stay off."
        />
      ) : (
        <p className="success-note" role="status">
          {grantedCount} scope{grantedCount === 1 ? "" : "s"} on. The rest stay off until you say so.
        </p>
      )}
      <p>
        <Link href="/consent">Open the consent protocol</Link>
      </p>
      <div className="sectlabel">Sensor lanes · sandbox</div>
      <div className="lanes">
        {status.sensor_lanes.map((lane) => (
          <section className="lane" key={lane.modality}>
            <h3>{lane.modality}</h3>
            <span className="chip cyan">sandbox</span>
            <span className="chip">needs hw</span>
            <p className="muted">{lane.notes}</p>
          </section>
        ))}
      </div>
      <p>
        <Link href="/field">Open Field / Body</Link>
      </p>
      <p className="muted">{status.notes[0] || ""}</p>
      <p className="muted">{status.notes[1] || ""}</p>
    </div>
  );
}

export function ConsentPage() {
  const data = useAppStore((s) => s.consent);
  const [filter, setFilter] = useState<"all" | "on" | "off">("all");
  if (!data) return <Empty title="Consent ledger loading" body="Waiting on the local ledger." />;
  const scopes =
    filter === "on"
      ? data.scopes.filter((row) => row.granted)
      : filter === "off"
        ? data.scopes.filter((row) => !row.granted)
        : data.scopes;
  return (
    <div className="workspace">
      <Heading
        kicker="Protocol"
        title="Consent"
        lead="Seven capabilities. All start off. Turn on only what you want this machine to do; turn any of them off later."
      />
      <p className="consent-intro">
        Each row is a separate permission. Granting one does not grant the others. The ledger below
        is the local record of those choices.
      </p>
      <div className="filter-bar" role="group" aria-label="Filter scopes">
        {(["all", "on", "off"] as const).map((id) => (
          <button
            key={id}
            type="button"
            aria-pressed={filter === id}
            onClick={() => setFilter(id)}
          >
            {id === "all" ? `All (${data.scopes.length})` : id === "on" ? "ON only" : "OFF only"}
          </button>
        ))}
      </div>
      {scopes.map((row) => (
        <section className="scope" key={row.id}>
          <div className="row">
            <span className="scope-num" aria-hidden="true">
              {pad2(data.scopes.findIndex((item) => item.id === row.id) + 1)}
            </span>
            <h2>{row.human_label}</h2>
            <span className={row.granted ? "pill on" : "pill off"}>{row.granted ? "ON" : "OFF"}</span>
            <span className={row.granted ? "toggle on" : "toggle"} aria-hidden="true" />
          </div>
          <p>{row.description}</p>
          <p className="muted">{row.limits}</p>
          <button
            className={row.granted ? "" : "primary"}
            type="button"
            aria-pressed={row.granted}
            onClick={async () => {
              await api(row.granted ? "/api/consent/revoke" : "/api/consent/grant", {
                method: "POST",
                body: JSON.stringify({ scopes: [row.id] }),
              });
              window.dispatchEvent(new Event("somatic:refresh"));
            }}
          >
            {row.granted ? `Turn off ${row.human_label}` : `Turn on ${row.human_label}`}
          </button>
        </section>
      ))}
      <h2>Ledger</h2>
      {!data.events.length ? (
        <Empty title="No events yet" body="Grants and revokes will list here after you change a scope." />
      ) : (
        <ol>
          {data.events.map((event, i) => (
            <li key={`${event.timestamp}-${i}`}>
              {event.timestamp} {event.action} {event.scope_id}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export function PrivacyPage() {
  const [message, setMessage] = useState("");
  const [store, setStore] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api<Record<string, unknown>>("/api/privacy")
      .then(setStore)
      .catch((err: Error) => setError(err.message));
  }, []);
  return (
    <div className="workspace">
      <Heading
        kicker="Your store"
        title="Privacy and erasure"
        lead="This machine stores a consent ledger, optional readings, and optional experiment tags. Nothing is uploaded."
      />
      <p className="privacy-reassure">
        Erasure deletes those local files together. It cannot be undone. Stored CSI is derived
        features only.
      </p>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {store ? (
        <ul className="store-list">
          <li>Consent file: {String(store.consent_store)}</li>
          <li>
            Readings: {String(store.reading_count)} ({String(store.readings_store)})
          </li>
          <li>Experiment tags: {String(store.tag_count)}</li>
          <li>{String(store.sensor_capture_note)}</li>
          <li>
            Encryption at rest:{" "}
            <strong>{store.encryption_at_rest ? "ON" : "OFF"}</strong>{" "}
            {typeof store.encryption_flag === "string"
              ? `(opt in with ${String(store.encryption_flag)}=1)`
              : ""}
          </li>
          <li className="muted">{String(store.encryption_note || "")}</li>
        </ul>
      ) : (
        <Empty title="Reading local stores" body="Paths appear once the privacy endpoint answers." />
      )}
      <button
        className="erase"
        type="button"
        onClick={async () => {
          const confirmed = window.confirm(
            "Erase consent, readings, and experiment tags on this machine? This cannot be undone.",
          );
          if (!confirmed) return;
          const result = await api<{ message: string }>("/api/privacy/erase", {
            method: "POST",
            body: "{}",
          });
          setMessage(result.message);
          window.dispatchEvent(new Event("somatic:refresh"));
        }}
      >
        Erase everything stored about me
      </button>
      {message ? (
        <p className="success-note" role="status">
          {message}
        </p>
      ) : null}
    </div>
  );
}
