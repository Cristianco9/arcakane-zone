import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { renderConCatalogo } from "../../../test/renderConCatalogo";
import { ProductDetailPage } from "./ProductDetailPage";

function renderDetail(productId: string) {
  return renderConCatalogo(
    <Routes>
      <Route path="/productos/:productId" element={<ProductDetailPage />} />
    </Routes>,
    `/productos/${productId}`,
  );
}

describe("ProductDetailPage", () => {
  it("renders the information and offers of a product from the API", async () => {
    renderDetail("1");

    expect(
      await screen.findByRole("heading", { level: 1, name: "Neon Drift" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Ediciones disponibles")).toBeInTheDocument();
    expect(screen.getByText(/SKU AZ-ND-PC/)).toBeInTheDocument();
    expect(screen.getByText("Ficha técnica")).toBeInTheDocument();
    expect(
      screen.getByRole("navigation", { name: "Ruta de navegación" }),
    ).toBeInTheDocument();
  });

  it("renders the not found view for an unknown product", async () => {
    renderDetail("unknown");

    expect(
      await screen.findByRole("heading", { level: 1, name: "No encontramos esa vista" }),
    ).toBeInTheDocument();
  });
});
