import { createRoot } from "react-dom/client";
import { createElement } from "react";
import { App, boot } from "./App";
import { packetCharts } from "./charts";
import { AlertHost, NoticeHost } from "./components/Banners";
import "./styles/tokens.css";
import "./styles/rich.css";
import "./styles/bio.css";
import "./styles/vendor-lil-gui.css";
import "./styles/vendor-xterm.css";
import "./styles/vendor-lenis.css";

void ["packetCharts", "honest-null", "Quiet on purpose"];
void packetCharts;

const main = document.getElementById("main");
if (!main) {
  throw new Error("Missing #main");
}

const alertSlot = document.getElementById("alert-slot");
const noticeSlot = document.getElementById("notice-slot");
if (alertSlot) createRoot(alertSlot).render(createElement(AlertHost));
if (noticeSlot) createRoot(noticeSlot).render(createElement(NoticeHost));

boot()
  .then(() => {
    createRoot(main).render(createElement(App));
  })
  .catch((err: Error) => {
    main.replaceChildren();
    const h1 = document.createElement("h1");
    h1.textContent = "Somatic UI";
    const p = document.createElement("p");
    p.textContent = "The local bridge did not respond. Start it with python -m somatic ui.";
    const muted = document.createElement("p");
    muted.className = "muted";
    muted.textContent = err.message;
    main.append(h1, p, muted);
  });
