import { Canvas, useFrame } from "@react-three/fiber";
import { ContactShadows, Grid, Html, OrbitControls, Text } from "@react-three/drei";
import { preloadFont } from "troika-three-text";
import { Bloom, EffectComposer } from "@react-three/postprocessing";
import { easing } from "maath";
import { getProject, types } from "@theatre/core";
import { useEffect, useMemo, useRef } from "react";
import type { InstancedMesh, Group } from "three";
import { Color, Object3D } from "three";
import type { FieldSnapshot } from "../api";
import { namedJoints, StagePoster } from "./Fallbacks";
import type { FieldGuiState } from "./FieldGui";
import { prefersReducedMotion } from "../motion";

const defaultGui: FieldGuiState = {
  autoRotate: true,
  bloom: true,
  occupancyScale: 1,
  showGrid: true,
};

void preloadFont;

const project = getProject("somatic-field");
const sheet = project.sheet("sandbox");
const cameraObj = sheet.object("rig", {
  yaw: types.number(0.35, { range: [-1.2, 1.2] }),
});

const dummy = new Object3D();
const moss = new Color("#35E7A6");
const seed = new Color("#4CC4F5");

function toVec(joint: number[]): [number, number, number] {
  const x = (Number(joint[0] || 0.5) - 0.5) * 1.7;
  const y = (0.58 - Number(joint[1] || 0.5)) * 2.35;
  const z = (Number(joint[2] || 0.5) - 0.5) * 0.9;
  return [x, y, z];
}

function templateBody(
  joints: number[][],
  energy: number,
  t: number,
): Record<string, [number, number, number]> {
  const head = toVec(joints[0] || [0.5, 0.12, 0.5]);
  const torso = toVec(joints[1] || [0.5, 0.42, 0.5]);
  const sway = Math.sin(t * 1.4) * Math.min(energy, 1) * 0.08;
  const breath = Math.sin(t * 2.2) * 0.03;
  const hip: [number, number, number] = [torso[0], torso[1] - 0.42, torso[2]];
  const lShoulder: [number, number, number] = [torso[0] - 0.28, torso[1] + 0.22 + breath, torso[2]];
  const rShoulder: [number, number, number] = [torso[0] + 0.28, torso[1] + 0.22 + breath, torso[2]];
  const lHip: [number, number, number] = [hip[0] - 0.14, hip[1], hip[2]];
  const rHip: [number, number, number] = [hip[0] + 0.14, hip[1], hip[2]];
  return {
    head: [head[0] + sway * 0.3, head[1], head[2]],
    neck: [torso[0], torso[1] + 0.38, torso[2]],
    torso: [torso[0], torso[1] + breath, torso[2]],
    lShoulder,
    rShoulder,
    lElbow: [lShoulder[0] - 0.08, lShoulder[1] - 0.32, lShoulder[2] + sway],
    rElbow: [rShoulder[0] + 0.08, rShoulder[1] - 0.32, rShoulder[2] - sway],
    lHand: [lShoulder[0] - 0.04, lShoulder[1] - 0.62, lShoulder[2] + sway * 1.4],
    rHand: [rShoulder[0] + 0.04, rShoulder[1] - 0.62, rShoulder[2] - sway * 1.4],
    hip,
    lHip,
    rHip,
    lKnee: [lHip[0], lHip[1] - 0.42, lHip[2] + 0.04],
    rKnee: [rHip[0], rHip[1] - 0.42, rHip[2] + 0.04],
    lFoot: [lHip[0], lHip[1] - 0.82, lHip[2] + 0.02],
    rFoot: [rHip[0], rHip[1] - 0.82, rHip[2] + 0.02],
  };
}

function Bone({
  a,
  b,
  radius = 0.035,
}: {
  a: [number, number, number];
  b: [number, number, number];
  radius?: number;
}) {
  const mid: [number, number, number] = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
  const dir = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const len = Math.hypot(dir[0], dir[1], dir[2]) || 0.01;
  const rx = Math.atan2(dir[2], dir[1]);
  const rz = Math.atan2(dir[0], Math.hypot(dir[1], dir[2]));
  return (
    <mesh position={mid} rotation={[-rx, 0, rz]}>
      <cylinderGeometry args={[radius, radius, len, 8]} />
      <meshStandardMaterial color={moss} roughness={0.42} metalness={0.08} emissive={moss} emissiveIntensity={0.22} />
    </mesh>
  );
}

function Joint({ p, r = 0.055 }: { p: [number, number, number]; r?: number }) {
  return (
    <mesh position={p}>
      <sphereGeometry args={[r, 16, 16]} />
      <meshStandardMaterial color={"#12A574"} roughness={0.25} emissive={"#35E7A6"} emissiveIntensity={0.18} />
    </mesh>
  );
}

function BodyRig({ snapshot, t }: { snapshot: FieldSnapshot; t: number }) {
  const named = namedJoints(snapshot.pose3d?.joints || {});
  const seedPairs = [
    named.head || [0.5, 0.12, 0.5],
    named.torso || [0.5, 0.42, 0.5],
  ] as number[][];
  const parts = templateBody(
    seedPairs,
    Number(snapshot.motion_energy || 0),
    t,
  );
  const links: Array<[string, string]> = [
    ["head", "neck"],
    ["neck", "torso"],
    ["torso", "lShoulder"],
    ["torso", "rShoulder"],
    ["lShoulder", "lElbow"],
    ["lElbow", "lHand"],
    ["rShoulder", "rElbow"],
    ["rElbow", "rHand"],
    ["torso", "hip"],
    ["hip", "lHip"],
    ["hip", "rHip"],
    ["lHip", "lKnee"],
    ["lKnee", "lFoot"],
    ["rHip", "rKnee"],
    ["rKnee", "rFoot"],
  ];
  return (
    <group>
      {links.map(([a, b]) => (
        <Bone key={`${a}-${b}`} a={parts[a]} b={parts[b]} />
      ))}
      <Joint p={parts.head} r={0.11} />
      {Object.entries(parts)
        .filter(([name]) => name !== "head")
        .map(([name, p]) => (
          <Joint key={name} p={p} r={name.includes("Hand") || name.includes("Foot") ? 0.04 : 0.05} />
        ))}
    </group>
  );
}

function livePoseData(snapshot: FieldSnapshot): {
  joints: Record<string, number[]>;
  bones: Array<[string, string]>;
} | null {
  const raw = snapshot.pose3d?.joints;
  if (Array.isArray(raw)) return null;
  if (snapshot.pose3d?.simulated !== false) return null;
  const joints = namedJoints(raw || {});
  if (!Object.keys(joints).length) return null;
  const bones = (snapshot.pose3d?.bones || []).filter(
    (pair): pair is [string, string] =>
      Array.isArray(pair) && pair.length === 2 && Boolean(joints[pair[0]]) && Boolean(joints[pair[1]]),
  );
  return { joints, bones };
}

function LivePoseRig({ data }: { data: { joints: Record<string, number[]>; bones: Array<[string, string]> } }) {
  return (
    <group>
      {data.bones.map(([a, b]) => (
        <Bone key={`live-${a}-${b}`} a={toVec(data.joints[a])} b={toVec(data.joints[b])} />
      ))}
      {Object.entries(data.joints).map(([name, coords]) => (
        <Joint key={`live-joint-${name}`} p={toVec(coords)} r={name === "head" ? 0.1 : 0.05} />
      ))}
    </group>
  );
}

function OccupancyCloud({
  row,
  live,
  scale,
}: {
  row: number[];
  live: boolean;
  scale: number;
}) {
  const mesh = useRef<InstancedMesh>(null);
  const count = Math.max(row.length * (live ? 10 : 6), 8);
  useFrame((state, dt) => {
    if (!mesh.current) return;
    for (let i = 0; i < count; i += 1) {
      const src = row[i % Math.max(row.length, 1)] || 0;
      const col = i % Math.max(row.length, 1);
      const x = (col / Math.max(row.length - 1, 1) - 0.5) * 2.4;
      const y = src * 1.6 - 0.2 + Math.sin(state.clock.elapsedTime * 1.6 + i) * 0.05;
      const z = (Math.floor(i / Math.max(row.length, 1)) - 3) * 0.12;
      dummy.position.set(x, y, z);
      const s = (0.03 + src * 0.08) * scale;
      dummy.scale.setScalar(s);
      dummy.updateMatrix();
      mesh.current.setMatrixAt(i, dummy.matrix);
    }
    mesh.current.instanceMatrix.needsUpdate = true;
    easing.damp3(mesh.current.rotation, [0, state.clock.elapsedTime * 0.08, 0], 0.4, dt);
  });
  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={live ? seed : moss} transparent opacity={0.72} />
    </instancedMesh>
  );
}

function SceneContents({
  snapshot,
  gui,
}: {
  snapshot: FieldSnapshot;
  gui: FieldGuiState;
}) {
  const group = useRef<Group>(null);
  const reduced = prefersReducedMotion();
  const t = snapshot.tick || 0;
  const row = snapshot.occupancy_row || snapshot.envelope || [];
  const live = Boolean(snapshot.live) || snapshot.show_skeleton === false;
  const livePose = livePoseData(snapshot);
  useFrame((_state, dt) => {
    if (!group.current || reduced || !gui.autoRotate) return;
    const yaw = (cameraObj.value.yaw as number) + t * 0.01;
    easing.dampE(group.current.rotation, [0, yaw, 0], 0.35, dt);
  });
  return (
    <>
      <color attach="background" args={["#050d0a"]} />
      <hemisphereLight args={["#8df6c9", "#07120e", 0.95]} />
      <directionalLight position={[3.2, 4.5, 2.4]} intensity={1.5} color={"#eafff4"} />
      <directionalLight position={[-2.4, 1.2, -2]} intensity={0.45} color={"#4CC4F5"} />
      <group ref={group}>
        {livePose ? (
          <LivePoseRig data={livePose} />
        ) : snapshot.show_skeleton !== false ? (
          <BodyRig snapshot={snapshot} t={t * 0.12} />
        ) : null}
        <OccupancyCloud row={row} live={live} scale={gui.occupancyScale} />
        <Text
          position={[0, 1.55, 0]}
          fontSize={0.14}
          color="#35E7A6"
          anchorX="center"
          anchorY="middle"
        >
          {livePose ? "LIVE · ON-DEVICE" : "SANDBOX"}
        </Text>
        <Html position={[0, -1.25, 0]} center>
          <p className="muted" style={{ margin: 0, fontSize: "0.75rem" }}>
            {livePose
              ? "Camera pose features only; raw frames never stored"
              : "Synthetic template, not a scan"}
          </p>
        </Html>
      </group>
      {gui.showGrid ? (
        <Grid
          args={[8, 8]}
          cellSize={0.25}
          cellThickness={0.6}
          sectionSize={1}
          sectionThickness={1.1}
          fadeDistance={8}
          cellColor="#1E6B4E"
          sectionColor="#35E7A6"
          position={[0, -1.05, 0]}
        />
      ) : null}
      <ContactShadows opacity={0.35} scale={8} blur={2.2} far={4} />
      {!reduced && gui.bloom ? (
        <EffectComposer disableNormalPass>
          <Bloom luminanceThreshold={0.45} intensity={0.85} mipmapBlur />
        </EffectComposer>
      ) : null}
      <OrbitControls enablePan={false} enableDamping={!reduced} />
    </>
  );
}

function preferCanvas(): boolean {
  if (typeof navigator === "undefined") return false;
  if (navigator.webdriver || /HeadlessChrome/i.test(navigator.userAgent || "")) return false;
  try {
    const probe = document.createElement("canvas");
    return Boolean(probe.getContext("webgl2") || probe.getContext("webgl"));
  } catch {
    return false;
  }
}

export function FieldScene({
  snapshot,
  gui = defaultGui,
}: {
  snapshot: FieldSnapshot | null;
  gui?: FieldGuiState;
}) {
  const reduced = prefersReducedMotion();
  const key = useMemo(() => String(snapshot?.tick ?? "empty"), [snapshot?.tick]);
  const canvasOk = preferCanvas();
  useEffect(() => {
    if (reduced) return;
    void cameraObj;
  }, [reduced, key]);
  if (!snapshot) {
    return (
      <div className="stage-3d" role="img" aria-label="Field stage waiting for a sandbox tick">
        <p className="stagetag" aria-hidden="true">
          Sandbox · synthetic template
        </p>
        <p className="muted" style={{ padding: "1rem" }}>
          3D stage idle. Watch sandbox field to light the body.
        </p>
      </div>
    );
  }
  const livePose = snapshot ? livePoseData(snapshot) : null;
  return (
    <div
      className="stage-3d"
      role="img"
      aria-label={
        livePose
          ? "Live on-device camera pose rendered as named joints and bones. Features only; raw frames were never stored or exported."
          : snapshot.show_skeleton === false
            ? "Occupancy cloud from sensor features. Skeleton hidden in this mode. Not a real person."
            : "Lit 3D sandbox body built from head and torso joints plus a template rig. Not a real body scan."
      }
    >
      <p className="stagetag" aria-hidden="true">
        {livePose ? "Live · on-device camera pose" : "Sandbox · synthetic template"}
      </p>
      {canvasOk ? (
        <Canvas
          camera={{ position: [1.6, 1.1, 2.4], fov: 42 }}
          dpr={[1, 1.75]}
          gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
          frameloop="always"
        >
          <SceneContents snapshot={snapshot} gui={gui} />
        </Canvas>
      ) : (
        <StagePoster snapshot={snapshot} />
      )}
    </div>
  );
}
