import { describe, expect, it } from "vitest";
import { confirmPasswordReset } from "../features/auth/api/passwordReset";

describe("mock de confirmPasswordReset", () => {
  it("un token usado una vez no se puede reutilizar", async () => {
    const input = { uid: "u1", token: "token-unico", newPassword: "clave-segura-1" };
    expect(await confirmPasswordReset(input)).toEqual({ ok: true });
    expect(await confirmPasswordReset(input)).toEqual({ ok: false, kind: "invalid-link" });
  });

  it("rechaza contraseñas comunes con un error de validación", async () => {
    const result = await confirmPasswordReset({ uid: "u2", token: "otro", newPassword: "12345678" });
    expect(result).toMatchObject({ ok: false, kind: "validation" });
  });

  it("simula un error de red con el token de prueba", async () => {
    const result = await confirmPasswordReset({ uid: "u3", token: "red", newPassword: "clave-segura-1" });
    expect(result).toMatchObject({ ok: false, kind: "network" });
  });
});
