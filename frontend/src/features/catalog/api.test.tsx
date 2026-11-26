import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
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
});
