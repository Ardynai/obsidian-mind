/**
 * Write the production SPA shell after Vite emits app.js + styles.css.
 * Vite uses a module script for authoring; the bridge tests and a11y gate
 * expect <script src="/app.js" defer> plus the landmark shell.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../..");
const src = path.join(here, "../index.html");
const dest = path.join(repo, "somatic/bridge/static/index.html");
const appJs = path.join(repo, "somatic/bridge/static/app.js");
const css = path.join(repo, "somatic/bridge/static/styles.css");

let html = fs.readFileSync(src, "utf8");
html = html.replace(
  '<script type="module" src="/src/main.tsx"></script>',
  '<script src="/app.js" defer></script>',
);
if (!html.includes('href="#main"') || !html.includes("nav-label")) {
  console.error("write-shell: landmarks missing from ui/index.html");
  process.exit(1);
}
if (html.includes("\u2014")) {
  console.error("write-shell: em dash in index.html");
  process.exit(1);
}
if (!fs.existsSync(appJs) || !fs.existsSync(css)) {
  console.error("write-shell: app.js or styles.css missing after vite build");
  process.exit(1);
}
const js = fs.readFileSync(appJs, "utf8");
for (const needle of ["packetCharts", "honest-null", "Quiet on purpose"]) {
  if (!js.includes(needle)) {
    console.error(`write-shell: ${needle} missing from app.js`);
    process.exit(1);
  }
}
fs.writeFileSync(dest, html);
console.log("wrote somatic/bridge/static/index.html");
