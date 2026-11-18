import { categories, platforms, products } from "./data/mockData";
import type { CatalogCategory, Product, ProductFilters, ProductOffer } from "./types";

export const ALL_FILTER = "todas";

function normalize(value: string): string {
  return value
    .toLocaleLowerCase("es")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

export function getProductById(productId: string): Product | undefined {
  return products.find((product) => product.id === productId);
}

export function getPublishedOffers(product: Product): ProductOffer[] {
  return product.offers.filter((offer) => offer.status === "publicado");
}

export function getStartingPrice(product: Product): number | null {
  const prices = getPublishedOffers(product).map((offer) => offer.price);
  return prices.length > 0 ? Math.min(...prices) : null;
}

export function isProductAvailable(product: Product): boolean {
  return getPublishedOffers(product).some((offer) => offer.stock > 0);
}

export function filterProducts(
  source: readonly Product[],
  filters: ProductFilters = {},
): Product[] {
  const query = normalize(filters.query?.trim() ?? "");
  const categoryId = filters.categoryId ?? ALL_FILTER;
  const platform = filters.platform ?? ALL_FILTER;

  return source.filter((product) => {
    const searchableText = normalize(
      [
        product.title,
        product.description,
        product.category.name,
        product.genre.name,
        product.developer,
        ...product.tags,
      ].join(" "),
    );

    const matchesQuery = query.length === 0 || searchableText.includes(query);
    const matchesCategory =
      categoryId === ALL_FILTER || product.category.id === categoryId;
    const matchesPlatform =
      platform === ALL_FILTER ||
      getPublishedOffers(product).some((offer) => offer.platform === platform);

    return matchesQuery && matchesCategory && matchesPlatform;
  });
}

export function groupProductsByCategory(
  source: readonly Product[],
): { category: CatalogCategory; products: Product[] }[] {
  return categories
    .map((category) => ({
      category,
      products: source.filter((product) => product.category.id === category.id),
    }))
    .filter((group) => group.products.length > 0);
}

export function getRelatedProducts(product: Product, limit = 3): Product[] {
  return products
    .filter((item) => item.id !== product.id && item.category.id === product.category.id)
    .slice(0, limit);
}

export function getAvailablePlatforms(source: readonly Product[] = products): string[] {
  const usedPlatforms = new Set(
    source.flatMap((product) =>
      getPublishedOffers(product).map((offer) => offer.platform),
    ),
  );
  return platforms.filter((platform) => usedPlatforms.has(platform));
}
