import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { ApiError, api, type FieldSnapshot, type LiveConsentPayload } from "../api";
import { Blocked } from "../components/States";
import { Heading, Link } from "../components/ui";
import { AudioReadout, OccupancyStrip, FieldReadout, TemplateBodySvg } from "../field/Fallbacks";
import { FieldGui, type FieldGuiState } from "../field/FieldGui";
import { FieldScene } from "../field/FieldScene";
import { AvatarScene } from "../presence/AvatarScene";
import { prefersReducedMotion } from "../motion";
import { granted, useAppStore } from "../store";

const LIVE_MODALITIES = ["csi", "audio", "video", "video3d"] as const;

const LANE_LABELS: Record<string, string> = {
  csi: "CSI · loopback Wi-Fi sensing",
  audio: "Audio · on-device biomarkers",
  video: "Camera pose (RGB)",
  video3d: "Camera pose (depth)",
};

export function LiveLaneAccess({ onError }: { onError: (message: string) => void }) {
  const [consent, setConsent] = useState<LiveConsentPayload | null>(null);
  const [subject, setSubject] = useState<Record<string, boolean>>({});

  const refresh = useCallback(async () => {
    try {
      const data = await api<LiveConsentPayload>("/api/sensors/live-consent");
      setConsent(data);
      const next: Record<string, boolean> = {};
      for (const [name, grant] of Object.entries(data.grants || {})) {
        next[name] = Boolean(grant?.subject_consent);
      }
      setSubject(next);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Request failed");
    }
  }, [onError]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (!consent) return null;
  return (
    <section className="subject-consent">
      <h2>Live lane access</h2>
      <p>{consent.subject_consent_note}</p>
      <p className="muted">
        Every lane starts OFF. Grants are stored locally and revoked with erasure. Raw signals
        never leave this machine: features only.
      </p>
      {LIVE_MODALITIES.filter((name) => consent.grants?.[name]).map((name) => {
        const grant = consent.grants[name];
        return (
          <div className="lane" key={`live-${name}`}>
            <div className="row">
              <h3>{LANE_LABELS[name] || name}</h3>
              <span className={grant.granted ? "pill on" : "pill off"}>
                {grant.granted ? "Live grant ON" : "Live grant OFF"}
              </span>
            </div>
            <label>
              <input
                type="checkbox"
                id={`subject-consent-${name}`}
                name={`subject-consent-${name}`}
                checked={Boolean(subject[name])}
                onChange={(event) =>
                  setSubject((prev) => ({ ...prev, [name]: event.target.checked }))
                }
              />
              <span>
                Subject consent for {name}: I am the only person in the field, or every person
                here consented, and signage is visible.
              </span>
            </label>
            <div className="field-actions">
              <button
                className={grant.granted ? "" : "primary"}
                type="button"
                onClick={async () => {
                  try {
                    await api("/api/sensors/live-consent/grant", {
                      method: "POST",
                      body: JSON.stringify({
                        modality: name,
                        subject_consent: Boolean(subject[name]),
                      }),
                    });
                    await refresh();
                  } catch (err) {
                    onError(err instanceof Error ? err.message : "Request failed");
                  }
                }}
              >
                Grant live {name}
              </button>
              <button
                type="button"
                disabled={!grant.granted}
                onClick={async () => {
                  try {
                    await api("/api/sensors/live-consent/revoke", {
                      method: "POST",
                      body: JSON.stringify({ modality: name }),
                    });
                    await refresh();
                  } catch (err) {
                    onError(err instanceof Error ? err.message : "Request failed");
                  }
                }}
              >
                Revoke live {name}
              </button>
            </div>
          </div>
        );
      })}
      <p className="muted">Grant store: {consent.store}</p>
    </section>
  );
}

export function SensorsPage() {
  const [listing, setListing] = useState<{ lanes: Array<Record<string, unknown>> } | null>(null);
  const [error, setError] = useState("");
  const [snapshot, setSnapshot] = useState<FieldSnapshot | null>(null);
  const [fusion, setFusion] = useState("");
  const [history, setHistory] = useState<number[][]>([]);
  useEffect(() => {
    api<{ lanes: Array<Record<string, unknown>> }>("/api/sensors")
      .then(setListing)
      .catch((err: Error) => setError(err.message));
  }, []);
  return (
    <div className="workspace">
      <Heading
        kicker="Sandbox"
        title="Sensor roster"
        lead="Sandbox features only. Raw frames, audio, CSI, and biosignals are not shown or stored."
      />
      <p className="sandbox-banner">
        <strong>Sandbox · synthetic · not a real person.</strong> Open Field to watch the sandbox
        body and heatmap move. Live lanes (CSI, audio, camera pose) stay off until you grant each
        one.
      </p>
      <p>
        <Link href="/field">Open Field / Body view</Link>
      </p>
      {listing?.lanes.map((lane) => (
        <section className="lane" key={String(lane.modality)}>
          <div className="row">
            <h2>{String(lane.modality)}</h2>
            <span className="pill off">Sandbox</span>
            <span className="pill">{lane.live_granted ? "Live grant ON" : "Live grant OFF"}</span>
          </div>
          <p>{String(lane.notes || "")}</p>
          <p className="muted">Go live: {String(lane.go_live || "")}</p>
        </section>
      ))}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      <LiveLaneAccess onError={setError} />
      {!granted("data-ingestion") || !granted("analysis-insight") ? (
        <Blocked
          scopeId={granted("data-ingestion") ? "analysis-insight" : "data-ingestion"}
          label={granted("data-ingestion") ? "analysis insight" : "data ingestion"}
        />
      ) : (
        <>
          {listing?.lanes.map((lane) => (
            <button
              key={`scan-${String(lane.modality)}`}
              type="button"
              onClick={async () => {
                setError("");
                try {
                  const data = await api<FieldSnapshot>("/api/sensors/field", {
                    method: "POST",
                    body: JSON.stringify({
                      modality: lane.modality,
                      tick: Date.now() % 10000,
                      live: false,
                    }),
                  });
                  const row = data.occupancy_row || data.envelope || [];
                  setHistory(row.length ? [row] : []);
                  setSnapshot(data);
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Request failed");
                }
              }}
            >
              Sandbox scan {String(lane.modality)}
            </button>
          ))}
          <button
            type="button"
            onClick={async () => {
              const data = await api<Record<string, unknown>>("/api/sensors/fuse", {
                method: "POST",
                body: "{}",
              });
              setFusion(JSON.stringify(data.fusion, null, 2));
            }}
          >
            Sandbox RF-vision fusion
          </button>
        </>
      )}
      {snapshot ? (
        <>
          <h2>{snapshot.disclaimer}</h2>
          <p className="sandbox-banner">{snapshot.disclaimer}</p>
          <FieldScene snapshot={snapshot} />
          {snapshot ? (
            <TemplateBodySvg
              joints={snapshot.pose3d.joints}
              live={snapshot.show_skeleton === false}
            />
          ) : (
            <TemplateBodySvg joints={[]} />
          )}
          <OccupancyStrip history={history} />
          <FieldReadout snapshot={snapshot as unknown as Record<string, unknown>} />
          <pre className="code">
            {JSON.stringify(
              {
                breathing_rate_per_min: snapshot.breathing_rate_per_min,
                motion_energy: snapshot.motion_energy,
                presence: snapshot.presence,
                joints: snapshot.pose3d.joints,
              },
              null,
              2,
            )}
          </pre>
        </>
      ) : null}
      {fusion ? <pre className="code">{fusion}</pre> : null}
    </div>
  );
}

export function FieldPage() {
  const [error, setError] = useState("");
  const [snapshot, setSnapshot] = useState<FieldSnapshot | null>(null);
  const [modality, setModality] = useState<string>("csi");
  const modalityRef = useRef("csi");
  const [liveConsent, setLiveConsent] = useState<LiveConsentPayload | null>(null);
  const [subject, setSubject] = useState(false);
  const [liveGrant, setLiveGrant] = useState(false);
  const liveMode = useRef(false);
  const tick = useRef(0);
  const [history, setHistory] = useState<number[][]>([]);
  const [gui, setGui] = useState<FieldGuiState>({
    autoRotate: true,
    bloom: true,
    occupancyScale: 1,
    showGrid: true,
  });
  const timer = useRef<number | null>(null);

  const stopTimer = () => {
    if (timer.current !== null) {
      window.clearInterval(timer.current);
      timer.current = null;
    }
  };

  const pull = useCallback(async () => {
    setError("");
    const data = await api<FieldSnapshot>("/api/sensors/field", {
      method: "POST",
      body: JSON.stringify({
        modality: modalityRef.current,
        tick: tick.current,
        live: liveMode.current,
      }),
    });
    const row = data.occupancy_row || data.envelope || [];
    if (row.length) {
      setHistory((prev) => [...prev, row].slice(-48));
    }
    setSnapshot(data);
    tick.current += 1;
  }, []);

  useEffect(() => {
    api<LiveConsentPayload>("/api/sensors/live-consent")
      .then((data) => {
        setLiveConsent(data);
        setLiveGrant(Boolean(data.grants?.["csi"]?.granted));
        setSubject(Boolean(data.grants?.["csi"]?.subject_consent));
      })
      .catch((err: Error) => setError(err.message));
    if (new URLSearchParams(location.search).get("preview") === "1") {
      pull().catch((err: Error) => setError(err.message));
    }
    return () => stopTimer();
  }, [pull]);

  const chooseModality = (next: string) => {
    stopTimer();
    liveMode.current = false;
    modalityRef.current = next;
    setModality(next);
    setHistory([]);
    setSnapshot(null);
  };

  const startStream = (live: boolean) => {
    stopTimer();
    liveMode.current = live;
    setHistory([]);
    const run = () =>
      pull().catch((err: Error) => {
        setError(err.message);
        stopTimer();
      });
    void run();
    if (prefersReducedMotion()) return;
    timer.current = window.setInterval(run, 450);
  };

  if (!granted("data-ingestion") || !granted("analysis-insight")) {
    return (
      <div className="workspace">
        <Heading title="Field" lead="Watch sandbox pose and occupancy before any hardware is plugged in." />
        <Blocked
          scopeId={granted("data-ingestion") ? "analysis-insight" : "data-ingestion"}
          label={granted("data-ingestion") ? "analysis insight" : "data ingestion"}
        />
      </div>
    );
  }

  return (
    <div className="workspace">
      <Heading
        kicker="Sandbox"
        title="Field"
        lead="Sandbox pose and occupancy first. The same view can show loopback CSI, on-device audio biomarkers, or camera pose when you grant each live lane."
      />
      <p className="sandbox-banner">
        <strong>{snapshot?.disclaimer || "Sandbox · synthetic · not a real person."}</strong>
      </p>
      <div className="field-actions">
        <label>
          <span className="sr-only">Field modality</span>
          <select
            id="field-modality"
            name="field-modality"
            value={modality}
            onChange={(event) => chooseModality(event.target.value)}
          >
            <option value="csi">CSI (Wi-Fi sensing)</option>
            <option value="audio">Audio (biomarkers)</option>
            <option value="video">Camera pose (RGB)</option>
            <option value="video3d">Camera pose (depth)</option>
          </select>
        </label>
        <button
          className="primary"
          type="button"
          onClick={() => startStream(false)}
        >
          Watch sandbox field
        </button>
        <button
          type="button"
          onClick={() => {
            pull().catch((err: Error) => setError(err.message));
          }}
        >
          Advance one tick
        </button>
      </div>
      <div className="field-grid">
        <section className="field-panel">
          <h2>Body</h2>
          <FieldScene snapshot={snapshot} gui={gui} />
          <p className="muted">{snapshot?.pose3d.note || "Synthetic template body from head and torso joints."}</p>
        </section>
        <section className="field-panel">
          <h2>{modality === "audio" ? "Audio biomarkers" : "Occupancy"}</h2>
          <OccupancyStrip history={history} />
          {snapshot ? <FieldReadout snapshot={snapshot as unknown as Record<string, unknown>} /> : null}
          {modality === "audio" && snapshot ? (
            <AudioReadout
              breathing={snapshot.breathing_rate_per_min}
              coughs={snapshot.cough_event_count}
              speechActivity={snapshot.speech_activity_ratio}
            />
          ) : null}
          <FieldGui onChange={setGui} />
        </section>
      </div>
      <p className="muted">
        Tick {snapshot?.tick ?? 0} · {snapshot?.hardware_validation || "sandbox-verified; needs a real ESP32 to validate live"}
      </p>
      <p className="sr-only" aria-live="polite">
        {snapshot
          ? `${snapshot.disclaimer} Breathing ${snapshot.breathing_rate_per_min ?? 0} per minute. Motion ${snapshot.motion_energy ?? 0}. Presence ${snapshot.presence ? "yes" : "no"}.`
          : ""}
      </p>
      <section className="subject-consent">
        <h2>Live {modality} lane</h2>
        <p>{liveConsent?.subject_consent_note || ""}</p>
        <p className="muted">
          On-device and features only: raw audio, raw frames, and raw CSI never leave this
          machine. The grant stays off until you give it, per modality.
        </p>
        <label>
          <input
            type="checkbox"
            id="subject-consent"
            name="subject-consent"
            checked={subject}
            onChange={(event) => setSubject(event.target.checked)}
          />
          <span>
            Subject consent for {modality}: I am the only person in the field, or every person
            here consented, and signage is visible.
          </span>
        </label>
        <label>
          <input
            type="checkbox"
            id={`live-${modality}`}
            name={`live-${modality}`}
            checked={liveGrant && modality === "csi"}
            disabled
          />
          <span>
            Live {modality} grant is a separate switch. It stays off until you grant it.
          </span>
        </label>
        <div className="field-actions">
          <button
            type="button"
            onClick={async () => {
              setError("");
              try {
                await api("/api/sensors/live-consent/grant", {
                  method: "POST",
                  body: JSON.stringify({ modality, subject_consent: subject }),
                });
                const data = await api<LiveConsentPayload>("/api/sensors/live-consent");
                setLiveConsent(data);
                setLiveGrant(Boolean(data.grants?.[modality]?.granted));
                setSubject(Boolean(data.grants?.[modality]?.subject_consent));
              } catch (err) {
                setError(err instanceof Error ? err.message : "Request failed");
              }
            }}
          >
            Grant live {modality}
          </button>
          <button
            type="button"
            onClick={async () => {
              await api("/api/sensors/live-consent/revoke", {
                method: "POST",
                body: JSON.stringify({ modality }),
              });
              setLiveGrant(false);
              liveMode.current = false;
              stopTimer();
              const data = await api<LiveConsentPayload>("/api/sensors/live-consent");
              setLiveConsent(data);
              setSubject(Boolean(data.grants?.[modality]?.subject_consent));
            }}
          >
            Revoke live {modality}
          </button>
          <button
            type="button"
            onClick={() => {
              if (!liveConsent?.grants?.[modality]?.granted) {
                setError(
                  `Live ${modality} is off by default; grant live-sensor ${modality} with subject consent first.`,
                );
                return;
              }
              startStream(true);
            }}
          >
            Watch live {modality}
          </button>
        </div>
      </section>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function SciencePage() {
  const [error, setError] = useState("");
  const [out, setOut] = useState<Record<string, unknown> | null>(null);
  if (!granted("autonomous-research") || !granted("analysis-insight")) {
    return (
      <div className="workspace">
        <Heading
          title="Science harness"
          lead="Sandbox tournament, belief ledger, and falsifier. Read-only results."
        />
        <Blocked
          scopeId={granted("autonomous-research") ? "analysis-insight" : "autonomous-research"}
        />
      </div>
    );
  }
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    try {
      const data = await api<Record<string, unknown>>("/api/science", {
        method: "POST",
        body: JSON.stringify({
          goal: (event.currentTarget.elements.namedItem("goal") as HTMLTextAreaElement).value,
        }),
      });
      const report = data.report as { blocked?: string; summary?: string };
      if (report?.blocked) {
        useAppStore.getState().setAlert({ text: String(report.summary || ""), kind: String(report.blocked) });
      }
      setOut(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    }
  }
  return (
    <div className="workspace">
      <Heading title="Science harness" lead="Sandbox only. Biosecurity refusals stay in place. No lab spend." />
      <form onSubmit={onSubmit}>
        <label>
          <span>Research goal</span>
          <textarea id="goal" name="goal" />
        </label>
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button className="primary" type="submit">
          Run sandbox cycle
        </button>
      </form>
      {out ? (
        <>
          <h2>Sandbox results (read-only)</h2>
          <p>{String((out.report as { summary?: string })?.summary || "")}</p>
          <p>Ranked: {String((out.report as { ranked_hypothesis_id?: string })?.ranked_hypothesis_id || "(none)")}</p>
          <pre className="code">{JSON.stringify((out.report as { belief?: unknown })?.belief, null, 2)}</pre>
        </>
      ) : (
        <p className="muted">Sandbox results appear here. Nothing leaves this machine.</p>
      )}
    </div>
  );
}

export function PresencePage() {
  const [speech, setSpeech] = useState("");
  const [persona, setPersona] = useState("doctor");
  const [meta, setMeta] = useState("");
  if (!granted("ai-advisory")) {
    return (
      <div className="workspace">
        <Heading title="Presence" lead="Render-only restatement. Never part of the reasoning path." />
        <Blocked scopeId="ai-advisory" label="AI advisory" />
      </div>
    );
  }
  return (
    <div className="workspace">
      <Heading title="Presence" lead="Scientist and doctor voices restate a gated verdict. They do not reason." />
      <div className="field-grid">
        <AvatarScene persona={persona} speech={speech} />
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const nextPersona = (form.elements.namedItem("persona") as HTMLSelectElement).value;
            const data = await api<Record<string, unknown>>("/api/avatar", {
              method: "POST",
              body: JSON.stringify({
                verdict: (form.elements.namedItem("verdict") as HTMLTextAreaElement).value,
                persona: nextPersona,
              }),
            });
            setPersona(nextPersona);
            setSpeech(String(data.speech || ""));
            setMeta(
              `Render-only: ${data.render_only}. TTS: ${data.tts_runtime}. Talking head: ${data.talking_head_runtime}.`,
            );
          }}
        >
          <label>
            <span>Gated verdict to rephrase</span>
            <textarea id="verdict" name="verdict" />
          </label>
          <label>
            <span>Persona</span>
            <select id="persona" name="persona" defaultValue="doctor">
              <option value="doctor">doctor</option>
              <option value="scientist">scientist</option>
            </select>
          </label>
          <button className="primary" type="submit">
            Render presence
          </button>
        </form>
      </div>
      {speech ? <p>{speech}</p> : <p className="muted">A restated verdict will appear here. Presence does not reason.</p>}
      {meta ? <p className="muted">{meta}</p> : null}
      <p className="muted">Audio stays off. Talking-head runtimes are founder-gated and not shipped here.</p>
    </div>
  );
}

export function BenchPage() {
  const [error, setError] = useState("");
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  if (!granted("autonomous-research") || !granted("analysis-insight")) {
    return (
      <div className="workspace">
        <Heading title="Science bench" lead="Sandbox scoring only. No lab spend." />
        <Blocked
          scopeId={granted("autonomous-research") ? "analysis-insight" : "autonomous-research"}
        />
      </div>
    );
  }
  return (
    <div className="workspace">
      <Heading title="Science bench" lead="Read-only sandbox scoring. Dollars spent stay at zero." />
      <button
        className="primary"
        type="button"
        onClick={async () => {
          setError("");
          try {
            setData(await api<Record<string, unknown>>("/api/bench", { method: "POST", body: "{}" }));
          } catch (err) {
            setError(err instanceof Error ? err.message : "Request failed");
          }
        }}
      >
        Run sandbox bench
      </button>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {data ? (
        <>
          <h2>Sandbox score</h2>
          <p>Task: {String(data.task_id)}</p>
          <p>Passed: {String(data.passed)}</p>
          <p>Blocked: {String(data.blocked || "no")}</p>
          <ul>
            {((data.notes as string[]) || []).map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </>
      ) : null}
    </div>
  );
}

export function SuggestionsPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [blocked, setBlocked] = useState("");
  useEffect(() => {
    if (!granted("proactive-suggestions")) return;
    api<Record<string, unknown>>("/api/suggestions")
      .then(setData)
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.payload.scope_id) {
          setBlocked(String(err.payload.scope_id));
        }
      });
  }, []);
  if (!granted("proactive-suggestions")) {
    return (
      <div className="workspace">
        <Heading
          title="Proactive suggestions"
          lead="This scope stays OFF until you grant it. Somatic does not currently send unsolicited suggestions."
        />
        <Blocked scopeId="proactive-suggestions" label="proactive suggestions" />
      </div>
    );
  }
  if (blocked) {
    return (
      <div className="workspace">
        <Heading title="Proactive suggestions" lead="Grant this scope to inspect the reserved surface." />
        <Blocked scopeId={blocked} />
      </div>
    );
  }
  return (
    <div className="workspace">
      <Heading title="Proactive suggestions" lead={String(data?.message || "")} />
      <p role="status">
        {data?.implemented ? "Suggestions are available." : "No unsolicited suggestions. This surface is reserved."}
      </p>
    </div>
  );
}

