import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ProductDetailPage } from "./ProductDetailPage";

function renderDetail(productId: string) {
  return render(
    <MemoryRouter initialEntries={[`/productos/${productId}`]}>
      <Routes>
        <Route path="/productos/:productId" element={<ProductDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProductDetailPage", () => {
  it("renders the information and offers of a product", () => {
    renderDetail("1");

    expect(
      screen.getByRole("heading", { level: 1, name: "Neon Drift" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Ediciones disponibles")).toBeInTheDocument();
    expect(screen.getByText(/SKU AZ-ND-PC/)).toBeInTheDocument();
    expect(screen.getByText("Ficha técnica")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Ruta de navegación" })).toBeInTheDocument();
  });

  it("renders the not found view for an unknown product", () => {
    renderDetail("unknown");

    expect(
      screen.getByRole("heading", { level: 1, name: "No encontramos esa vista" }),
    ).toBeInTheDocument();
  });
});
