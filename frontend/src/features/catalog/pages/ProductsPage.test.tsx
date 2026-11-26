import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderConCatalogo } from "../../../test/renderConCatalogo";
import { ProductsPage } from "./ProductsPage";

describe("ProductsPage", () => {
  it("renders every product from the API and filters them by search term", async () => {
    const user = userEvent.setup();

    renderConCatalogo(<ProductsPage />, "/productos");

    expect(
      await screen.findByRole("heading", { level: 1, name: "Productos" }),
    ).toBeInTheDocument();
    expect(screen.getByText("8 resultados")).toBeInTheDocument();

    await user.type(screen.getByRole("searchbox", { name: /Buscar productos/i }), "neon");

    expect(await screen.findByText("1 resultado")).toBeInTheDocument();
    expect(screen.getByText("Neon Drift")).toBeInTheDocument();
    expect(screen.queryByText("Chrono Forge")).not.toBeInTheDocument();
  });

  it("shows an empty state when no product matches", async () => {
    const user = userEvent.setup();

    renderConCatalogo(<ProductsPage />, "/productos");

    await user.type(
      await screen.findByRole("searchbox", { name: /Buscar productos/i }),
      "titulo-que-no-existe",
    );

    expect(await screen.findByText("No encontramos productos")).toBeInTheDocument();
    expect(screen.getByText("0 resultados")).toBeInTheDocument();
  });
});
