import { useEffect, useMemo, useRef, useState } from "react";
import { navigate, ROUTES } from "../routes";
import { toggleTheme } from "../theme";
import { useAppStore } from "../store";

type Item = { id: string; title: string; hint: string; run: () => void; group: string };

export function CommandPalette() {
  const open = useAppStore((s) => s.paletteOpen);
  const setOpen = useAppStore((s) => s.setPaletteOpen);
  const setShortcuts = useAppStore((s) => s.setShortcutsOpen);
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const items = useMemo<Item[]>(() => {
    const nav = ROUTES.map((route) => ({
      id: route.path,
      title: `Open ${route.title}`,
      hint: route.path,
      group: route.group,
      run: () => navigate(route.path),
    }));
    const actions: Item[] = [
      {
        id: "theme",
        title: "Toggle light / dark theme",
        hint: "D",
        group: "Actions",
        run: () => {
          toggleTheme();
        },
      },
      {
        id: "shortcuts",
        title: "Show keyboard shortcuts",
        hint: "?",
        group: "Actions",
        run: () => setShortcuts(true),
      },
      {
        id: "privacy",
        title: "Jump to erasure",
        hint: "/privacy",
        group: "Actions",
        run: () => navigate("/privacy"),
      },
    ];
    const q = query.trim().toLowerCase();
    return [...nav, ...actions].filter(
      (item) =>
        !q ||
        item.title.toLowerCase().includes(q) ||
        item.hint.toLowerCase().includes(q) ||
        item.group.toLowerCase().includes(q),
    );
  }, [query, setShortcuts]);

  useEffect(() => {
    setIndex(0);
  }, [query, open]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
    else setQuery("");
  }, [open]);

  if (!open) return null;
  const current = items[index];

  return (
    <div
      className="palette-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) setOpen(false);
      }}
    >
      <div
        className="palette max-w-xl"
        id="command-palette"
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
      >
        <label>
          <span className="sr-only">Search commands</span>
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Go to a surface, toggle theme, open shortcuts"
            onKeyDown={(event) => {
              if (event.key === "ArrowDown") {
                event.preventDefault();
                setIndex((n) => Math.min(n + 1, Math.max(items.length - 1, 0)));
              } else if (event.key === "ArrowUp") {
                event.preventDefault();
                setIndex((n) => Math.max(n - 1, 0));
              } else if (event.key === "Enter" && current) {
                event.preventDefault();
                current.run();
                setOpen(false);
              } else if (event.key === "Escape") {
                setOpen(false);
              }
            }}
          />
        </label>
        <ul className="palette-list" role="listbox" aria-label="Commands">
          {items.length === 0 ? (
            <li>
              <p className="muted">No matching command.</p>
            </li>
          ) : (
            items.map((item, i) => (
              <li key={item.id} role="presentation">
                <button
                  type="button"
                  role="option"
                  aria-selected={i === index}
                  onMouseEnter={() => setIndex(i)}
                  onClick={() => {
                    item.run();
                    setOpen(false);
                  }}
                >
                  <span>
                    {item.group} / {item.title}
                  </span>
                  <kbd>{item.hint}</kbd>
                </button>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}

export function ShortcutsPanel() {
  const open = useAppStore((s) => s.shortcutsOpen);
  const setOpen = useAppStore((s) => s.setShortcutsOpen);
  if (!open) return null;
  return (
    <div
      className="shortcuts-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) setOpen(false);
      }}
    >
      <div className="shortcuts-panel" role="dialog" aria-modal="true" aria-labelledby="shortcuts-title">
        <h2 id="shortcuts-title">Keyboard</h2>
        <ul>
          <li>
            <kbd>Ctrl</kbd>+<kbd>K</kbd> command palette
          </li>
          <li>
            <kbd>?</kbd> this list
          </li>
          <li>
            <kbd>G</kbd> then a letter jumps: C consent, F field, T tools, P privacy
          </li>
          <li>
            <kbd>Esc</kbd> closes overlays
          </li>
        </ul>
        <button type="button" className="primary" onClick={() => setOpen(false)}>
          Close shortcuts
        </button>
      </div>
    </div>
  );
}
