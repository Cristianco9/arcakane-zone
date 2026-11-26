import type { SyntheticEvent } from "react";
import catalogCover from "../../assets/covers/catalog-placeholder.svg";

export const COVER_FALLBACK = catalogCover;

/** Sustituye una portada remota que no carga por la portada local. */
export function alFallarPortada(
  evento: SyntheticEvent<HTMLImageElement>,
): void {
  const imagen = evento.currentTarget;
  if (imagen.dataset.fallbackAplicado === "true") return;
  imagen.dataset.fallbackAplicado = "true";
  imagen.src = COVER_FALLBACK;
}
