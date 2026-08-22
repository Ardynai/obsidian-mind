export class ApiError extends Error {
  status: number;
  payload: Record<string, unknown>;

  constructor(message: string, status: number, payload: Record<string, unknown>) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export async function api<T = Record<string, unknown>>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = (await response.json().catch(() => ({}))) as Record<string, unknown>;
  if (!response.ok) {
    throw new ApiError(
      String(data.message || "Request failed"),
      response.status,
      data,
    );
  }
  return data as T;
}

export type Scope = {
  id: string;
  human_label: string;
  description: string;
  limits: string;
  granted: boolean;
  default?: string;
};

export type StatusPayload = {
  ok: boolean;
  all_scopes_off: boolean;
  adapter_config: string;
  informational_notice: string;
  scopes: Scope[];
  sensor_lanes: Array<{
    modality: string;
    notes: string;
    go_live?: string;
    live_granted?: boolean;
  }>;
  encryption_at_rest?: boolean;
  emergency_self_test?: {
    triggered: boolean;
    kind: string;
    language_scope?: string;
  };
  notes: string[];
};

export type LiveConsentPayload = {
  modalities: string[];
  grants: Record<
    string,
    { granted: boolean; subject_consent: boolean; default: string }
  >;
  store: string;
  hardware_validation: string;
  subject_consent_note: string;
};

export type SensorsPayload = {
  modalities: string[];
  lanes: Array<{
    modality: string;
    extra_package: string;
    extra_available: boolean;
    live_granted: boolean;
    go_live: string;
    notes: string;
  }>;
  audio_live_granted?: boolean;
  video_live_granted?: boolean;
  video3d_live_granted?: boolean;
  csi_live_granted?: boolean;
  pose_model?: Record<string, unknown>;
  hardware_validation?: string;
};

export type ConsentPayload = {
  scopes: Scope[];
  events: Array<{ timestamp: string; action: string; scope_id: string }>;
};

export type PoseJoints = Record<string, number[]> | number[][];

export type FieldSnapshot = {
  disclaimer: string;
  hardware_validation: string;
  tick: number;
  live?: boolean;
  simulated?: boolean;
  modality?: string;
  show_skeleton?: boolean;
  breathing_rate_per_min?: number;
  motion_energy?: number;
  presence?: boolean;
  cough_event_count?: number;
  speech_activity_ratio?: number;
  occupancy_row?: number[];
  envelope?: number[];
  pose3d: {
    origin?: string;
    simulated?: boolean;
    note?: string;
    bones?: string[][];
    joints: PoseJoints;
  };
};
