import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { paginado, videojuegosApi } from "../../test/handlers";
import { server } from "../../test/server";
import { useCatalogCategories, useCatalogProducts } from "./api";

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("catalog API", () => {
  it("carga y transforma las respuestas paginadas del catálogo", async () => {
    const { result } = renderHook(
      () => ({
        categorias: useCatalogCategories(),
        productos: useCatalogProducts(),
      }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.productos.isSuccess).toBe(true));

    expect(result.current.categorias.data).toHaveLength(6);
    expect(result.current.productos.data).toHaveLength(8);
    expect(result.current.productos.data?.[0]?.offers[0]?.sku).toBe("AZ-ND-PC");
    expect(result.current.productos.data?.[0]?.developer).toBeTruthy();
  });

  it("rechaza una respuesta que no cumple el contrato", async () => {
    server.use(
      http.get("/api/v1/catalogo/categorias/", () =>
        HttpResponse.json({ success: true, data: [{ id: "no-numero" }] }),
      ),
    );

    const { result } = renderHook(() => useCatalogCategories(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
  });

  it("carga todos los juegos de todas las páginas y usa imagen_url", async () => {
    const muchos = Array.from({ length: 120 }, (_, indice) => ({
      ...videojuegosApi[indice % videojuegosApi.length],
      id: indice + 1,
      titulo: `Videojuego ${indice + 1}`,
      imagen_url: `https://ejemplo.test/portada-${indice + 1}.png`,
      portada: "https://ejemplo.test/portada-antigua.png",
    }));
    server.use(
      http.get("/api/v1/catalogo/videojuegos/", ({ request }) =>
        HttpResponse.json(paginado(muchos, request)),
      ),
    );

    const { result } = renderHook(() => useCatalogProducts(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toHaveLength(120);
    expect(result.current.data?.[0]?.cover).toBe(
      "https://ejemplo.test/portada-1.png",
    );
    expect(result.current.data?.[119]?.cover).toBe(
      "https://ejemplo.test/portada-120.png",
    );
  });

  it("acepta un catálogo vacío con pagination vacía", async () => {
    server.use(
      http.get("/api/v1/catalogo/videojuegos/", () =>
        HttpResponse.json({ success: true, data: [], pagination: {} }),
      ),
    );

    const { result } = renderHook(() => useCatalogProducts(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([]);
  });
});
