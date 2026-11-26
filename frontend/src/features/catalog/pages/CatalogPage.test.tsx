import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { renderConCatalogo } from "../../../test/renderConCatalogo";
import { CatalogPage } from "./CatalogPage";

describe("CatalogPage", () => {
  it("agrupa los videojuegos de la API por categoría", async () => {
    renderConCatalogo(<CatalogPage />, "/catalogo");

    const filtros = await screen.findByRole("group", {
      name: "Filtrar por categoría",
    });
    const botones = within(filtros).getAllByRole("button");

    expect(botones[0]).toHaveTextContent("Todas8");
    expect(botones[1]).toHaveTextContent("Acción2");
    expect(botones[2]).toHaveTextContent("Aventura2");
  });
});
