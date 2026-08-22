import { useAppStore } from "../store";

export function AlertHost() {
  const alert = useAppStore((s) => s.alert);
  if (!alert?.text) return null;
  return (
    <div className="alert" role="alert">
      <strong>{alert.kind === "crisis" ? "Crisis support" : "See a clinician now"}</strong>
      <p>{alert.text}</p>
    </div>
  );
}

export function NoticeHost() {
  const notice = useAppStore((s) => s.notice);
  if (!notice) return null;
  return (
    <div className="notice" role="status">
      {notice}
    </div>
  );
}
