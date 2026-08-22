import { create } from "zustand";
import type { ConsentPayload, StatusPayload } from "./api";

export type InspectorFact = { label: string; value: string };

type AppState = {
  path: string;
  meta: Record<string, unknown> | null;
  status: StatusPayload | null;
  consent: ConsentPayload | null;
  notice: string;
  alert: { text: string; kind?: string } | null;
  paletteOpen: boolean;
  shortcutsOpen: boolean;
  inspector: { title: string; facts: InspectorFact[]; notes: string[] };
  setPath: (path: string) => void;
  setBootstrap: (payload: {
    meta: Record<string, unknown>;
    status: StatusPayload;
    consent: ConsentPayload;
  }) => void;
  setConsent: (consent: ConsentPayload) => void;
  setNotice: (notice: string) => void;
  setAlert: (alert: { text: string; kind?: string } | null) => void;
  setPaletteOpen: (open: boolean) => void;
  setShortcutsOpen: (open: boolean) => void;
  setInspector: (inspector: AppState["inspector"]) => void;
};

export const useAppStore = create<AppState>((set) => ({
  path: "/",
  meta: null,
  status: null,
  consent: null,
  notice: "",
  alert: null,
  paletteOpen: false,
  shortcutsOpen: false,
  inspector: {
    title: "Inspector",
    facts: [],
    notes: ["Counts update as you move between surfaces."],
  },
  setPath: (path) => set({ path }),
  setBootstrap: ({ meta, status, consent }) => set({ meta, status, consent }),
  setConsent: (consent) => set({ consent }),
  setNotice: (notice) => set({ notice }),
  setAlert: (alert) => set({ alert }),
  setPaletteOpen: (paletteOpen) => set({ paletteOpen }),
  setShortcutsOpen: (shortcutsOpen) => set({ shortcutsOpen }),
  setInspector: (inspector) => set({ inspector }),
}));

export function granted(scopeId: string): boolean {
  const consent = useAppStore.getState().consent;
  return Boolean((consent?.scopes || []).find((row) => row.id === scopeId && row.granted));
}

export function scopeLabel(scopeId: string): string {
  const consent = useAppStore.getState().consent;
  return consent?.scopes.find((row) => row.id === scopeId)?.human_label || scopeId;
}
