import { Sparkline } from "../viz";
import { useAppStore } from "../store";

export function InspectorPanel() {
  const inspector = useAppStore((s) => s.inspector);
  const status = useAppStore((s) => s.status);
  const path = useAppStore((s) => s.path);
  const grantedCount = (status?.scopes || []).filter((row) => row.granted).length;
  const bits = (status?.scopes || []).map((row) => (row.granted ? 1 : 0.12));
  return (
    <>
      <p className="kicker">Inspector</p>
      <div className="tele">
        <h3>{inspector.title}</h3>
        <div className="kv">
          <span className="k">Route</span>
          <span className="v">{path}</span>
        </div>
        <div className="kv">
          <span className="k">Scopes on</span>
          <span className="v em">
            {grantedCount} / {(status?.scopes || []).length || 7}
          </span>
        </div>
        {inspector.facts.map((fact) => (
          <div className="kv" key={fact.label}>
            <span className="k">{fact.label}</span>
            <span className="v">{fact.value}</span>
          </div>
        ))}
      </div>
      <div className="tele">
        <h3>Live signal</h3>
        <Sparkline
          values={bits.length ? bits : [0.12, 0.12, 0.12]}
          label="Consent scopes this session, on is high, off is low. Not a vital sign."
          color="var(--cyan)"
        />
        <p className="muted" style={{ marginTop: 8 }}>
          Scope grant trace. Features only. Not a vital sign.
        </p>
      </div>
      {inspector.notes.map((note) => (
        <p className="muted" key={note}>
          {note}
        </p>
      ))}
      <p className="muted">
        CSP holds <code>script-src 'self'</code>. Nothing leaves 127.0.0.1.
      </p>
      <p className="emergency-arm">
        <strong>Emergency routing armed.</strong> Red-flag input short-circuits to see a clinician
        now. Coral is used for nothing else.
      </p>
    </>
  );
}
