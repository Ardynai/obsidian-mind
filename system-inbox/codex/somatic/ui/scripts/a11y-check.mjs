/**
 * WCAG 2.1 AA audit of the shipped SPA shell plus representative DOM states.
 * Authoring-time only (Node). Production users do not need this.
 *
 * jsdom cannot compute layout contrast, so color-contrast is still skipped
 * in axe. Token pairs in ui/contrast-tokens.json are checked here with
 * relative-luminance math (WCAG 2.1). That is the contrast gate.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";
import axeCore from "axe-core";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../..");
const staticDir = path.join(repo, "somatic/bridge/static");
const fixturePath = path.join(here, "../a11y/fixture.html");
const tokenPath = path.join(here, "../contrast-tokens.json");

function channel(value) {
  const n = value / 255;
  return n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
}

function luminance(hex) {
  const raw = hex.replace("#", "");
  const r = Number.parseInt(raw.slice(0, 2), 16);
  const g = Number.parseInt(raw.slice(2, 4), 16);
  const b = Number.parseInt(raw.slice(4, 6), 16);
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function contrastRatio(fg, bg) {
  const a = luminance(fg);
  const b = luminance(bg);
  const hi = Math.max(a, b);
  const lo = Math.min(a, b);
  return (hi + 0.05) / (lo + 0.05);
}

const tokens = JSON.parse(fs.readFileSync(tokenPath, "utf8"));
const contrastFails = [];
for (const pair of tokens.pairs) {
  const ratio = contrastRatio(pair.fg, pair.bg);
  if (ratio + 1e-6 < pair.min) {
    contrastFails.push(
      `${pair.id}: ${ratio.toFixed(2)}:1 < ${pair.min}:1 (${pair.fg} on ${pair.bg})`
    );
  }
}
if (contrastFails.length) {
  console.error("token contrast failures:\n" + contrastFails.join("\n"));
  process.exit(1);
}

const css = fs.readFileSync(path.join(staticDir, "styles.css"), "utf8");
if (!css.includes("IBM Plex Sans") || !css.includes("@font-face")) {
  console.error("styles.css must self-host IBM Plex Sans via @font-face");
  process.exit(1);
}
if (!css.includes("Space Grotesk") || !css.includes("IBM Plex Mono")) {
  console.error("styles.css must self-host Space Grotesk and IBM Plex Mono");
  process.exit(1);
}
if (!css.includes("prefers-reduced-motion")) {
  console.error("styles.css must gate motion on prefers-reduced-motion");
  process.exit(1);
}

const shell = fs.readFileSync(path.join(staticDir, "index.html"), "utf8");
const sampleMain = fs.readFileSync(fixturePath, "utf8");

const html = shell
  .replace(
    '<link rel="stylesheet" href="/styles.css" />',
    `<style>${css}</style>`
  )
  .replace('<main id="main" tabindex="-1"></main>', `<main id="main" tabindex="-1">${sampleMain}</main>`)
  .replace('<script src="/app.js" defer></script>', "");

const dom = new JSDOM(html, {
  url: "http://127.0.0.1:8765/",
  pretendToBeVisual: true,
  runScripts: "outside-only",
});

dom.window.eval(axeCore.source);
const results = await dom.window.axe.run(dom.window.document, {
  runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] },
  rules: {
    "color-contrast": { enabled: false },
    "color-contrast-enhanced": { enabled: false },
  },
});

if (results.violations.length) {
  console.error(JSON.stringify(results.violations, null, 2));
  process.exit(1);
}
console.log(
  `axe: 0 violations, ${results.passes.length} passes; token contrast ${tokens.pairs.length} pairs OK`
);
process.exit(0);
