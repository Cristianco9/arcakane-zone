import { describe, expect, it } from "vitest";
import {
  ALL_FILTER,
  filterProducts,
  getProductById,
  getPublishedOffers,
  getRelatedProducts,
  getStartingPrice,
  groupProductsByCategory,
} from "./catalog";
import { products } from "./data/mockData";

describe("catalog selectors", () => {
  it("filters products by title without taking accents into account", () => {
    const results = filterProducts(products, { query: "aurora" });
    expect(results).toHaveLength(1);
    expect(results[0]?.title).toBe("Guardians of Aurora");
  });

  it("filters products by category and platform", () => {
    const results = filterProducts(products, {
      categoryId: "1",
      platform: "PC",
    });
    expect(results.map((product) => product.title)).toEqual([
      "Neon Drift",
      "Terminal Velocity",
    ]);
  });

  it("returns every product when filters use the sentinel value", () => {
    expect(filterProducts(products, { categoryId: ALL_FILTER })).toHaveLength(
      products.length,
    );
  });

  it("groups products by category", () => {
    const groups = groupProductsByCategory(products);
    expect(groups).toHaveLength(6);
    expect(groups[0]?.category.name).toBe("Acción");
    expect(groups[0]?.products).toHaveLength(2);
  });

  it("calculates the starting price from published offers", () => {
    const product = getProductById("1");
    expect(product).toBeDefined();
    if (!product) return;
    expect(getPublishedOffers(product)).toHaveLength(2);
    expect(getStartingPrice(product)).toBe(89000);
  });

  it("returns related products from the same category", () => {
    const product = getProductById("1");
    expect(product).toBeDefined();
    if (!product) return;
    expect(getRelatedProducts(product).map((item) => item.id)).toEqual(["6"]);
  });

  it("returns undefined for an unknown product", () => {
    expect(getProductById("unknown")).toBeUndefined();
  });
});
