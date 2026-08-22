import { useEffect, useRef, type JSX } from "react";
import { api, type ConsentPayload, type StatusPayload } from "./api";
import { mountChrome } from "./components/chrome";
import { Skeleton } from "./components/States";
import { revealMain, startLenis } from "./motion";
import { AnalyzePage, ExperimentsPage, IngestPage, SharePage } from "./pages/DataPages";
import { ConsentPage, PrivacyPage, StatusPage } from "./pages/HomePages";
import { ParasitePage, RemedyPage, ResearchPage } from "./pages/LibraryPages";
import { ReplayPage, ToolsPage } from "./pages/MachinePages";
import {
  BenchPage,
  FieldPage,
  PresencePage,
  SciencePage,
  SensorsPage,
  SuggestionsPage,
} from "./pages/SandboxPages";
import { currentPath, navigate, ROUTES } from "./routes";
import { granted, useAppStore } from "./store";
import { initTheme, toggleTheme } from "./theme";

const pages: Record<string, () => JSX.Element> = {
  "/": StatusPage,
  "/consent": ConsentPage,
  "/privacy": PrivacyPage,
  "/ingest": IngestPage,
  "/analyze": AnalyzePage,
  "/share": SharePage,
  "/experiments": ExperimentsPage,
  "/research": ResearchPage,
  "/remedy": RemedyPage,
  "/parasite": ParasitePage,
  "/sensors": SensorsPage,
  "/field": FieldPage,
  "/science": SciencePage,
  "/presence": PresencePage,
  "/bench": BenchPage,
  "/suggestions": SuggestionsPage,
  "/tools": ToolsPage,
  "/replay": ReplayPage,
};

function markNav(path: string) {
  document.querySelectorAll<HTMLAnchorElement>(".nav a").forEach((link) => {
    const href = new URL(link.getAttribute("href") || "/", location.href).pathname.replace(/\/$/, "") || "/";
    if (href === path) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

function inspectorFor(path: string) {
  const status = useAppStore.getState().status;
  const grantedCount = (status?.scopes || []).filter((row) => row.granted).length;
  const title = ROUTES.find((row) => row.path === path)?.title || "Status";
  return {
    title,
    facts: [
      { label: "Surface", value: title },
      { label: "Granted", value: `${grantedCount} / ${(status?.scopes || []).length || 7}` },
      { label: "Adapter", value: String(status?.adapter_config || "local") },
      { label: "Loopback", value: "127.0.0.1" },
      { label: "3D Field", value: path === "/field" ? "R3F sandbox template" : "idle" },
    ],
    notes: [
      path === "/field"
        ? "Live CSI occupancy is features only. Skeleton hides when live."
        : "Use Ctrl+K to jump. Filters and inspectors stay on the right rail.",
      granted("data-ingestion") ? "Ingestion is on." : "Ingestion stays off until you grant it.",
    ],
  };
}

export function App() {
  const path = useAppStore((s) => s.path);
  const status = useAppStore((s) => s.status);
  const mainRef = useRef<HTMLDivElement>(null);
  const Page = pages[path] || StatusPage;

  useEffect(() => {
    markNav(path);
    const title = ROUTES.find((row) => row.path === path)?.title || "Status";
    document.title = `Somatic - ${title}`;
    useAppStore.getState().setInspector(inspectorFor(path));
    useAppStore.getState().setAlert(null);
    revealMain(mainRef.current);
  }, [path, status]);

  if (!status) {
    return <Skeleton />;
  }

  return (
    <div ref={mainRef} className="workspace" data-surface={path}>
      <Page />
    </div>
  );
}

export async function boot(): Promise<void> {
  initTheme();
  mountChrome();
  const stopLenis = startLenis();
  const refresh = async () => {
    const [meta, status, consent] = await Promise.all([
      api<Record<string, unknown>>("/api/meta"),
      api<StatusPayload>("/api/status"),
      api<ConsentPayload>("/api/consent"),
    ]);
    useAppStore.getState().setBootstrap({ meta, status, consent });
  };
  await refresh();
  useAppStore.getState().setPath(currentPath());
  const bootParams = new URLSearchParams(location.search);
  if (bootParams.get("palette") === "1") {
    useAppStore.getState().setPaletteOpen(true);
  }
  if (bootParams.get("shortcuts") === "1") {
    useAppStore.getState().setShortcutsOpen(true);
  }

  const go = () => useAppStore.getState().setPath(currentPath());
  window.addEventListener("popstate", go);
  window.addEventListener("somatic:navigate", go);
  window.addEventListener("somatic:refresh", () => {
    refresh().then(go);
  });

  document.body.addEventListener("click", (event) => {
    const link = (event.target as HTMLElement | null)?.closest("a");
    if (!link || link.target === "_blank" || link.hasAttribute("download")) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin) return;
    if (!url.pathname.startsWith("/api")) {
      event.preventDefault();
      navigate(`${url.pathname}${url.search}`);
    }
  });

  document.getElementById("theme-toggle")?.addEventListener("click", () => toggleTheme());
  document.getElementById("command-open")?.addEventListener("click", () => {
    useAppStore.getState().setPaletteOpen(true);
  });
  document.getElementById("shortcuts-open")?.addEventListener("click", () => {
    useAppStore.getState().setShortcutsOpen(true);
  });

  let pendingG = false;
  window.addEventListener("keydown", (event) => {
    const typing = event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement;
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      useAppStore.getState().setPaletteOpen(true);
      return;
    }
    if (event.key === "Escape") {
      useAppStore.getState().setPaletteOpen(false);
      useAppStore.getState().setShortcutsOpen(false);
      return;
    }
    if (typing) return;
    if (event.key === "?") {
      event.preventDefault();
      useAppStore.getState().setShortcutsOpen(true);
      return;
    }
    if (event.key.toLowerCase() === "g") {
      pendingG = true;
      return;
    }
    if (pendingG) {
      pendingG = false;
      const map: Record<string, string> = {
        h: "/",
        c: "/consent",
        e: "/privacy",
        a: "/analyze",
        i: "/ingest",
        f: "/field",
        t: "/tools",
        n: "/sensors",
        v: "/presence",
        r: "/research",
      };
      const dest = map[event.key.toLowerCase()];
      if (dest) navigate(dest);
    }
  });

  window.addEventListener("beforeunload", () => stopLenis());
}
