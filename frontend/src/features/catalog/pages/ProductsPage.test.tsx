import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ProductsPage } from "./ProductsPage";

describe("ProductsPage", () => {
  it("renders all mock products and filters them by search term", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/productos"]}>
        <ProductsPage />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "Productos" }),
    ).toBeInTheDocument();
    expect(screen.getByText("8 resultados")).toBeInTheDocument();

    await user.type(screen.getByRole("searchbox", { name: /Buscar productos/i }), "neon");

    expect(screen.getByText("1 resultado")).toBeInTheDocument();
    expect(screen.getByText("Neon Drift")).toBeInTheDocument();
    expect(screen.queryByText("Chrono Forge")).not.toBeInTheDocument();
  });

  it("shows an empty state when no product matches", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/productos"]}>
        <ProductsPage />
      </MemoryRouter>,
    );

    await user.type(
      screen.getByRole("searchbox", { name: /Buscar productos/i }),
      "titulo-que-no-existe",
    );

    expect(screen.getByText("No encontramos productos")).toBeInTheDocument();
    expect(screen.getByText("0 resultados")).toBeInTheDocument();
  });
});
