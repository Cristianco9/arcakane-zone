import type {
  ApiErrorEnvelope,
  ConfirmPasswordResetInput,
  ConfirmPasswordResetResult,
} from "../types";

// Mientras BE-06 no esté disponible se usa el mock.
// Para usar el backend real: VITE_USE_MOCK_AUTH=false en el .env
const USE_MOCK = import.meta.env.VITE_USE_MOCK_AUTH !== "false";
const API_URL: string = import.meta.env.VITE_API_URL ?? "/api";

const NETWORK_MESSAGE = "No pudimos conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.";
const WEAK_PASSWORDS = ["12345678", "password", "contraseña"];

function normalizeErrors(error: ApiErrorEnvelope["error"] | undefined): string[] {
  if (!error) return ["No se pudo guardar la contraseña."];
  if (typeof error === "string") return [error];
  if (Array.isArray(error)) return error;
  return Object.values(error).flat();
}

function isEnvelope(value: unknown): value is ApiErrorEnvelope {
  return typeof value === "object" && value !== null && "success" in value && "error" in value;
}

async function confirmMock(input: ConfirmPasswordResetInput): Promise<ConfirmPasswordResetResult> {
  await new Promise((resolve) => setTimeout(resolve, 400));
  // Tokens de prueba: "usado" o "expirado" => enlace inválido; "red" => error de red
  if (input.token === "usado" || input.token === "expirado") return { ok: false, kind: "invalid-link" };
  if (input.token === "red") return { ok: false, kind: "network", message: NETWORK_MESSAGE };
  if (WEAK_PASSWORDS.includes(input.newPassword.toLowerCase())) {
    return { ok: false, kind: "validation", errors: ["La contraseña es demasiado común."] };
  }
  return { ok: true };
}

async function confirmReal(input: ConfirmPasswordResetInput): Promise<ConfirmPasswordResetResult> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/auth/password-reset/confirm/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Ajusta los nombres de campo a lo que defina AZ-S2-BE-06
      body: JSON.stringify({ uid: input.uid, token: input.token, new_password: input.newPassword }),
    });
  } catch {
    return { ok: false, kind: "network", message: NETWORK_MESSAGE };
  }

  if (response.ok) return { ok: true };
  if (response.status === 404 || response.status === 410) return { ok: false, kind: "invalid-link" };

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    return { ok: false, kind: "network", message: NETWORK_MESSAGE };
  }

  const errors = isEnvelope(body) ? normalizeErrors(body.error) : normalizeErrors(undefined);
  // Ajusta esta regla cuando se conozca el código exacto que devuelve el backend
  if (errors.some((message) => /token|enlace|expir|inválid/i.test(message))) {
    return { ok: false, kind: "invalid-link" };
  }
  return { ok: false, kind: "validation", errors };
}

export function confirmPasswordReset(
  input: ConfirmPasswordResetInput,
): Promise<ConfirmPasswordResetResult> {
  return USE_MOCK ? confirmMock(input) : confirmReal(input);
}
