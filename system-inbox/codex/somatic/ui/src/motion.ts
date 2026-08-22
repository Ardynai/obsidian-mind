import gsap from "gsap";
import Lenis from "lenis";

let lenis: Lenis | null = null;

export function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function startLenis(): () => void {
  if (prefersReducedMotion()) return () => undefined;
  lenis = new Lenis({
    autoRaf: true,
    smoothWheel: true,
  });
  document.documentElement.classList.add("lenis");
  return () => {
    document.documentElement.classList.remove("lenis");
    lenis?.destroy();
    lenis = null;
  };
}

export function revealMain(node: HTMLElement | null): void {
  if (!node || prefersReducedMotion()) return;
  const targets = Array.from(node.children);
  if (!targets.length) return;
  gsap.from(targets, {
    y: 8,
    duration: 0.38,
    stagger: 0.028,
    ease: "power3.out",
    overwrite: "auto",
    immediateRender: false,
  });
}
