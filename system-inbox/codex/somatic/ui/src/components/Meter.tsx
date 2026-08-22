import type { Scope } from "../api";
import { CapabilityRing } from "../viz";

export function Meter({ scopes }: { scopes: Scope[] }) {
  return <CapabilityRing scopes={scopes} />;
}
