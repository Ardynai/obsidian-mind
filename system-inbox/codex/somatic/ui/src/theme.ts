export type ThemeName = "light" | "dark";

export function setTheme(theme: ThemeName): void {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("somatic-theme", theme);
  } catch {
    /* localStorage may be unavailable */
  }
  const toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.textContent = theme === "dark" ? "Use light theme" : "Use dark theme";
    toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
  }
}

export function initTheme(): ThemeName {
  const requested = new URLSearchParams(location.search).get("theme");
  if (requested === "dark" || requested === "light") {
    setTheme(requested);
    return requested;
  }
  let stored = "";
  try {
    stored = localStorage.getItem("somatic-theme") || "";
  } catch {
    stored = "";
  }
  if (stored === "dark" || stored === "light") {
    setTheme(stored);
    return stored;
  }
  setTheme("dark");
  return "dark";
}

export function toggleTheme(): ThemeName {
  const next: ThemeName =
    document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  setTheme(next);
  return next;
}
