import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { products } from "../data/mockData";
import { ProductCard } from "./ProductCard";

describe("ProductCard", () => {
  it("links to the product detail and shows its cover and price", () => {
    const product = products[0];
    expect(product).toBeDefined();
    if (!product) return;

    render(
      <MemoryRouter>
        <ProductCard product={product} />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("link", { name: "Ver detalle de Neon Drift" }),
    ).toHaveAttribute("href", "/productos/1");
    expect(screen.getByRole("img", { name: "Portada de Neon Drift" })).toBeInTheDocument();
    expect(screen.getByText(/89\.000/)).toBeInTheDocument();
    expect(screen.getByText(/2 ediciones/)).toBeInTheDocument();
  });
});
