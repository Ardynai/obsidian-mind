import { useAppStore } from "../store";

export function TopStatus() {
  const status = useAppStore((s) => s.status);
  const path = useAppStore((s) => s.path);
  const grantedCount = (status?.scopes || []).filter((row) => row.granted).length;
  const total = (status?.scopes || []).length || 7;
  return (
    <>
      <span className={status?.all_scopes_off ? "pill off" : "pill on"}>
        <span className="g live-pulse" />
        {status?.all_scopes_off ? "All scopes OFF" : `${grantedCount}/${total} granted`}
      </span>
      <span className="pill">{status?.ok ? "Emergency screen OK" : "Emergency screen failed"}</span>
      <span className="pill">{path}</span>
    </>
  );
}
