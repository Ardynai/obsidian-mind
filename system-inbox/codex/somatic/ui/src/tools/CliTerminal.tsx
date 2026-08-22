import { useEffect, useRef } from "react";
import { Terminal } from "@xterm/xterm";

export function CliTerminal({ lines }: { lines: string[] }) {
  const host = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);

  useEffect(() => {
    if (!host.current || termRef.current) return;
    const term = new Terminal({
      convertEol: true,
      fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
      fontSize: 13,
      theme: {
        background: "#050d0a",
        foreground: "#EAF5EF",
        cursor: "#35E7A6",
        selectionBackground: "#12A574",
      },
      disableStdin: true,
    });
    term.open(host.current);
    termRef.current = term;
    return () => {
      term.dispose();
      termRef.current = null;
    };
  }, []);

  useEffect(() => {
    const term = termRef.current;
    if (!term) return;
    term.clear();
    term.writeln("somatic@127.0.0.1  CLI companions (read-only replica)");
    term.writeln("Fabric vectors stay in the real terminal. This pane does not spawn processes.");
    term.writeln("");
    for (const line of lines) {
      term.writeln(`$ ${line}`);
    }
    term.writeln("");
    term.writeln("csi_live_capture stays false until hardware + founder-gated model.");
  }, [lines]);

  return (
    <div
      className="term-host"
      ref={host}
      role="region"
      aria-label="Read-only replica of Somatic CLI commands on this machine"
    />
  );
}
