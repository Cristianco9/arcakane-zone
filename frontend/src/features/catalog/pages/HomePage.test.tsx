import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { renderConCatalogo } from "../../../test/renderConCatalogo";
import { HomePage } from "./HomePage";

describe("HomePage", () => {
  it("muestra las cifras y el destacado que devuelve la API", async () => {
    renderConCatalogo(<HomePage />);

    expect(await screen.findByText("8")).toBeInTheDocument();
    expect(screen.getAllByText("videojuegos").length).toBeGreaterThan(0);
    expect(screen.getByText("6")).toBeInTheDocument();
    expect(screen.getAllByText("categorías").length).toBeGreaterThan(0);
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getAllByText("plataformas").length).toBeGreaterThan(0);
    expect(
      screen.getAllByRole("link", { name: "Ver detalle de Neon Drift" }).length,
    ).toBeGreaterThan(0);
  });
});
