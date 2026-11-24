// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { confirmPasswordReset } from "../features/auth/api/passwordReset";
import { ResetPasswordPage } from "../features/auth/pages/ResetPasswordPage";
import { authPaths } from "../features/auth/paths";

vi.mock("../features/auth/api/passwordReset", () => ({
  confirmPasswordReset: vi.fn(),
}));

const mockedConfirm = vi.mocked(confirmPasswordReset);

function LoginStub() {
  const state: unknown = useLocation().state;
  const notice =
    typeof state === "object" && state !== null && "notice" in state ? String(state.notice) : "";
  return <p>Iniciar sesión: {notice}</p>;
}

function renderPage(path = "/restablecer/abc/tok123") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path={authPaths.resetPassword} element={<ResetPasswordPage />} />
        <Route path={authPaths.login} element={<LoginStub />} />
        <Route path={authPaths.forgotPassword} element={<p>Recuperar</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

async function fill(password: string, confirm: string) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Nueva contraseña"), password);
  await user.type(screen.getByLabelText("Confirmar contraseña"), confirm);
  await user.click(screen.getByRole("button", { name: "Guardar contraseña" }));
}

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ResetPasswordPage", () => {
  it("muestra los campos y el botón", () => {
    renderPage();
    expect(screen.getByRole("heading", { name: "Nueva contraseña" })).toBeInTheDocument();
    expect(screen.getByLabelText("Nueva contraseña")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirmar contraseña")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Guardar contraseña" })).toBeInTheDocument();
  });

  it("avisa si las contraseñas no coinciden y no llama a la API", async () => {
    renderPage();
    await fill("clave-segura-1", "clave-segura-2");
    expect(await screen.findByText("Las contraseñas no coinciden.")).toBeInTheDocument();
    expect(mockedConfirm).not.toHaveBeenCalled();
  });

  it("avisa si la contraseña es muy corta", async () => {
    renderPage();
    await fill("corta", "corta");
    expect(await screen.findByText(/al menos 8 caracteres/)).toBeInTheDocument();
    expect(mockedConfirm).not.toHaveBeenCalled();
  });

  it("llama a la API con uid y token y redirige a iniciar sesión con aviso", async () => {
    mockedConfirm.mockResolvedValue({ ok: true });
    renderPage();
    await fill("clave-segura-1", "clave-segura-1");
    expect(mockedConfirm).toHaveBeenCalledWith({
      uid: "abc",
      token: "tok123",
      newPassword: "clave-segura-1",
    });
    expect(await screen.findByText(/Contraseña actualizada/)).toBeInTheDocument();
  });

  it("muestra los errores de reglas que devuelve el backend", async () => {
    mockedConfirm.mockResolvedValue({
      ok: false,
      kind: "validation",
      errors: ["La contraseña es demasiado común."],
    });
    renderPage();
    await fill("12345678", "12345678");
    expect(await screen.findByText("La contraseña es demasiado común.")).toBeInTheDocument();
  });

  it("muestra enlace inválido con acceso para pedir uno nuevo", async () => {
    mockedConfirm.mockResolvedValue({ ok: false, kind: "invalid-link" });
    renderPage();
    await fill("clave-segura-1", "clave-segura-1");
    expect(await screen.findByText(/ya se usó o venció/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Solicitar nuevo enlace" })).toBeInTheDocument();
  });

  it("muestra mensaje general si falla la red", async () => {
    mockedConfirm.mockResolvedValue({ ok: false, kind: "network", message: "Sin conexión." });
    renderPage();
    await fill("clave-segura-1", "clave-segura-1");
    expect(await screen.findByText("Sin conexión.")).toBeInTheDocument();
  });
});
