export function currentPath(): string {
  return location.pathname.replace(/\/$/, "") || "/";
}

export function navigate(href: string): void {
  const url = new URL(href, location.href);
  if (url.origin !== location.origin) return;
  history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
  window.dispatchEvent(new Event("somatic:navigate"));
}

export const ROUTES: Array<{
  path: string;
  title: string;
  group: string;
  hint: string;
}> = [
  { path: "/", title: "Status", group: "Home", hint: "G" },
  { path: "/consent", title: "Consent", group: "Home", hint: "C" },
  { path: "/privacy", title: "Privacy", group: "Home", hint: "E" },
  { path: "/ingest", title: "Ingest", group: "Your data", hint: "I" },
  { path: "/analyze", title: "Analyze", group: "Your data", hint: "A" },
  { path: "/share", title: "Share", group: "Your data", hint: "S" },
  { path: "/experiments", title: "Experiments", group: "Your data", hint: "X" },
  { path: "/research", title: "Research", group: "Library", hint: "R" },
  { path: "/remedy", title: "Remedy", group: "Library", hint: "M" },
  { path: "/parasite", title: "Parasite Q&A", group: "Library", hint: "P" },
  { path: "/sensors", title: "Sensors", group: "Sandbox", hint: "N" },
  { path: "/field", title: "Field", group: "Sandbox", hint: "F" },
  { path: "/science", title: "Science", group: "Sandbox", hint: "H" },
  { path: "/presence", title: "Presence", group: "Sandbox", hint: "V" },
  { path: "/bench", title: "Bench", group: "Sandbox", hint: "B" },
  { path: "/suggestions", title: "Suggestions", group: "Sandbox", hint: "U" },
  { path: "/tools", title: "CLI tools", group: "Machine", hint: "T" },
  { path: "/replay", title: "Replay", group: "Machine", hint: "Y" },
];
