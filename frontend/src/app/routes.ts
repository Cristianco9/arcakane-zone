export const routes = {
  home: "/",
  products: "/productos",
  catalog: "/catalogo",
  productDetail: (productId: string) => `/productos/${encodeURIComponent(productId)}`,
} as const;

export const filterParams = {
  query: "q",
  category: "categoria",
  platform: "plataforma",
} as const;

export function buildProductsUrl(
  filters: {
    query?: string;
    category?: string;
    platform?: string;
  } = {},
): string {
  const params = new URLSearchParams();
  if (filters.query) params.set(filterParams.query, filters.query);
  if (filters.category) params.set(filterParams.category, filters.category);
  if (filters.platform) params.set(filterParams.platform, filters.platform);
  const search = params.toString();
  return search ? `${routes.products}?${search}` : routes.products;
}

export function buildCatalogUrl(category?: string): string {
  return category ? `${routes.catalog}?categoria=${encodeURIComponent(category)}` : routes.catalog;
}
