export type ResetStatus = "idle" | "loading" | "invalid-link" | "network-error";

export interface ConfirmPasswordResetInput {
  uid: string;
  token: string;
  newPassword: string;
}

/** Sobre de error del backend: { success: false, error } */
export interface ApiErrorEnvelope {
  success: false;
  error: string | string[] | Record<string, string[]>;
}

export type ConfirmPasswordResetResult =
  | { ok: true }
  | { ok: false; kind: "invalid-link" }
  | { ok: false; kind: "validation"; errors: string[] }
  | { ok: false; kind: "network"; message: string };
