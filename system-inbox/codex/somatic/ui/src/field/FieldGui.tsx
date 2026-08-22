import GUI from "lil-gui";
import { useEffect, useRef } from "react";

export type FieldGuiState = {
  autoRotate: boolean;
  bloom: boolean;
  occupancyScale: number;
  showGrid: boolean;
};

const defaults: FieldGuiState = {
  autoRotate: true,
  bloom: true,
  occupancyScale: 1,
  showGrid: true,
};

export function FieldGui({
  onChange,
}: {
  onChange: (state: FieldGuiState) => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  useEffect(() => {
    if (!host.current) return;
    const state = { ...defaults };
    const gui = new GUI({ container: host.current, title: "Field inspector", injectStyles: false });
    const emit = () => onChangeRef.current({ ...state });
    gui.add(state, "autoRotate").name("Auto rotate").onChange(emit);
    gui.add(state, "bloom").name("Bloom").onChange(emit);
    gui.add(state, "occupancyScale", 0.4, 2.0, 0.05).name("Occupancy scale").onChange(emit);
    gui.add(state, "showGrid").name("Show grid").onChange(emit);
    emit();
    return () => gui.destroy();
  }, []);
  return (
    <div
      className="gui-host"
      ref={host}
      role="group"
      aria-label="Field inspector controls"
    />
  );
}
