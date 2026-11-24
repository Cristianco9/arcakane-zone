import { useState, type FormEvent, type ReactNode } from "react";
import clsx from "clsx";
import { Link, useNavigate, useParams } from "react-router-dom";
import { confirmPasswordReset } from "../api/passwordReset";
import { authPaths } from "../paths";
import type { ResetStatus } from "../types";

const MIN_LENGTH = 8;

const focusRing =
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2d9bff]";

function fieldClass(hasError: boolean) {
  return clsx(
    "w-full rounded-md border bg-[#26262e] py-2.5 pl-3 pr-10 text-sm text-white",
    "focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[#2d9bff]",
    "disabled:opacity-60",
    hasError ? "border-[#ff6b6b]" : "border-[#34343d]",
  );
}

/** Centra la tarjeta horizontal y verticalmente dentro del contenido de la página. */
function CenteredCard({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-[60vh] w-full items-center justify-center px-4 py-10">
      <section className="w-full max-w-sm rounded-xl border border-[#34343d] bg-[#1e1e24] p-6 sm:p-7">
        {children}
      </section>
    </div>
  );
}

function EyeIcon({ crossed }: { crossed: boolean }) {
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
      {crossed && <path d="M3 3l18 18" />}
    </svg>
  );
}

interface PasswordFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
  errors: string[];
}

function PasswordField({ id, label, value, onChange, disabled, errors }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false);
  const errorId = `${id}-error`;
  const hasError = errors.length > 0;

  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-xs text-[#a3a3b2]">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={visible ? "text" : "password"}
          autoComplete="new-password"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          disabled={disabled}
          aria-invalid={hasError}
          aria-describedby={hasError ? errorId : undefined}
          className={fieldClass(hasError)}
        />
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          aria-label={visible ? `Ocultar ${label.toLowerCase()}` : `Mostrar ${label.toLowerCase()}`}
          aria-pressed={visible}
          className={clsx(
            "absolute inset-y-0 right-0 flex w-10 items-center justify-center rounded-md text-[#a3a3b2] hover:text-white",
            focusRing,
          )}
        >
          <EyeIcon crossed={visible} />
        </button>
      </div>
      {hasError && (
        <ul id={errorId} role="alert" className="mt-1 space-y-0.5 text-xs text-[#ff6b6b]">
          {errors.map((message) => (
            <li key={message}>{message}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function InvalidLink() {
  return (
    <CenteredCard>
      <h1 className="mb-3 text-xl font-bold text-white">Enlace no válido</h1>
      <p role="alert" className="mb-5 text-sm text-[#a3a3b2]">
        Este enlace ya se usó o venció. Solicita uno nuevo para cambiar tu contraseña.
      </p>
      <Link
        to={authPaths.forgotPassword}
        className={clsx(
          "block rounded-md bg-[#0073e6] py-2.5 text-center text-sm font-bold text-white hover:bg-[#1a84f0]",
          focusRing,
        )}
      >
        Solicitar nuevo enlace
      </Link>
    </CenteredCard>
  );
}

export function ResetPasswordPage() {
  const { uid, token } = useParams<{ uid: string; token: string }>();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [status, setStatus] = useState<ResetStatus>("idle");
  const [passwordErrors, setPasswordErrors] = useState<string[]>([]);
  const [confirmErrors, setConfirmErrors] = useState<string[]>([]);
  const [generalError, setGeneralError] = useState("");

  // Enlace sin uid/token (vacío) o rechazado por el backend (usado/vencido)
  if (!uid || !token || status === "invalid-link") return <InvalidLink />;

  const loading = status === "loading";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!uid || !token) return;

    const nextPasswordErrors: string[] = [];
    if (password.length === 0) nextPasswordErrors.push("Ingresa una contraseña.");
    else if (password.length < MIN_LENGTH)
      nextPasswordErrors.push(`La contraseña debe tener al menos ${MIN_LENGTH} caracteres.`);

    const nextConfirmErrors: string[] = [];
    if (confirm.length === 0) nextConfirmErrors.push("Confirma tu contraseña.");
    else if (password !== confirm) nextConfirmErrors.push("Las contraseñas no coinciden.");

    setGeneralError("");
    setPasswordErrors(nextPasswordErrors);
    setConfirmErrors(nextConfirmErrors);
    if (nextPasswordErrors.length > 0 || nextConfirmErrors.length > 0) return;

    setStatus("loading");
    const result = await confirmPasswordReset({ uid, token, newPassword: password });

    if (result.ok) {
      navigate(authPaths.login, {
        replace: true,
        state: { notice: "Contraseña actualizada. Ya puedes iniciar sesión." },
      });
      return;
    }

    if (result.kind === "invalid-link") {
      setStatus("invalid-link");
      return;
    }

    if (result.kind === "validation") {
      setStatus("idle");
      setPasswordErrors(result.errors);
      return;
    }

    setStatus("network-error");
    setGeneralError(result.message);
  }

  return (
    <CenteredCard>
      <h1 className="mb-5 text-xl font-bold text-white">Nueva contraseña</h1>
      <p className="mb-4 text-sm text-[#a3a3b2]">Elige una contraseña segura</p>

      <form onSubmit={handleSubmit} noValidate aria-busy={loading} className="space-y-4">
        <PasswordField
          id="new-password"
          label="Nueva contraseña"
          value={password}
          onChange={setPassword}
          disabled={loading}
          errors={passwordErrors}
        />
        <PasswordField
          id="confirm-password"
          label="Confirmar contraseña"
          value={confirm}
          onChange={setConfirm}
          disabled={loading}
          errors={confirmErrors}
        />

        {generalError && (
          <p role="alert" className="text-xs text-[#ff6b6b]">
            {generalError}
          </p>
        )}

        <p role="status" className="sr-only">
          {loading ? "Guardando contraseña" : ""}
        </p>

        <button
          type="submit"
          disabled={loading}
          className={clsx(
            "w-full rounded-md bg-[#0073e6] py-2.5 text-sm font-bold text-white hover:bg-[#1a84f0] disabled:opacity-60",
            focusRing,
          )}
        >
          {loading ? "Guardando…" : "Guardar contraseña"}
        </button>
      </form>
    </CenteredCard>
  );
}
