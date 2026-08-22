import { createRoot, type Root } from "react-dom/client";
import { useAppStore } from "../store";
import { InspectorPanel } from "./InspectorPanel";
import { TopStatus } from "./TopStatus";
import { CommandPalette, ShortcutsPanel } from "./CommandPalette";

let inspectorRoot: Root | null = null;
let overlayRoot: Root | null = null;
let statusRoot: Root | null = null;

function OverlayTree() {
  return (
    <>
      <CommandPalette />
      <ShortcutsPanel />
    </>
  );
}

export function mountChrome(): void {
  const context = document.getElementById("context");
  const overlay = document.getElementById("overlay-root");
  const status = document.getElementById("top-status");
  if (context && !inspectorRoot) {
    inspectorRoot = createRoot(context);
    inspectorRoot.render(<InspectorPanel />);
  }
  if (overlay && !overlayRoot) {
    overlayRoot = createRoot(overlay);
    overlayRoot.render(<OverlayTree />);
  }
  if (status && !statusRoot) {
    statusRoot = createRoot(status);
    statusRoot.render(<TopStatus />);
  }
}

export { useAppStore };
