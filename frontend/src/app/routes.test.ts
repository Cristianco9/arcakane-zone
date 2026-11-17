import { describe, expect, it } from "vitest";
import { buildCatalogUrl, buildProductsUrl, routes } from "./routes";

describe("route builders", () => {
  it("builds the product detail route", () => {
    expect(routes.productDetail("1")).toBe("/productos/1");
  });

  it("builds the products route without filters", () => {
    expect(buildProductsUrl({})).toBe("/productos");
  });

  it("builds the products route with filters", () => {
    expect(
      buildProductsUrl({ query: "neon", category: "1", platform: "PC" }),
    ).toBe("/productos?q=neon&categoria=1&plataforma=PC");
  });

  it("builds the catalog route with a category", () => {
    expect(buildCatalogUrl("2")).toBe("/catalogo?categoria=2");
  });
});
