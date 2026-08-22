import { Canvas } from "@react-three/fiber";
import { ContactShadows, OrbitControls, Text } from "@react-three/drei";
import { Bloom, EffectComposer } from "@react-three/postprocessing";
import { prefersReducedMotion } from "../motion";

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

function Figure({ persona }: { persona: string }) {
  const moss = persona === "scientist" ? "#AE97F7" : "#35E7A6";
  return (
    <group>
      <mesh position={[0, 1.15, 0]}>
        <sphereGeometry args={[0.22, 24, 24]} />
        <meshStandardMaterial color={moss} roughness={0.35} />
      </mesh>
      <mesh position={[0, 0.55, 0]}>
        <capsuleGeometry args={[0.22, 0.55, 8, 16]} />
        <meshStandardMaterial color={moss} roughness={0.4} />
      </mesh>
      <mesh position={[-0.32, 0.62, 0]} rotation={[0, 0, 0.35]}>
        <capsuleGeometry args={[0.07, 0.42, 6, 12]} />
        <meshStandardMaterial color={"#12A574"} emissive={"#35E7A6"} emissiveIntensity={0.2} />
      </mesh>
      <mesh position={[0.32, 0.62, 0]} rotation={[0, 0, -0.35]}>
        <capsuleGeometry args={[0.07, 0.42, 6, 12]} />
        <meshStandardMaterial color={"#12A574"} emissive={"#35E7A6"} emissiveIntensity={0.2} />
      </mesh>
      <Text position={[0, 1.55, 0]} fontSize={0.12} color="#35E7A6" anchorX="center">
        RENDER ONLY
      </Text>
    </group>
  );
}

export function AvatarScene({ persona, speech }: { persona: string; speech: string }) {
  const reduced = prefersReducedMotion();
  const canvasOk = preferCanvas();
  return (
    <div
      className="stage-3d"
      role="img"
      aria-label={`Presence avatar, ${persona} persona, render-only restatement. Audio stays off.`}
    >
      {canvasOk ? (
        <Canvas
          camera={{ position: [1.2, 1.1, 2.1], fov: 40 }}
          dpr={[1, 1.75]}
          frameloop="always"
          gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
        >
          <color attach="background" args={["#050d0a"]} />
          <hemisphereLight args={["#8df6c9", "#07120e", 0.95]} />
          <directionalLight position={[2.4, 3.2, 2]} intensity={1.35} color={"#eafff4"} />
          <Figure persona={persona} />
          <ContactShadows opacity={0.4} scale={6} blur={2.4} far={3} />
          {!reduced ? (
            <EffectComposer disableNormalPass>
              <Bloom luminanceThreshold={0.5} intensity={0.7} mipmapBlur />
            </EffectComposer>
          ) : null}
          <OrbitControls enablePan={false} />
        </Canvas>
      ) : (
        <svg className="stage-poster" viewBox="0 0 320 280" aria-hidden="true">
          <rect width="320" height="280" fill="#050d0a" />
          <ellipse cx="160" cy="232" rx="70" ry="14" fill="#35E7A6" opacity="0.18" />
          <circle cx="160" cy="88" r="22" fill={persona === "scientist" ? "#AE97F7" : "#35E7A6"} />
          <rect x="138" y="112" width="44" height="78" rx="18" fill="#12A574" />
          <text
            x="160"
            y="28"
            textAnchor="middle"
            fill="#35E7A6"
            fontSize="11"
            fontFamily="IBM Plex Mono, monospace"
          >
            RENDER ONLY · {persona.toUpperCase()}
          </text>
        </svg>
      )}
      <p className="sr-only">{speech}</p>
    </div>
  );
}
